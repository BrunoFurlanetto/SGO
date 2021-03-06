# Generated by Django 4.0.1 on 2022-05-22 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0042_alter_disponibilidade_mes'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaLimite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_limite', models.PositiveIntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='disponibilidade',
            name='mes',
            field=models.IntegerField(choices=[(11, 'Novembro'), (10, 'Outubro'), (5, 'Maio'), (12, 'Dezembro'), (4, 'Abril'), (2, 'Fevereiro'), (7, 'Julho'), (6, 'Junho'), (1, 'Janeiro'), (8, 'Agosto'), (9, 'Setembro'), (3, 'Março')]),
        ),
    ]
