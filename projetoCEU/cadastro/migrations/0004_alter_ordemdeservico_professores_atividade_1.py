# Generated by Django 3.2.9 on 2021-12-08 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0003_alter_ordemdeservico_professores_atividade_1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemdeservico',
            name='professores_atividade_1',
            field=models.JSONField(),
        ),
    ]
