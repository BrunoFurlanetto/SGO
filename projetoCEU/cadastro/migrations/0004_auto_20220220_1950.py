# Generated by Django 3.2.9 on 2022-02-20 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0003_rename_nao_pode_ser_realizado_atividades_limitacao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='atividades',
            old_name='numero_de_participantes',
            new_name='numero_de_participantes_maximo',
        ),
        migrations.AddField(
            model_name='atividades',
            name='numero_de_participantes_minimo',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
