# Generated by Django 4.0.1 on 2022-07-03 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0059_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(1, 'Janeiro'), (5, 'Maio'), (4, 'Abril'), (3, 'Março'), (11, 'Novembro'), (8, 'Agosto'), (12, 'Dezembro'), (2, 'Fevereiro'), (6, 'Junho'), (10, 'Outubro'), (9, 'Setembro'), (7, 'Julho')]),
        ),
    ]
