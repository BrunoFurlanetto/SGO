# Generated by Django 4.0.1 on 2022-04-30 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0018_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (2, 'Fevereiro'), (8, 'Agosto'), (5, 'Maio'), (12, 'Dezembro'), (7, 'Julho'), (3, 'Março'), (4, 'Abril'), (11, 'Novembro'), (9, 'Setembro'), (1, 'Janeiro'), (10, 'Outubro')]),
        ),
    ]
