# Generated by Django 4.0.1 on 2022-03-27 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0092_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(7, 'Julho'), (10, 'Outubro'), (12, 'Dezembro'), (8, 'Agosto'), (11, 'Novembro'), (5, 'Maio'), (1, 'Janeiro'), (3, 'Março'), (2, 'Fevereiro'), (9, 'Setembro'), (6, 'Junho'), (4, 'Abril')]),
        ),
    ]