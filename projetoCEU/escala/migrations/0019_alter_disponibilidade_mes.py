# Generated by Django 3.2.9 on 2022-02-06 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0018_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(1, 'Janeiro'), (7, 'Julho'), (6, 'Junho'), (2, 'Fevereiro'), (8, 'Agosto'), (5, 'Maio'), (4, 'Abril'), (10, 'Outubro'), (3, 'Março'), (11, 'Novembro'), (12, 'Dezembro'), (9, 'Setembro')]),
        ),
    ]