# Generated by Django 4.0.1 on 2022-02-06 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0027_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (12, 'Dezembro'), (8, 'Agosto'), (5, 'Maio'), (2, 'Fevereiro'), (3, 'Março'), (11, 'Novembro'), (1, 'Janeiro'), (9, 'Setembro'), (4, 'Abril'), (6, 'Junho'), (7, 'Julho')]),
        ),
    ]