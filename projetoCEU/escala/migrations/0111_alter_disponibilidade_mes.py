# Generated by Django 4.0.1 on 2022-04-01 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0110_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (9, 'Setembro'), (2, 'Fevereiro'), (11, 'Novembro'), (10, 'Outubro'), (1, 'Janeiro'), (6, 'Junho'), (12, 'Dezembro'), (7, 'Julho'), (5, 'Maio'), (8, 'Agosto'), (3, 'Março')]),
        ),
    ]