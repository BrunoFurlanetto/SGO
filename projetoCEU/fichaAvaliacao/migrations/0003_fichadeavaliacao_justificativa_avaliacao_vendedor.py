# Generated by Django 3.2.9 on 2022-01-07 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichaAvaliacao', '0002_remove_fichadeavaliacao_justificativa_avaliacao_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichadeavaliacao',
            name='justificativa_avaliacao_vendedor',
            field=models.TextField(default=0, max_length=300),
            preserve_default=False,
        ),
    ]
