# Generated by Django 4.0.1 on 2022-03-19 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0059_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(2, 'Fevereiro'), (12, 'Dezembro'), (7, 'Julho'), (5, 'Maio'), (9, 'Setembro'), (1, 'Janeiro'), (8, 'Agosto'), (6, 'Junho'), (11, 'Novembro'), (3, 'Março'), (10, 'Outubro'), (4, 'Abril')]),
        ),
    ]