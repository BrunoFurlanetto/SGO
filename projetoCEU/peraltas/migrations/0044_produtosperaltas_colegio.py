# Generated by Django 4.0.1 on 2022-04-01 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0043_fichadeevento_qtd_meninas_fichadeevento_qtd_meninos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='produtosperaltas',
            name='colegio',
            field=models.BooleanField(default=True),
        ),
    ]
