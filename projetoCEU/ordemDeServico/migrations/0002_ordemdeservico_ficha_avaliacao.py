# Generated by Django 4.0.1 on 2022-05-21 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordemDeServico', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemdeservico',
            name='ficha_avaliacao',
            field=models.BooleanField(default=False),
        ),
    ]
