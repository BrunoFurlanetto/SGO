# Generated by Django 4.0.1 on 2022-03-10 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0015_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(1, 'Janeiro'), (9, 'Setembro'), (10, 'Outubro'), (3, 'Março'), (2, 'Fevereiro'), (6, 'Junho'), (5, 'Maio'), (11, 'Novembro'), (7, 'Julho'), (8, 'Agosto'), (4, 'Abril'), (12, 'Dezembro')]),
        ),
    ]