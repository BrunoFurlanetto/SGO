# Generated by Django 4.0.1 on 2022-03-21 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0070_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (12, 'Dezembro'), (2, 'Fevereiro'), (11, 'Novembro'), (5, 'Maio'), (7, 'Julho'), (3, 'Março'), (6, 'Junho'), (4, 'Abril'), (8, 'Agosto'), (9, 'Setembro'), (1, 'Janeiro')]),
        ),
    ]
