# Generated by Django 2.2.10 on 2020-05-07 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0006_brand_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='imagen',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
    ]
