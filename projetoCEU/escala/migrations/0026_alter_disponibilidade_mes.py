# Generated by Django 4.0.1 on 2022-04-30 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0025_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(11, 'Novembro'), (3, 'Março'), (2, 'Fevereiro'), (12, 'Dezembro'), (5, 'Maio'), (1, 'Janeiro'), (4, 'Abril'), (10, 'Outubro'), (7, 'Julho'), (9, 'Setembro'), (6, 'Junho'), (8, 'Agosto')]),
        ),
    ]