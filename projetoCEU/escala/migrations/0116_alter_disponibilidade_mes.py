# Generated by Django 4.0.1 on 2022-04-14 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0115_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (6, 'Junho'), (1, 'Janeiro'), (7, 'Julho'), (12, 'Dezembro'), (8, 'Agosto'), (2, 'Fevereiro'), (5, 'Maio'), (11, 'Novembro'), (9, 'Setembro'), (4, 'Abril'), (3, 'Março')]),
        ),
    ]
