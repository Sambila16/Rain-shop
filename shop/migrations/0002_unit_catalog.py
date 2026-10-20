from django.db import migrations, models


def seed_units(apps, schema_editor):
    Unit = apps.get_model('shop', 'Unit')
    for name in ('bottle', 'crate', 'carton', 'pack', 'piece'):
        Unit.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [('shop', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.RunPython(seed_units, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(default='bottle', max_length=20),
        ),
    ]
