# Generated by Django 4.0.1 on 2022-07-17 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0063_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(12, 'Dezembro'), (3, 'Março'), (7, 'Julho'), (9, 'Setembro'), (1, 'Janeiro'), (10, 'Outubro'), (6, 'Junho'), (4, 'Abril'), (2, 'Fevereiro'), (8, 'Agosto'), (11, 'Novembro'), (5, 'Maio')]),
        ),
    ]
