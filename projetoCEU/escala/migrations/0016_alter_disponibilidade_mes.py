# Generated by Django 4.0.1 on 2022-02-26 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0015_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(3, 'Março'), (11, 'Novembro'), (4, 'Abril'), (8, 'Agosto'), (6, 'Junho'), (2, 'Fevereiro'), (7, 'Julho'), (1, 'Janeiro'), (10, 'Outubro'), (5, 'Maio'), (12, 'Dezembro'), (9, 'Setembro')]),
        ),
    ]
