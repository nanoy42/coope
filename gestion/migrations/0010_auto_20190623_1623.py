# Generated by Django 2.1 on 2019-06-23 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0009_auto_20190506_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalkeg',
            name='name',
            field=models.CharField(db_index=True, max_length=255, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='barcode',
            field=models.CharField(db_index=True, max_length=255, verbose_name='Code barre'),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='name',
            field=models.CharField(db_index=True, max_length=255, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='keg',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='product',
            name='barcode',
            field=models.CharField(max_length=255, unique=True, verbose_name='Code barre'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nom'),
        ),
    ]
