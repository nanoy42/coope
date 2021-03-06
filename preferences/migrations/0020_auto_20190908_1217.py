# Generated by Django 2.1 on 2019-09-08 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0019_improvement'),
    ]

    operations = [
        migrations.AddField(
            model_name='improvement',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default='2019-09-08 00:00'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='improvement',
            name='done',
            field=models.BooleanField(default=False, verbose_name='Fait ?'),
        ),
        migrations.AlterField(
            model_name='improvement',
            name='mode',
            field=models.IntegerField(choices=[(0, 'Bug'), (1, 'Amélioration'), (2, 'Nouvelle fonctionnalité')], verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='improvement',
            name='seen',
            field=models.BooleanField(default=False, verbose_name='Vu ?'),
        ),
        migrations.AlterField(
            model_name='improvement',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Titre'),
        ),
    ]
