# Generated by Django 4.0.1 on 2022-03-07 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0003_relatoriodeatendimentocolegioceu_tipo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatoriodeatendimentopublicoceu',
            name='tipo',
            field=models.CharField(blank=True, default='Público', max_length=7),
        ),
    ]
