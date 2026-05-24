from django.contrib import admin
from .models import Cart, Cartitems, Order, OrderItem


class CartitemsInline(admin.TabularInline):
    model = Cartitems
    extra = 0
    autocomplete_fields = ["product"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "owner", "created", "updated_at"]
    search_fields = ["owner__email", "id"]
    inlines = [CartitemsInline]


@admin.register(Cartitems)
class CartitemsAdmin(admin.ModelAdmin):
    list_display = ["id", "cart", "product", "quantity"]
    list_filter = ["product"]
    search_fields = ["cart__owner__email", "product__name"]
    autocomplete_fields = ["cart", "product"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "unit_price", "line_total"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "owner", "pending_status", "total_amount", "discount_amount", "final_amount", "placed_at"]
    list_filter = ["pending_status", "placed_at", "discount_code"]
    search_fields = ["id", "owner__email", "customer_phone", "address_snapshot"]
    readonly_fields = ["placed_at", "total_amount", "discount_amount", "final_amount", "address_snapshot"]
    autocomplete_fields = ["owner", "address", "discount_code"]
    inlines = [OrderItemInline]
    fieldsets = (
        ("اطلاعات سفارش", {"fields": ("owner", "pending_status", "placed_at", "address", "discount_code")}),
        ("مبلغ", {"fields": ("total_amount", "discount_amount", "final_amount")}),
        ("اطلاعات مشتری", {"fields": ("customer_first_name", "customer_last_name", "customer_email", "customer_phone", "address_snapshot")}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "unit_price", "line_total"]
    search_fields = ["order__id", "product__name"]
    list_filter = ["product"]
    autocomplete_fields = ["order", "product"]
