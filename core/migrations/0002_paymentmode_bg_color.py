# Generated by Django 5.0.6 on 2024-07-16 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_squash'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmode',
            name='bg_color',
            field=models.CharField(default='175175', max_length=6),
        ),
    ]
