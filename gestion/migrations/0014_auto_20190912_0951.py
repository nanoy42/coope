# Generated by Django 2.1 on 2019-09-12 07:51

import django.core.validators
from django.db import migrations, models

def update(apps, schema_editor):
    Keg = apps.get_model('gestion', 'Keg')
    for keg in Keg.objects.all():
        keg.deg = keg.pinte.deg
        keg.save()

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0013_auto_20190829_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalkeg',
            name='deg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Degré'),
        ),
        migrations.AddField(
            model_name='keg',
            name='deg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Degré'),
        ),
        migrations.RunPython(update, reverse)
    ]
