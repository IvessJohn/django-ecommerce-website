# Generated by Django 4.0.2 on 2022-04-06 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_customer_device_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]