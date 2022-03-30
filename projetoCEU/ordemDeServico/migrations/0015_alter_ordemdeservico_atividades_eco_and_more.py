# Generated by Django 4.0.1 on 2022-03-30 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0036_alter_resumofinanceiro_valor'),
        ('ordemDeServico', '0014_ordemdeservico_atividades_eco_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemdeservico',
            name='atividades_eco',
            field=models.ManyToManyField(blank=True, to='peraltas.AtividadesEco'),
        ),
        migrations.AlterField(
            model_name='ordemdeservico',
            name='atividades_peraltas',
            field=models.ManyToManyField(blank=True, to='peraltas.AtividadePeraltas'),
        ),
    ]
