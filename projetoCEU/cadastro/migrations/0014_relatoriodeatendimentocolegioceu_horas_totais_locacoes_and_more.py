# Generated by Django 4.0.1 on 2022-03-29 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0013_relatoriodeatendimentopublicoceu_data_hora_salvo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatoriodeatendimentocolegioceu',
            name='horas_totais_locacoes',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='relatoriodeatendimentoempresaceu',
            name='horas_totais_locacoes',
            field=models.DurationField(blank=True, null=True),
        ),
    ]