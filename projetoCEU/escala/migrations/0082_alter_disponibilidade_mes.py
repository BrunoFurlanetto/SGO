# Generated by Django 4.0.1 on 2022-03-24 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0081_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(2, 'Fevereiro'), (4, 'Abril'), (5, 'Maio'), (11, 'Novembro'), (3, 'Março'), (10, 'Outubro'), (1, 'Janeiro'), (9, 'Setembro'), (6, 'Junho'), (7, 'Julho'), (12, 'Dezembro'), (8, 'Agosto')]),
        ),
    ]