from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)  # item no, shown to staff and customers
    barcode = models.CharField(
        max_length=64, unique=True, blank=True, null=True, db_index=True,
        help_text='The number/code printed in the barcode on the product.'
    )
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items'
    )
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.code} — {self.name}'

    def save(self, *args, **kwargs):
        # An empty string in a unique field isn't the same as NULL to the database,
        # so two blank barcodes would collide. Normalize blank -> None on every save
        # so items can be added without a barcode.
        if not self.barcode:
            self.barcode = None
        super().save(*args, **kwargs)

    @property
    def margin_percent(self):
        if not self.retail_price:
            return None
        return round((self.retail_price - self.wholesale_price) / self.retail_price * 100)
