# Generated by Django 4.0.1 on 2022-05-01 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0002_monitor_n_avaliacoes_vendedor_n_avaliacoes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientecolegio',
            name='codigo_app_pf',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='clientecolegio',
            name='codigo_app_pj',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]