# Generated by Django 4.0.1 on 2022-03-18 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0054_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (6, 'Junho'), (8, 'Agosto'), (11, 'Novembro'), (10, 'Outubro'), (5, 'Maio'), (1, 'Janeiro'), (9, 'Setembro'), (12, 'Dezembro'), (2, 'Fevereiro'), (7, 'Julho'), (3, 'Março')]),
        ),
    ]