# Generated by Django 4.0.1 on 2022-04-24 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0007_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(5, 'Maio'), (3, 'Março'), (12, 'Dezembro'), (11, 'Novembro'), (1, 'Janeiro'), (10, 'Outubro'), (7, 'Julho'), (8, 'Agosto'), (4, 'Abril'), (2, 'Fevereiro'), (6, 'Junho'), (9, 'Setembro')]),
        ),
    ]