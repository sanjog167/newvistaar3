# Generated by Django 3.2.9 on 2022-04-03 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_quotations_a'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quotations',
            name='a',
        ),
    ]
