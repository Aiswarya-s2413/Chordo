# Generated by Django 5.1.1 on 2024-10-14 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0007_customuser_otp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='otp',
        ),
    ]