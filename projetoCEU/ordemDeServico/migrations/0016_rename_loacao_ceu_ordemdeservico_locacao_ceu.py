# Generated by Django 4.0.1 on 2022-03-31 04:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ordemDeServico', '0015_alter_ordemdeservico_atividades_eco_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='loacao_ceu',
            new_name='locacao_ceu',
        ),
    ]