# Generated by Django 4.0.1 on 2022-04-30 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0008_alter_reembolsosprofessores_mes_referente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reembolsosprofessores',
            name='comprovante_reembolso',
            field=models.FileField(upload_to='comprovantes/<function ReembolsosProfessores.nome_completo at 0x000001B0BE341240>/%Y/%m'),
        ),
    ]
