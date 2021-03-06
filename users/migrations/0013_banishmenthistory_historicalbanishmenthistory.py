# Generated by Django 2.1 on 2019-10-06 09:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0012_auto_20190925_0125'),
    ]

    operations = [
        migrations.CreateModel(
            name='BanishmentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ban_date', models.DateTimeField(auto_now_add=True, verbose_name='Date du banissement')),
                ('end_date', models.DateTimeField(verbose_name='Date de fin')),
                ('reason', models.CharField(blank=True, max_length=255, verbose_name='Raison')),
                ('coopeman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='banishment_made', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Client')),
            ],
            options={
                'verbose_name': 'Historique banissement',
                'verbose_name_plural': 'Historique banissements',
            },
        ),
        migrations.CreateModel(
            name='HistoricalBanishmentHistory',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('ban_date', models.DateTimeField(blank=True, editable=False, verbose_name='Date du banissement')),
                ('end_date', models.DateTimeField(verbose_name='Date de fin')),
                ('reason', models.CharField(blank=True, max_length=255, verbose_name='Raison')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('coopeman', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Historique banissement',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
