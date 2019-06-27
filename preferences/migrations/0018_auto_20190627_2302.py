# Generated by Django 2.1 on 2019-06-27 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0017_auto_20190623_1453'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='priceprofile',
            options={'verbose_name': 'Profil de prix', 'verbose_name_plural': 'Profils de prix'},
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='amount_ptm',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, null=True, verbose_name='Montant pour le club Phœnix Technopôle Metz'),
        ),
        migrations.AlterField(
            model_name='historicalcotisation',
            name='amount_ptm',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, null=True, verbose_name='Montant pour le club Phœnix Technopôle Metz'),
        ),
    ]