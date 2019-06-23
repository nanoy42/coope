# Generated by Django 2.1 on 2019-06-23 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0015_dividehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('a', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='Marge constante')),
                ('b', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='Marge constante')),
                ('c', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Marge constante')),
                ('alpha', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Marge constante')),
                ('use_for_draft', models.BooleanField(default=False)),
            ],
        ),
    ]
