# Generated by Django 5.1.1 on 2024-10-30 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0020_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
