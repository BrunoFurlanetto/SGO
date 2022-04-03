# Generated by Django 4.0.1 on 2022-04-03 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0049_remove_informacoesadcionais_atividades_ceu_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientecolegio',
            name='responsavel_evento',
        ),
        migrations.RemoveField(
            model_name='responsavel',
            name='responsavel_por',
        ),
        migrations.CreateModel(
            name='RelacaoClienteResponsavel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peraltas.clientecolegio')),
                ('responsavel', models.ManyToManyField(to='peraltas.Responsavel')),
            ],
        ),
    ]
