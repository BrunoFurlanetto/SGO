# Generated by Django 4.0.1 on 2022-05-08 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0035_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (5, 'Maio'), (7, 'Julho'), (6, 'Junho'), (2, 'Fevereiro'), (3, 'Março'), (11, 'Novembro'), (4, 'Abril'), (12, 'Dezembro'), (1, 'Janeiro'), (8, 'Agosto'), (9, 'Setembro')]),
        ),
    ]
