# Generated by Django 2.1 on 2019-01-20 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0006_auto_20190119_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalpreferences',
            name='automatic_logout_time',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralpreferences',
            name='automatic_logout_time',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
