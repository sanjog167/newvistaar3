# Generated by Django 3.2.9 on 2023-05-01 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20230322_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='brand',
            field=models.CharField(blank=True, default='Not Mentioned', max_length=100, null=True),
        ),
    ]