# Generated by Django 2.1 on 2019-06-23 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0010_auto_20190623_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalkeg',
            name='barcode',
        ),
        migrations.RemoveField(
            model_name='historicalmenu',
            name='barcode',
        ),
        migrations.RemoveField(
            model_name='historicalproduct',
            name='barcode',
        ),
        migrations.RemoveField(
            model_name='keg',
            name='barcode',
        ),
        migrations.RemoveField(
            model_name='menu',
            name='barcode',
        ),
        migrations.RemoveField(
            model_name='product',
            name='barcode',
        ),
    ]