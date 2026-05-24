from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from orders.models import Cart, Cartitems, Order
from orders.serializers import (
    CartSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CartItemSerializer,
    CheckoutSerializer, OrderSerializer, UpdateOrderSerializer,
)


class CartViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Cart.objects.select_related("owner").prefetch_related("items__product")
        return Cart.objects.filter(owner=user).prefetch_related("items__product")

    def perform_create(self, serializer):
        Cart.objects.get_or_create(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        return Response(CartSerializer(cart).data)


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        return Cart.objects.get(pk=self.kwargs["cart_pk"], owner=self.request.user)

    def get_queryset(self):
        cart_pk = self.kwargs.get("cart_pk")
        if not cart_pk:
            return Cartitems.objects.none()
        return Cartitems.objects.filter(cart_id=cart_pk, cart__owner=self.request.user).select_related("product")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        self.get_cart()
        return {"cart_id": self.kwargs["cart_pk"]}


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "post", "delete", "options", "head"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CheckoutSerializer
        if self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.select_related("owner", "address", "discount_code").prefetch_related("items__product")
        if user.is_staff:
            return queryset
        return queryset.filter(owner=user)
