# Generated by Django 4.0.2 on 2022-03-16 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon_management', '0002_alter_allowedusersrule_options_and_more'),
        ('store', '0008_alter_shippinginformation_country'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippinginformation',
            options={'verbose_name': 'Shipping Information', 'verbose_name_plural': 'Shipping Informations'},
        ),
        migrations.AddField(
            model_name='order',
            name='applied_coupon',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='coupon_management.coupon'),
        ),
    ]
