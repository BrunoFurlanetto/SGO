# Generated by Django 4.0.1 on 2022-06-19 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0024_informacoesadcionais_lista_segurados_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prereserva',
            name='ficha_evento',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='disponibilidadeacampamento',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (9, 'Setembro'), (6, 'Junho'), (11, 'Novembro'), (3, 'Março'), (2, 'Fevereiro'), (7, 'Julho'), (12, 'Dezembro'), (5, 'Maio'), (10, 'Outubro'), (1, 'Janeiro'), (8, 'Agosto')]),
        ),
        migrations.AlterField(
            model_name='disponibilidadehotelaria',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (9, 'Setembro'), (6, 'Junho'), (11, 'Novembro'), (3, 'Março'), (2, 'Fevereiro'), (7, 'Julho'), (12, 'Dezembro'), (5, 'Maio'), (10, 'Outubro'), (1, 'Janeiro'), (8, 'Agosto')]),
        ),
    ]
