# Generated by Django 4.0.1 on 2022-05-01 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0034_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(5, 'Maio'), (6, 'Junho'), (11, 'Novembro'), (9, 'Setembro'), (10, 'Outubro'), (3, 'Março'), (8, 'Agosto'), (12, 'Dezembro'), (2, 'Fevereiro'), (4, 'Abril'), (1, 'Janeiro'), (7, 'Julho')]),
        ),
    ]
