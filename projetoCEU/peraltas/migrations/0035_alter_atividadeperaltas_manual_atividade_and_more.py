# Generated by Django 4.0.1 on 2022-07-21 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0034_rename_atividade_atividadeseco_nome_atividade_eco_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atividadeperaltas',
            name='manual_atividade',
            field=models.FileField(blank=True, upload_to='manuais_atividades_acampamento/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='atividadeseco',
            name='manual_atividade',
            field=models.FileField(blank=True, upload_to='manuais_atividades_eco/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='disponibilidadeacampamento',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (8, 'Agosto'), (1, 'Janeiro'), (5, 'Maio'), (6, 'Junho'), (9, 'Setembro'), (10, 'Outubro'), (7, 'Julho'), (11, 'Novembro'), (3, 'Março'), (12, 'Dezembro'), (2, 'Fevereiro')]),
        ),
        migrations.AlterField(
            model_name='disponibilidadehotelaria',
            name='mes',
            field=models.IntegerField(choices=[(4, 'Abril'), (8, 'Agosto'), (1, 'Janeiro'), (5, 'Maio'), (6, 'Junho'), (9, 'Setembro'), (10, 'Outubro'), (7, 'Julho'), (11, 'Novembro'), (3, 'Março'), (12, 'Dezembro'), (2, 'Fevereiro')]),
        ),
    ]
