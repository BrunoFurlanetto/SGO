# Generated by Django 4.0.1 on 2022-03-07 20:14

from django.db import migrations, models
import json


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0004_alter_relatoriodeatendimentopublicoceu_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatoriodeatendimentopublicoceu',
            name='equipe',
            field=models.JSONField(blank=True, decoder=json.loads),
        ),
    ]
