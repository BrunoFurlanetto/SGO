# Generated by Django 4.0.1 on 2022-02-02 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0016_ordemdeservico_entregue'),
    ]

    operations = [
        migrations.AddField(
            model_name='professores',
            name='diarista',
            field=models.BooleanField(default=False),
        ),
    ]
