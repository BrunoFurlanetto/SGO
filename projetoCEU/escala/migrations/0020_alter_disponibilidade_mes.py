# Generated by Django 4.0.1 on 2022-04-30 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0019_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(2, 'Fevereiro'), (10, 'Outubro'), (7, 'Julho'), (4, 'Abril'), (1, 'Janeiro'), (12, 'Dezembro'), (9, 'Setembro'), (5, 'Maio'), (6, 'Junho'), (3, 'Março'), (8, 'Agosto'), (11, 'Novembro')]),
        ),
    ]