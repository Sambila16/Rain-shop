from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('shop', '0002_unit_catalog')]

    operations = [
        migrations.AddField(
            model_name='product',
            name='items_per_carton',
            field=models.PositiveIntegerField(default=24, help_text='Number of single items in one carton'),
        ),
        migrations.AddField(
            model_name='product',
            name='sell_carton_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Leave blank if this product is not sold by the carton', max_digits=10, null=True),
        ),
    ]
