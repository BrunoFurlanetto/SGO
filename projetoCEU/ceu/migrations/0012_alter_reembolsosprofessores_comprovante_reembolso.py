# Generated by Django 4.0.1 on 2022-04-30 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0011_alter_reembolsosprofessores_comprovante_reembolso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reembolsosprofessores',
            name='comprovante_reembolso',
            field=models.FileField(upload_to='comprovantes/None_id/%Y/%m'),
        ),
    ]
