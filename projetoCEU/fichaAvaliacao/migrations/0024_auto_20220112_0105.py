# Generated by Django 3.2.9 on 2022-01-12 04:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichaAvaliacao', '0023_alter_fichadeavaliacao_data_preenchimento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='data_atividade_1',
            field=models.DateField(verbose_name='0000/00/00'),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='data_preenchimento',
            field=models.DateField(default=datetime.datetime(2022, 1, 12, 1, 5, 10, 477640)),
        ),
    ]