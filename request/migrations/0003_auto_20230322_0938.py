# Generated by Django 3.2.9 on 2023-03-22 09:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0002_subcategoryrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategoryrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subcategoryrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
