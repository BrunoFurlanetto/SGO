# Generated by Django 3.2.9 on 2022-01-12 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichaAvaliacao', '0013_auto_20220111_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='n_alunos',
            field=models.IntegerField(max_length=4),
        ),
    ]