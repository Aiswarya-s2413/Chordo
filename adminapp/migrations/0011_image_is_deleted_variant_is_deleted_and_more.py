# Generated by Django 5.1.1 on 2024-10-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0010_alter_product_variant_alter_product_variant_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variant',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variantoption',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
