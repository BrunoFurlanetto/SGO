# Generated by Django 4.0.1 on 2022-01-28 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0012_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(1, 'Janeiro'), (9, 'Setembro'), (10, 'Outubro'), (2, 'Fevereiro'), (4, 'Abril'), (7, 'Julho'), (11, 'Novembro'), (3, 'Março'), (8, 'Agosto'), (5, 'Maio'), (12, 'Dezembro'), (6, 'Junho')]),
        ),
    ]
