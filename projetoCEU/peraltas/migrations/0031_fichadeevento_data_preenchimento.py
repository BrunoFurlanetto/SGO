# Generated by Django 4.0.1 on 2022-03-24 17:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0030_alter_resumofinanceiro_valor'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichadeevento',
            name='data_preenchimento',
            field=models.DateField(blank=True, default=datetime.datetime.now, null=True),
        ),
    ]