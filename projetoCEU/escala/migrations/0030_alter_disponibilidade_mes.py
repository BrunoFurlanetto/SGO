# Generated by Django 4.0.1 on 2022-04-30 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0029_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (8, 'Agosto'), (5, 'Maio'), (2, 'Fevereiro'), (3, 'Março'), (12, 'Dezembro'), (7, 'Julho'), (9, 'Setembro'), (4, 'Abril'), (10, 'Outubro'), (1, 'Janeiro'), (11, 'Novembro')]),
        ),
    ]
