# Generated by Django 4.0.1 on 2022-06-23 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0026_remove_informacoesadcionais_outros_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='biologo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monitor',
            name='fotos_e_filmagens',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monitor',
            name='som',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monitor',
            name='tecnica',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monitor',
            name='video',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='disponibilidadeacampamento',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (2, 'Fevereiro'), (8, 'Agosto'), (4, 'Abril'), (7, 'Julho'), (9, 'Setembro'), (6, 'Junho'), (1, 'Janeiro'), (3, 'Março'), (12, 'Dezembro'), (11, 'Novembro'), (5, 'Maio')]),
        ),
        migrations.AlterField(
            model_name='disponibilidadehotelaria',
            name='mes',
            field=models.IntegerField(choices=[(10, 'Outubro'), (2, 'Fevereiro'), (8, 'Agosto'), (4, 'Abril'), (7, 'Julho'), (9, 'Setembro'), (6, 'Junho'), (1, 'Janeiro'), (3, 'Março'), (12, 'Dezembro'), (11, 'Novembro'), (5, 'Maio')]),
        ),
    ]
