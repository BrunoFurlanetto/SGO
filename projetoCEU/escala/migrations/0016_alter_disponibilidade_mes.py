# Generated by Django 4.0.1 on 2022-02-02 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0015_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (3, 'Março'), (11, 'Novembro'), (8, 'Agosto'), (4, 'Abril'), (9, 'Setembro'), (7, 'Julho'), (1, 'Janeiro'), (2, 'Fevereiro'), (10, 'Outubro'), (5, 'Maio'), (12, 'Dezembro')]),
        ),
    ]
