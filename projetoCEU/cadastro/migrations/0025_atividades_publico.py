# Generated by Django 4.0.1 on 2022-02-06 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0024_alter_ordemdeservico_coordenador'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividades',
            name='publico',
            field=models.BooleanField(default=False),
        ),
    ]
