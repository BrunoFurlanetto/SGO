# Generated by Django 4.0.1 on 2022-04-24 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='professores',
            name='n_avaliacoes',
            field=models.IntegerField(default=0),
        ),
    ]
