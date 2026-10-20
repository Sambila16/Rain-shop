from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0005_sale_loan_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(choices=[('cash', 'Cash'), ('mobile', 'Mobile money'), ('bank', 'Bank')], default='cash', max_length=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loan_payments', to='shop.customer')),
            ],
            options={'ordering': ['-date']},
        ),
    ]
