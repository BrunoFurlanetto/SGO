# Generated by Django 4.0.1 on 2022-07-09 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0060_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(12, 'Dezembro'), (1, 'Janeiro'), (5, 'Maio'), (10, 'Outubro'), (11, 'Novembro'), (9, 'Setembro'), (4, 'Abril'), (2, 'Fevereiro'), (3, 'Março'), (8, 'Agosto'), (7, 'Julho'), (6, 'Junho')]),
        ),
    ]
