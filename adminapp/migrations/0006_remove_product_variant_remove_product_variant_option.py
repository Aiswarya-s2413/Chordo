# Generated by Django 5.1.1 on 2024-10-10 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0005_alter_product_variant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='variant',
        ),
        migrations.RemoveField(
            model_name='product',
            name='variant_option',
        ),
    ]
