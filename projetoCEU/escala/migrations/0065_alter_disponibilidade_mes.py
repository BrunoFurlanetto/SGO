# Generated by Django 4.0.1 on 2022-07-17 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0064_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (1, 'Janeiro'), (2, 'Fevereiro'), (8, 'Agosto'), (5, 'Maio'), (10, 'Outubro'), (12, 'Dezembro'), (9, 'Setembro'), (11, 'Novembro'), (3, 'Março'), (7, 'Julho'), (4, 'Abril')]),
        ),
    ]
