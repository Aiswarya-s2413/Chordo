# Generated by Django 5.1.1 on 2024-11-01 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0025_order_cancellation_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='return_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
