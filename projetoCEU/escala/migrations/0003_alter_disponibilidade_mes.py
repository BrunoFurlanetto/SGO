# Generated by Django 4.0.1 on 2022-04-22 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0002_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (2, 'Fevereiro'), (12, 'Dezembro'), (5, 'Maio'), (7, 'Julho'), (1, 'Janeiro'), (11, 'Novembro'), (6, 'Junho'), (3, 'Março'), (4, 'Abril'), (8, 'Agosto'), (9, 'Setembro')]),
        ),
    ]
