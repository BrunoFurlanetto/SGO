# Generated by Django 4.0.1 on 2022-03-07 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0008_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(12, 'Dezembro'), (11, 'Novembro'), (5, 'Maio'), (8, 'Agosto'), (3, 'Março'), (1, 'Janeiro'), (4, 'Abril'), (2, 'Fevereiro'), (6, 'Junho'), (7, 'Julho'), (10, 'Outubro'), (9, 'Setembro')]),
        ),
    ]