# Generated by Django 5.1.1 on 2024-10-10 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0003_rename_stock_product_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(max_length=255, upload_to='product_images/'),
        ),
    ]