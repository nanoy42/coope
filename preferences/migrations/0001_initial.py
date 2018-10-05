# Generated by Django 2.1 on 2018-10-04 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cotisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5, null=True, verbose_name='Montant')),
                ('duration', models.PositiveIntegerField(verbose_name='Durée de la cotisation (jours)')),
            ],
        ),
        migrations.CreateModel(
            name='GeneralPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('active_message', models.TextField(blank=True)),
                ('global_message', models.TextField(blank=True)),
                ('president', models.CharField(blank=True, max_length=255)),
                ('vice_president', models.CharField(blank=True, max_length=255)),
                ('treasurer', models.CharField(blank=True, max_length=255)),
                ('secretary', models.CharField(blank=True, max_length=255)),
                ('brewer', models.CharField(blank=True, max_length=255)),
                ('grocer', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
                ('is_active', models.BooleanField(default=True)),
                ('is_usable_in_cotisation', models.BooleanField(default=True)),
                ('affect_balance', models.BooleanField(default=False)),
            ],
        ),
    ]
