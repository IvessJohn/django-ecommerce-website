# Generated by Django 4.0.2 on 2022-04-05 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_order_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='device_id',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]