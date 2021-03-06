# Generated by Django 4.0.1 on 2022-06-09 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0022_prereserva_agendado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disponibilidadeacampamento',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (6, 'Junho'), (7, 'Julho'), (2, 'Fevereiro'), (1, 'Janeiro'), (4, 'Abril'), (5, 'Maio'), (8, 'Agosto'), (9, 'Setembro'), (11, 'Novembro'), (12, 'Dezembro'), (3, 'Março')]),
        ),
        migrations.AlterField(
            model_name='disponibilidadehotelaria',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (6, 'Junho'), (7, 'Julho'), (2, 'Fevereiro'), (1, 'Janeiro'), (4, 'Abril'), (5, 'Maio'), (8, 'Agosto'), (9, 'Setembro'), (11, 'Novembro'), (12, 'Dezembro'), (3, 'Março')]),
        ),
        migrations.AlterField(
            model_name='prereserva',
            name='observacoes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
