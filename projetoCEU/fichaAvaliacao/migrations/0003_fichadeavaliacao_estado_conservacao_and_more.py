# Generated by Django 4.0.1 on 2022-04-24 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichaAvaliacao', '0002_rename_email_educador_1_fichadeavaliacao_email_avaliador_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichadeavaliacao',
            name='estado_conservacao',
            field=models.IntegerField(choices=[(5, 'Excelente'), (4, 'Ótimo'), (3, 'Bom'), (2, 'Regular'), (1, 'Ruim')], default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fichadeavaliacao',
            name='o_que_quer_proxima',
            field=models.TextField(blank=True),
        ),
    ]
