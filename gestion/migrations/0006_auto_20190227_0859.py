# Generated by Django 2.1 on 2019-02-27 07:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_auto_20190106_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumption',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consumption_global_taken', to=settings.AUTH_USER_MODEL, verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='consumption',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Product', verbose_name='Produit'),
        ),
        migrations.AlterField(
            model_name='consumption',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='consumptionhistory',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Montant'),
        ),
        migrations.AlterField(
            model_name='consumptionhistory',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consumption_taken', to=settings.AUTH_USER_MODEL, verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='consumptionhistory',
            name='paymentMethod',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='preferences.PaymentMethod', verbose_name='Moyen de paiement'),
        ),
        migrations.AlterField(
            model_name='consumptionhistory',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Product', verbose_name='Produit'),
        ),
        migrations.AlterField(
            model_name='consumptionhistory',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='historicalconsumption',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='historicalconsumptionhistory',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Montant'),
        ),
        migrations.AlterField(
            model_name='historicalconsumptionhistory',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='historicalkeghistory',
            name='amountSold',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Somme vendue'),
        ),
        migrations.AlterField(
            model_name='historicalkeghistory',
            name='closingDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date fermeture'),
        ),
        migrations.AlterField(
            model_name='historicalkeghistory',
            name='isCurrentKegHistory',
            field=models.BooleanField(default=True, verbose_name='Actuel'),
        ),
        migrations.AlterField(
            model_name='historicalkeghistory',
            name='openingDate',
            field=models.DateTimeField(blank=True, editable=False, verbose_name='Date ouverture'),
        ),
        migrations.AlterField(
            model_name='historicalkeghistory',
            name='quantitySold',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Quantité vendue'),
        ),
        migrations.AlterField(
            model_name='historicalmenuhistory',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Montant'),
        ),
        migrations.AlterField(
            model_name='historicalmenuhistory',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='category',
            field=models.CharField(choices=[('PP', 'Pinte Pression'), ('DP', 'Demi Pression'), ('GP', 'Galopin pression'), ('BT', 'Bouteille'), ('SO', 'Soft'), ('FO', 'En-cas'), ('PA', 'Ingredients panini')], default='FO', max_length=2, verbose_name='Catégorie'),
        ),
        migrations.AlterField(
            model_name='keghistory',
            name='amountSold',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Somme vendue'),
        ),
        migrations.AlterField(
            model_name='keghistory',
            name='closingDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date fermeture'),
        ),
        migrations.AlterField(
            model_name='keghistory',
            name='isCurrentKegHistory',
            field=models.BooleanField(default=True, verbose_name='Actuel'),
        ),
        migrations.AlterField(
            model_name='keghistory',
            name='keg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Keg', verbose_name='Fût'),
        ),
        migrations.AlterField(
            model_name='keghistory',
            name='openingDate',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date ouverture'),
        ),
        migrations.AlterField(
            model_name='keghistory',
            name='quantitySold',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Quantité vendue'),
        ),
        migrations.AlterField(
            model_name='menuhistory',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Montant'),
        ),
        migrations.AlterField(
            model_name='menuhistory',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='menu_taken', to=settings.AUTH_USER_MODEL, verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='menuhistory',
            name='paymentMethod',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='preferences.PaymentMethod', verbose_name='Moyen de paiement'),
        ),
        migrations.AlterField(
            model_name='menuhistory',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('PP', 'Pinte Pression'), ('DP', 'Demi Pression'), ('GP', 'Galopin pression'), ('BT', 'Bouteille'), ('SO', 'Soft'), ('FO', 'En-cas'), ('PA', 'Ingredients panini')], default='FO', max_length=2, verbose_name='Catégorie'),
        ),
    ]