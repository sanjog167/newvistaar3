# Generated by Django 3.2.9 on 2023-03-21 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0007_supplier_mobile_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='slug',
            field=models.SlugField(blank=True, max_length=200, null=True),
        ),
    ]
