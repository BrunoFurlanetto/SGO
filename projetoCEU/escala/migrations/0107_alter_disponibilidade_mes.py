# Generated by Django 4.0.1 on 2022-04-01 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0106_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(5, 'Maio'), (11, 'Novembro'), (7, 'Julho'), (10, 'Outubro'), (1, 'Janeiro'), (8, 'Agosto'), (9, 'Setembro'), (2, 'Fevereiro'), (12, 'Dezembro'), (6, 'Junho'), (3, 'Março'), (4, 'Abril')]),
        ),
    ]