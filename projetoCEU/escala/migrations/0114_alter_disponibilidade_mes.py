# Generated by Django 4.0.1 on 2022-04-03 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0113_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(11, 'Novembro'), (10, 'Outubro'), (4, 'Abril'), (5, 'Maio'), (8, 'Agosto'), (6, 'Junho'), (9, 'Setembro'), (1, 'Janeiro'), (7, 'Julho'), (12, 'Dezembro'), (3, 'Março'), (2, 'Fevereiro')]),
        ),
    ]