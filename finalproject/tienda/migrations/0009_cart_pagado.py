# Generated by Django 2.2.10 on 2020-05-09 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0008_product_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='pagado',
            field=models.CharField(choices=[('0', 'No'), ('1', 'Si')], default=0, max_length=5),
        ),
    ]
