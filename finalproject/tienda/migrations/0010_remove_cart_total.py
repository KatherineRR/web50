# Generated by Django 2.2.10 on 2020-05-09 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0009_cart_pagado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='total',
        ),
    ]