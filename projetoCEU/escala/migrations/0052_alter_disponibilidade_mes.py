# Generated by Django 4.0.1 on 2022-05-28 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0051_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (1, 'Janeiro'), (2, 'Fevereiro'), (12, 'Dezembro'), (10, 'Outubro'), (7, 'Julho'), (3, 'Março'), (9, 'Setembro'), (11, 'Novembro'), (5, 'Maio'), (4, 'Abril'), (8, 'Agosto')]),
        ),
    ]
