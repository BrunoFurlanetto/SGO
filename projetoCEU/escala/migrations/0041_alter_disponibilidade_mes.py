# Generated by Django 4.0.1 on 2022-05-21 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0040_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (9, 'Setembro'), (8, 'Agosto'), (12, 'Dezembro'), (4, 'Abril'), (1, 'Janeiro'), (3, 'Março'), (2, 'Fevereiro'), (5, 'Maio'), (7, 'Julho'), (6, 'Junho'), (11, 'Novembro')]),
        ),
    ]
