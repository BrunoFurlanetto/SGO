# Generated by Django 4.0.1 on 2022-03-18 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0053_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(7, 'Julho'), (5, 'Maio'), (10, 'Outubro'), (12, 'Dezembro'), (1, 'Janeiro'), (3, 'Março'), (6, 'Junho'), (4, 'Abril'), (2, 'Fevereiro'), (9, 'Setembro'), (11, 'Novembro'), (8, 'Agosto')]),
        ),
    ]