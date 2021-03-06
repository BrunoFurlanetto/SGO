# Generated by Django 4.0.1 on 2022-04-21 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Estruturas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estrutura', models.CharField(max_length=100)),
                ('locavel', models.BooleanField(default=False)),
                ('lotacao', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Limitacoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limitacao', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Professores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefone', models.CharField(max_length=11)),
                ('diarista', models.BooleanField(default=False)),
                ('nota', models.FloatField(default=0.0)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Locaveis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ceu.estruturas')),
            ],
        ),
        migrations.CreateModel(
            name='Atividades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atividade', models.CharField(max_length=100)),
                ('numero_de_participantes_minimo', models.IntegerField()),
                ('numero_de_participantes_maximo', models.IntegerField()),
                ('duracao', models.DurationField()),
                ('publico', models.BooleanField(default=False)),
                ('limitacao', models.ManyToManyField(to='ceu.Limitacoes')),
                ('local_da_atividade', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='local', to='ceu.estruturas')),
            ],
        ),
    ]
