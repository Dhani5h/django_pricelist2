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
    fields = ['code', 'name', 'category', 'wholesale_price', 'retail_price', 'barcode']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Barcode and retail price are both optional in this shop's workflow —
        # not every item has a barcode label or a set retail price yet.
        form.base_fields['barcode'].required = False
        form.base_fields['retail_price'].required = False
        return form

    @admin.display(description='Margin')
    def margin_display(self, obj):
        pct = obj.margin_percent
        return f'{pct}%' if pct is not None else '—'
