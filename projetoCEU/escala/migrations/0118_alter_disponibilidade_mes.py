# Generated by Django 4.0.1 on 2022-04-14 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0117_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(12, 'Dezembro'), (3, 'Março'), (2, 'Fevereiro'), (10, 'Outubro'), (1, 'Janeiro'), (4, 'Abril'), (11, 'Novembro'), (5, 'Maio'), (8, 'Agosto'), (7, 'Julho'), (6, 'Junho'), (9, 'Setembro')]),
        ),
    ]
