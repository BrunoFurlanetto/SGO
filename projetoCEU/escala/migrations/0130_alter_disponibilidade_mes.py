# Generated by Django 4.0.1 on 2022-04-18 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0129_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(9, 'Setembro'), (1, 'Janeiro'), (2, 'Fevereiro'), (12, 'Dezembro'), (5, 'Maio'), (7, 'Julho'), (6, 'Junho'), (8, 'Agosto'), (10, 'Outubro'), (4, 'Abril'), (3, 'Março'), (11, 'Novembro')]),
        ),
    ]
