# Generated by Django 5.1.1 on 2024-11-01 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0026_order_return_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='popularity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]