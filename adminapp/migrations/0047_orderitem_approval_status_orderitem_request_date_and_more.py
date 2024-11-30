# Generated by Django 5.1.1 on 2024-11-15 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0046_order_discount_amount_alter_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='approval_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='request_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='request_type',
            field=models.CharField(blank=True, choices=[('cancel', 'Cancel'), ('return', 'Return')], max_length=20, null=True),
        ),
    ]