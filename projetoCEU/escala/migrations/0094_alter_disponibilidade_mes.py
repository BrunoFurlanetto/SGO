# Generated by Django 4.0.1 on 2022-03-27 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0093_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(5, 'Maio'), (1, 'Janeiro'), (12, 'Dezembro'), (2, 'Fevereiro'), (7, 'Julho'), (3, 'Março'), (4, 'Abril'), (10, 'Outubro'), (9, 'Setembro'), (11, 'Novembro'), (6, 'Junho'), (8, 'Agosto')]),
        ),
    ]
