# Generated by Django 4.0.1 on 2022-04-30 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0003_atividades_n_avaliacoes_atividades_nota'),
    ]

    operations = [
        migrations.CreateModel(
            name='Valores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_atividade', models.FloatField(default=0.0)),
                ('valor_diaria', models.FloatField(default=0.0)),
            ],
        ),
    ]
