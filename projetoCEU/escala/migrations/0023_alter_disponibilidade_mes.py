# Generated by Django 4.0.1 on 2022-04-30 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0022_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'), (4, 'Abril'), (1, 'Janeiro'), (2, 'Fevereiro'), (12, 'Dezembro'), (5, 'Maio'), (3, 'Março'), (6, 'Junho'), (11, 'Novembro')]),
        ),
    ]
