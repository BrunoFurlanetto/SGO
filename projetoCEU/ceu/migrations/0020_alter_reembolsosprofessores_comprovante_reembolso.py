# Generated by Django 4.0.1 on 2022-04-30 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0019_alter_reembolsosprofessores_comprovante_reembolso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reembolsosprofessores',
            name='comprovante_reembolso',
            field=models.FileField(upload_to='comprovantes/[(<django.db.models.fields.BigAutoField: id>, <django.db.models.fields.related.ForeignKey>)]/%Y/%m'),
        ),
    ]
