from django.contrib import admin
from .models import Category, Item


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'barcode', 'name', 'category', 'wholesale_price', 'retail_price', 'margin_display', 'updated_at']
    list_filter = ['category']
    search_fields = ['code', 'barcode', 'name']
    ordering = ['category', 'name']
    list_select_related = ['category']

    @admin.display(description='Margin')
    def margin_display(self, obj):
        pct = obj.margin_percent
        return f'{pct}%' if pct is not None else '—'
