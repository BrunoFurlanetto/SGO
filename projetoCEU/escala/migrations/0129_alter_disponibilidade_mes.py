# Generated by Django 4.0.1 on 2022-04-18 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0128_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(11, 'Novembro'), (3, 'Março'), (2, 'Fevereiro'), (4, 'Abril'), (8, 'Agosto'), (6, 'Junho'), (12, 'Dezembro'), (5, 'Maio'), (10, 'Outubro'), (9, 'Setembro'), (1, 'Janeiro'), (7, 'Julho')]),
        ),
    ]
