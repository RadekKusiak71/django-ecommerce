# Generated by Django 5.0.1 on 2024-01-27 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_order_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_status',
            field=models.CharField(choices=[('p', 'Pending'), ('c', 'Cancelled'), ('d', 'Declined'), ('ap', 'Awaiting Pickup'), ('as', 'Awaiting Shipment'), ('cp', 'Completed'), ('pr', 'Preparing')], default=('p', 'Pending'), max_length=3),
        ),
    ]