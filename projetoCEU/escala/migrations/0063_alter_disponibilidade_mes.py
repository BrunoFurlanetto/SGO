# Generated by Django 4.0.1 on 2022-03-21 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0062_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(11, 'Novembro'), (2, 'Fevereiro'), (9, 'Setembro'), (6, 'Junho'), (7, 'Julho'), (3, 'Março'), (5, 'Maio'), (4, 'Abril'), (12, 'Dezembro'), (1, 'Janeiro'), (10, 'Outubro'), (8, 'Agosto')]),
        ),
    ]
