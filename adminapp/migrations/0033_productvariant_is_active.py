# Generated by Django 5.1.1 on 2024-11-06 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0032_remove_product_variant_remove_variantoption_variant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
