# Generated by Django 5.1.1 on 2024-11-20 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0047_orderitem_approval_status_orderitem_request_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_charge',
            field=models.DecimalField(decimal_places=2, default=100.0, max_digits=10),
        ),
    ]
