# Generated by Django 5.1.1 on 2024-11-02 03:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0028_remove_offer_product_delete_categoryoffer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='adminapp.product'),
        ),
    ]
