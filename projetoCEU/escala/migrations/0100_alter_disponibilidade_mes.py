# Generated by Django 4.0.1 on 2022-03-30 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0099_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (5, 'Maio'), (10, 'Outubro'), (6, 'Junho'), (3, 'Março'), (11, 'Novembro'), (7, 'Julho'), (9, 'Setembro'), (2, 'Fevereiro'), (12, 'Dezembro'), (1, 'Janeiro'), (8, 'Agosto')]),
        ),
    ]
