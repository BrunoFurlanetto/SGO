# Generated by Django 4.0.1 on 2022-03-23 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0023_alter_informacoesadcionais_atividades_eco_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumofinanceiro',
            name='observacoes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='resumofinanceiro',
            name='valor_por_participantes',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='resumofinanceiro',
            name='forma_pagamento',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]