# Generated by Django 4.0.1 on 2022-04-30 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0026_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (7, 'Julho'), (1, 'Janeiro'), (3, 'Março'), (2, 'Fevereiro'), (9, 'Setembro'), (12, 'Dezembro'), (4, 'Abril'), (8, 'Agosto'), (5, 'Maio'), (11, 'Novembro'), (10, 'Outubro')]),
        ),
    ]
