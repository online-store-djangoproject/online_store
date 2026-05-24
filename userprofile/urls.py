from django.urls import path
from . import views

urlpatterns = [
    path('addresses/', views.AddressListCreateView.as_view(), name="address_list"),
    path('addresses/<int:pk>/', views.AddressUpdateDeleteView.as_view(), name="address_detail"),
    path("discounts/request/", views.RequestDiscountCodeAPIView.as_view(), name="request_discount_code"),
    path("discounts/validate/", views.ValidateDiscountCodeAPIView.as_view(), name="validate_discount_code"),


]
