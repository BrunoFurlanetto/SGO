# Generated by Django 4.0.1 on 2022-03-23 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0076_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(8, 'Agosto'), (2, 'Fevereiro'), (11, 'Novembro'), (7, 'Julho'), (6, 'Junho'), (9, 'Setembro'), (10, 'Outubro'), (5, 'Maio'), (4, 'Abril'), (3, 'Março'), (1, 'Janeiro'), (12, 'Dezembro')]),
        ),
    ]
