# Generated by Django 2.1 on 2018-12-13 18:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import gestion.models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('preferences', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consumption_global_taken', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Consommation totale',
            },
        ),
        migrations.CreateModel(
            name='ConsumptionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('coopeman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consumption_selled', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consumption_taken', to=settings.AUTH_USER_MODEL)),
                ('paymentMethod', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='preferences.PaymentMethod')),
            ],
            options={
                'verbose_name': 'Consommation',
            },
        ),
        migrations.CreateModel(
            name='HistoricalConsumption',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('customer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Consommation totale',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalConsumptionHistory',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(blank=True, editable=False)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('coopeman', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('paymentMethod', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='preferences.PaymentMethod')),
            ],
            options={
                'verbose_name': 'historical Consommation',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalKeg',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=20, verbose_name='Nom')),
                ('stockHold', models.IntegerField(default=0, verbose_name='Stock en soute')),
                ('barcode', models.CharField(db_index=True, max_length=20, verbose_name='Code barre')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Prix du fût')),
                ('capacity', models.IntegerField(default=30, verbose_name='Capacité (L)')),
                ('is_active', models.BooleanField(default=False, verbose_name='Actif')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical Fût',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalKegHistory',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('openingDate', models.DateTimeField(blank=True, editable=False)),
                ('quantitySold', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('amountSold', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('closingDate', models.DateTimeField(blank=True, null=True)),
                ('isCurrentKegHistory', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Historique de fût',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalMenu',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Montant')),
                ('barcode', models.CharField(db_index=True, max_length=20, verbose_name='Code barre')),
                ('is_active', models.BooleanField(default=False, verbose_name='Actif')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical menu',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalMenuHistory',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(blank=True, editable=False)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('coopeman', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Historique de menu',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProduct',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=40, verbose_name='Nom')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Prix de vente')),
                ('stockHold', models.IntegerField(default=0, verbose_name='Stock en soute')),
                ('stockBar', models.IntegerField(default=0, verbose_name='Stock en bar')),
                ('barcode', models.CharField(db_index=True, max_length=20, verbose_name='Code barre')),
                ('category', models.CharField(choices=[('PP', 'Pinte Pression'), ('DP', 'Demi Pression'), ('GP', 'Galopin pression'), ('BT', 'Bouteille'), ('SO', 'Soft'), ('FO', 'Bouffe autre que panini'), ('PA', 'Bouffe pour panini')], default='FO', max_length=2, verbose_name='Catégorie')),
                ('needQuantityButton', models.BooleanField(default=False, verbose_name='Bouton quantité')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('volume', models.PositiveIntegerField(default=0)),
                ('deg', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Degré')),
                ('adherentRequired', models.BooleanField(default=True, verbose_name='Adhérent requis')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Produit',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRefund',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, editable=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Montant')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('coopeman', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Remboursement',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalReload',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Montant')),
                ('date', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('PaymentMethod', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='preferences.PaymentMethod')),
                ('coopeman', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Rechargement',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Keg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='Nom')),
                ('stockHold', models.IntegerField(default=0, verbose_name='Stock en soute')),
                ('barcode', models.CharField(max_length=20, unique=True, verbose_name='Code barre')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Prix du fût')),
                ('capacity', models.IntegerField(default=30, verbose_name='Capacité (L)')),
                ('is_active', models.BooleanField(default=False, verbose_name='Actif')),
            ],
            options={
                'verbose_name': 'Fût',
                'permissions': (('open_keg', 'Peut percuter les fûts'), ('close_keg', 'Peut fermer les fûts')),
            },
        ),
        migrations.CreateModel(
            name='KegHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openingDate', models.DateTimeField(auto_now_add=True)),
                ('quantitySold', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('amountSold', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('closingDate', models.DateTimeField(blank=True, null=True)),
                ('isCurrentKegHistory', models.BooleanField(default=True)),
                ('keg', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Keg')),
            ],
            options={
                'verbose_name': 'Historique de fût',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Montant')),
                ('barcode', models.CharField(max_length=20, unique=True, verbose_name='Code barre')),
                ('is_active', models.BooleanField(default=False, verbose_name='Actif')),
            ],
        ),
        migrations.CreateModel(
            name='MenuHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('coopeman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='menu_selled', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='menu_taken', to=settings.AUTH_USER_MODEL)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Menu')),
                ('paymentMethod', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='preferences.PaymentMethod')),
            ],
            options={
                'verbose_name': 'Historique de menu',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='Nom')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Prix de vente')),
                ('stockHold', models.IntegerField(default=0, verbose_name='Stock en soute')),
                ('stockBar', models.IntegerField(default=0, verbose_name='Stock en bar')),
                ('barcode', models.CharField(max_length=20, unique=True, verbose_name='Code barre')),
                ('category', models.CharField(choices=[('PP', 'Pinte Pression'), ('DP', 'Demi Pression'), ('GP', 'Galopin pression'), ('BT', 'Bouteille'), ('SO', 'Soft'), ('FO', 'Bouffe autre que panini'), ('PA', 'Bouffe pour panini')], default='FO', max_length=2, verbose_name='Catégorie')),
                ('needQuantityButton', models.BooleanField(default=False, verbose_name='Bouton quantité')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('volume', models.PositiveIntegerField(default=0)),
                ('deg', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Degré')),
                ('adherentRequired', models.BooleanField(default=True, verbose_name='Adhérent requis')),
            ],
            options={
                'verbose_name': 'Produit',
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Montant')),
                ('coopeman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='refund_realized', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='refund_taken', to=settings.AUTH_USER_MODEL, verbose_name='Client')),
            ],
            options={
                'verbose_name': 'Remboursement',
            },
        ),
        migrations.CreateModel(
            name='Reload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Montant')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('PaymentMethod', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='preferences.PaymentMethod', verbose_name='Moyen de paiement')),
                ('coopeman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reload_realized', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reload_taken', to=settings.AUTH_USER_MODEL, verbose_name='Client')),
            ],
            options={
                'verbose_name': 'Rechargement',
            },
        ),
        migrations.AddField(
            model_name='menu',
            name='articles',
            field=models.ManyToManyField(to='gestion.Product', verbose_name='Produits'),
        ),
        migrations.AddField(
            model_name='keg',
            name='demi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='futd', to='gestion.Product', validators=[gestion.models.isDemi]),
        ),
        migrations.AddField(
            model_name='keg',
            name='galopin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='futg', to='gestion.Product', validators=[gestion.models.isGalopin]),
        ),
        migrations.AddField(
            model_name='keg',
            name='pinte',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='futp', to='gestion.Product', validators=[gestion.models.isPinte]),
        ),
        migrations.AddField(
            model_name='historicalmenuhistory',
            name='menu',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Menu'),
        ),
        migrations.AddField(
            model_name='historicalmenuhistory',
            name='paymentMethod',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='preferences.PaymentMethod'),
        ),
        migrations.AddField(
            model_name='historicalkeghistory',
            name='keg',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Keg'),
        ),
        migrations.AddField(
            model_name='historicalkeg',
            name='demi',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Product'),
        ),
        migrations.AddField(
            model_name='historicalkeg',
            name='galopin',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Product'),
        ),
        migrations.AddField(
            model_name='historicalkeg',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalkeg',
            name='pinte',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Product'),
        ),
        migrations.AddField(
            model_name='historicalconsumptionhistory',
            name='product',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Product'),
        ),
        migrations.AddField(
            model_name='historicalconsumption',
            name='product',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestion.Product'),
        ),
        migrations.AddField(
            model_name='consumptionhistory',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Product'),
        ),
        migrations.AddField(
            model_name='consumption',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Product'),
        ),
    ]
