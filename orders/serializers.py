from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from orders.models import Cart, Cartitems, Order, OrderItem
from products.models import Product
from products.serializers import SimpleProductSerializer
from userprofile.models import Address, DiscountCode
from userprofile.serializers import AddressSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False)
    sub_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    inventory = serializers.IntegerField(source="product.inventory", read_only=True)

    class Meta:
        model = Cartitems
        fields = ["id", "cart", "product", "quantity", "sub_total", "inventory"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()

    class Meta:
        model = Cartitems
        fields = ["id", "product_id", "quantity"]

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("محصول مورد نظر پیدا نشد.")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("تعداد باید حداقل ۱ باشد.")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        product = Product.objects.get(pk=product_id)
        cartitem, _ = Cartitems.objects.get_or_create(cart_id=cart_id, product_id=product_id, defaults={"quantity": 0})
        if cartitem.quantity + quantity > product.inventory:
            raise serializers.ValidationError("موجودی محصول کافی نیست.")
        cartitem.quantity += quantity
        cartitem.save()
        self.instance = cartitem
        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartitems
        fields = ["quantity"]

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("تعداد معتبر نیست.")
        if self.instance and value > self.instance.product.inventory:
            raise serializers.ValidationError("موجودی محصول کافی نیست.")
        return value

    def update(self, instance, validated_data):
        if validated_data["quantity"] < 1:
            instance.delete()
            return None
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "owner", "items", "grand_total"]
        extra_kwargs = {"owner": {"read_only": True}}

    def get_grand_total(self, cart):
        return sum((item.sub_total for item in cart.items.select_related("product")), Decimal("0"))


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    discount_code_value = serializers.CharField(source="discount_code.code", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "placed_at", "pending_status", "owner", "address", "discount_code_value",
            "total_amount", "discount_amount", "final_amount", "customer_first_name",
            "customer_last_name", "customer_email", "customer_phone", "address_snapshot", "items",
        ]
        extra_kwargs = {"owner": {"read_only": True}}


class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    address_id = serializers.IntegerField(required=True, allow_null=False)
    discount_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = self.context["request"].user
        profile_fields = [user.first_name, user.last_name, user.email, user.phone]
        if not all(str(field).strip() for field in profile_fields):
            raise serializers.ValidationError("برای پرداخت ابتدا پروفایل را کامل کنید.")
        try:
            cart = Cart.objects.get(pk=attrs["cart_id"], owner=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("سبد خرید معتبر نیست.")
        cartitems = list(cart.items.select_related("product"))
        if not cartitems:
            raise serializers.ValidationError("سبد خرید خالی است.")
        address_id = attrs.get("address_id")
        if not address_id:
            raise serializers.ValidationError("برای پرداخت باید یک آدرس کامل انتخاب کنید.")
        try:
            address = Address.objects.get(pk=address_id, user=user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("آدرس انتخابی معتبر نیست.")
        address_fields = [address.title, address.state, address.city, address.full_address, address.postal_code]
        if not all(str(field).strip() for field in address_fields) or len(address.postal_code) != 10:
            raise serializers.ValidationError("برای پرداخت باید یک آدرس کامل ثبت و انتخاب کنید.")
        for item in cartitems:
            if item.quantity > item.product.inventory:
                raise serializers.ValidationError(f"موجودی {item.product.name} کافی نیست.")
        discount = None
        code = attrs.get("discount_code", "").strip()
        if code:
            try:
                discount = DiscountCode.objects.get(code__iexact=code)
            except DiscountCode.DoesNotExist:
                raise serializers.ValidationError("کد تخفیف نامعتبر است.")
            if not discount.can_be_used_by(user):
                raise serializers.ValidationError("کد تخفیف قابل استفاده نیست.")
        attrs["cart"] = cart
        attrs["cartitems"] = cartitems
        attrs["address"] = address
        attrs["discount"] = discount
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        cart = self.validated_data["cart"]
        cartitems = self.validated_data["cartitems"]
        address = self.validated_data["address"]
        discount = self.validated_data.get("discount")
        with transaction.atomic():
            total = sum((item.product.price * item.quantity for item in cartitems), Decimal("0"))
            discount_amount = Decimal("0")
            if discount:
                discount_amount = (total * Decimal(discount.percentage) / Decimal(100)).quantize(Decimal("0.01"))
                discount.is_used = True
                discount.used_by = user
                from django.utils import timezone
                discount.used_at = timezone.now()
                discount.save(update_fields=["is_used", "used_by", "used_at"])
            final_amount = total - discount_amount
            order = Order.objects.create(
                owner=user,
                address=address,
                discount_code=discount,
                pending_status=Order.PAYMENT_STATUS_COMPLETE,
                total_amount=total,
                discount_amount=discount_amount,
                final_amount=final_amount,
                customer_first_name=user.first_name,
                customer_last_name=user.last_name,
                customer_email=user.email,
                customer_phone=user.phone,
                address_snapshot=f"{address.title} - {address.state}، {address.city}، {address.full_address} - {address.postal_code}",
            )
            order_items = []
            for item in cartitems:
                unit_price = item.product.price
                line_total = unit_price * item.quantity
                order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity, unit_price=unit_price, line_total=line_total))
                item.product.inventory -= item.quantity
                item.product.save(update_fields=["inventory"])
            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["pending_status"]
