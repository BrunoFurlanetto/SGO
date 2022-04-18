# Generated by Django 4.0.1 on 2022-04-17 20:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('peraltas', '0051_alter_fichadeevento_perfil_participantes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monitor',
            name='nome',
        ),
        migrations.RemoveField(
            model_name='vendedor',
            name='nome_vendedor',
        ),
        migrations.AddField(
            model_name='monitor',
            name='nota',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='monitor',
            name='telefone',
            field=models.CharField(default=0, max_length=11),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='monitor',
            name='usuario',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vendedor',
            name='nota',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='vendedor',
            name='telefone',
            field=models.CharField(default=0, max_length=11),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vendedor',
            name='usuario',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='fichadeevento',
            name='perfil_participantes',
            field=models.ManyToManyField(blank=True, to='peraltas.PerfilsParticipantes'),
        ),
    ]
