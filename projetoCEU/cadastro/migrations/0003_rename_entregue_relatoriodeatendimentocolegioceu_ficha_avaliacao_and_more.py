# Generated by Django 4.0.1 on 2022-05-21 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0002_relatoriodeatendimentocolegioceu_ficaa_avaliacao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='relatoriodeatendimentocolegioceu',
            old_name='entregue',
            new_name='ficha_avaliacao',
        ),
        migrations.RemoveField(
            model_name='relatoriodeatendimentocolegioceu',
            name='ficaa_avaliacao',
        ),
    ]
