# Generated by Django 4.0.1 on 2022-04-30 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0012_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(11, 'Novembro'), (6, 'Junho'), (5, 'Maio'), (8, 'Agosto'), (3, 'Março'), (7, 'Julho'), (9, 'Setembro'), (1, 'Janeiro'), (2, 'Fevereiro'), (10, 'Outubro'), (4, 'Abril'), (12, 'Dezembro')]),
        ),
    ]