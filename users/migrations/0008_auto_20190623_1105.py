# Generated by Django 2.1 on 2019-06-23 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20190623_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalwhitelisthistory',
            name='reason',
            field=models.CharField(blank=True, max_length=255, verbose_name='Raison'),
        ),
        migrations.AddField(
            model_name='whitelisthistory',
            name='reason',
            field=models.CharField(blank=True, max_length=255, verbose_name='Raison'),
        ),
    ]
