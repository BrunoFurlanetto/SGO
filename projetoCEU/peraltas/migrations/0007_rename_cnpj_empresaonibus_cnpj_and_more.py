# Generated by Django 4.0.1 on 2022-05-20 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0006_empresaonibus_alter_disponibilidadeacampamento_mes_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='empresaonibus',
            old_name='CNPJ',
            new_name='cnpj',
        ),
        migrations.AlterField(
            model_name='disponibilidadeacampamento',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (4, 'Abril'), (9, 'Setembro'), (12, 'Dezembro'), (1, 'Janeiro'), (11, 'Novembro'), (5, 'Maio'), (3, 'Março'), (7, 'Julho'), (8, 'Agosto'), (2, 'Fevereiro'), (10, 'Outubro')]),
        ),
        migrations.AlterField(
            model_name='disponibilidadehotelaria',
            name='mes',
            field=models.IntegerField(choices=[(6, 'Junho'), (4, 'Abril'), (9, 'Setembro'), (12, 'Dezembro'), (1, 'Janeiro'), (11, 'Novembro'), (5, 'Maio'), (3, 'Março'), (7, 'Julho'), (8, 'Agosto'), (2, 'Fevereiro'), (10, 'Outubro')]),
        ),
    ]
