# Generated by Django 3.2.9 on 2022-01-12 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichaAvaliacao', '0020_alter_fichadeavaliacao_data_atividade_1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='n_alunos',
            field=models.IntegerField(default=0, max_length=200),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='n_educadores',
            field=models.IntegerField(default=0, max_length=200),
        ),
    ]
