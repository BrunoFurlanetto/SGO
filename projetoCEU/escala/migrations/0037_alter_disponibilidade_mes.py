# Generated by Django 4.0.1 on 2022-05-20 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0036_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(9, 'Setembro'), (5, 'Maio'), (10, 'Outubro'), (7, 'Julho'), (12, 'Dezembro'), (8, 'Agosto'), (6, 'Junho'), (11, 'Novembro'), (2, 'Fevereiro'), (1, 'Janeiro'), (4, 'Abril'), (3, 'Março')]),
        ),
    ]
