# Generated by Django 3.2.9 on 2022-01-12 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichaAvaliacao', '0012_alter_fichadeavaliacao_data_preenchimento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='data_preenchimento',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='observacoes',
            field=models.TextField(max_length=400),
        ),
    ]
