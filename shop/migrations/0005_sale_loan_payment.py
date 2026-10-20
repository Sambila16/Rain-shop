from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('shop', '0004_product_items_per_carton_default')]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='payment',
            field=models.CharField(
                choices=[('cash', 'Cash'), ('mobile', 'Mobile money'), ('bank', 'Bank'), ('loan', 'Loan')],
                default='cash',
                max_length=10,
            ),
        ),
    ]
