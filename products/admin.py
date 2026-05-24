from django.contrib import admin
from .models import Category, Product, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "inventory", "is_available", "category", "discount", "top_deal", "flash_sales"]
    list_filter = ["category", "is_available", "discount", "top_deal", "flash_sales"]
    list_editable = ["price", "inventory", "is_available"]
    search_fields = ["name", "description", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["category"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["category_id", "title", "slug"]
    search_fields = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "date_created", "name"]
    search_fields = ["product__name", "name", "description"]
