# Generated by Django 5.0.1 on 2024-01-25 11:11

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_customer_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='country',
            field=django_countries.fields.CountryField(max_length=200, null=True),
        ),
    ]