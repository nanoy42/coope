# Generated by Django 2.1 on 2019-01-05 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0004_auto_20181223_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='showingMultiplier',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='product',
            name='showingMultiplier',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
