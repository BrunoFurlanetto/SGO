# Generated by Django 3.2.9 on 2022-02-20 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0002_limitacoes_limitacao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='atividades',
            old_name='nao_pode_ser_realizado',
            new_name='limitacao',
        ),
    ]