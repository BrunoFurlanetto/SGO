# Generated by Django 4.0.1 on 2022-04-23 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0005_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(1, 'Janeiro'), (3, 'Março'), (2, 'Fevereiro'), (7, 'Julho'), (4, 'Abril'), (5, 'Maio'), (8, 'Agosto'), (9, 'Setembro'), (11, 'Novembro'), (10, 'Outubro'), (12, 'Dezembro'), (6, 'Junho')]),
        ),
    ]
