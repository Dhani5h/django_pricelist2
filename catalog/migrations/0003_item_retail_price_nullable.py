from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_item_barcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='retail_price',
            field=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
        ),
    ]
