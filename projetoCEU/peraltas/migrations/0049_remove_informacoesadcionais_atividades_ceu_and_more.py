# Generated by Django 4.0.1 on 2022-04-03 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0007_alter_locaveis_local'),
        ('peraltas', '0048_informacoesadcionais_terceirizado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='informacoesadcionais',
            name='atividades_ceu',
        ),
        migrations.RemoveField(
            model_name='informacoesadcionais',
            name='atividades_eco',
        ),
        migrations.RemoveField(
            model_name='informacoesadcionais',
            name='locacoes_ceu',
        ),
        migrations.AddField(
            model_name='fichadeevento',
            name='atividades_ceu',
            field=models.ManyToManyField(blank=True, to='ceu.Atividades'),
        ),
        migrations.AddField(
            model_name='fichadeevento',
            name='atividades_eco',
            field=models.ManyToManyField(blank=True, to='peraltas.AtividadesEco'),
        ),
        migrations.AddField(
            model_name='fichadeevento',
            name='atividades_peraltas',
            field=models.ManyToManyField(blank=True, to='peraltas.AtividadePeraltas'),
        ),
        migrations.AddField(
            model_name='fichadeevento',
            name='locacoes_ceu',
            field=models.ManyToManyField(blank=True, to='ceu.Locaveis'),
        ),
    ]