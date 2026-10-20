from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('shop', '0003_product_carton_pricing')]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='items_per_carton',
            field=models.PositiveIntegerField(default=1, help_text='Number of single items in one carton'),
        ),
    ]
