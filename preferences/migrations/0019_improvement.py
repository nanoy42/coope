# Generated by Django 2.1 on 2019-09-08 09:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('preferences', '0018_auto_20190627_2302'),
    ]

    operations = [
        migrations.CreateModel(
            name='Improvement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('mode', models.IntegerField(choices=[(0, 'Bug'), (1, 'Amélioration'), (2, 'Nouvelle fonctionnalité')])),
                ('description', models.TextField()),
                ('seen', models.BooleanField(default=False)),
                ('done', models.BooleanField(default=False)),
                ('coopeman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='improvement_submitted', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Amélioration',
            },
        ),
    ]
