# Generated by Django 4.0.1 on 2022-03-17 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0048_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(8, 'Agosto'), (1, 'Janeiro'), (11, 'Novembro'), (12, 'Dezembro'), (10, 'Outubro'), (5, 'Maio'), (7, 'Julho'), (4, 'Abril'), (9, 'Setembro'), (3, 'Março'), (6, 'Junho'), (2, 'Fevereiro')]),
        ),
    ]
