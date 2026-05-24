from django.contrib import admin
from .models import Address, DiscountCode


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "title", "city", "state", "postal_code", "is_default"]
    list_filter = ["city", "state", "is_default"]
    search_fields = ["user__email", "title", "city", "state", "full_address", "postal_code"]
    autocomplete_fields = ["user"]


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "user", "percentage", "is_active", "is_used", "used_by", "expires_at", "created_at"]
    list_filter = ["is_active", "is_used", "percentage", "created_at"]
    search_fields = ["code", "user__email", "used_by__email"]
    autocomplete_fields = ["user", "used_by"]
