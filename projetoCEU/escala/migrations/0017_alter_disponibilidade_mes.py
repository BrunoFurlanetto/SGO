# Generated by Django 4.0.1 on 2022-02-26 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0016_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(12, 'Dezembro'), (10, 'Outubro'), (8, 'Agosto'), (5, 'Maio'), (2, 'Fevereiro'), (9, 'Setembro'), (6, 'Junho'), (1, 'Janeiro'), (11, 'Novembro'), (7, 'Julho'), (3, 'Março'), (4, 'Abril')]),
        ),
    ]
