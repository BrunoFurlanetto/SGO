# Generated by Django 4.0.1 on 2022-03-13 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordemDeServico', '0005_ordemdeservico_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemdeservico',
            name='loacao_ceu',
            field=models.JSONField(blank=True, null=True),
        ),
    ]