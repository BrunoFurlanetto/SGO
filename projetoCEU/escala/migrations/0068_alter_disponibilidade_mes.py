# Generated by Django 4.0.1 on 2022-03-21 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0067_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (12, 'Dezembro'), (2, 'Fevereiro'), (5, 'Maio'), (1, 'Janeiro'), (8, 'Agosto'), (9, 'Setembro'), (11, 'Novembro'), (7, 'Julho'), (3, 'Março'), (10, 'Outubro'), (4, 'Abril')]),
        ),
    ]