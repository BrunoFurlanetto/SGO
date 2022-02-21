# Generated by Django 4.0.1 on 2022-02-21 14:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cadastro', '0005_rename_ordemdeservico_relatoriodeatendimentoceu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professores',
            name='email',
        ),
        migrations.RemoveField(
            model_name='professores',
            name='primeiro_nome',
        ),
        migrations.RemoveField(
            model_name='professores',
            name='sobrenome',
        ),
        migrations.AlterField(
            model_name='professores',
            name='usuario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='relatoriodeatendimentoceu',
            name='locacoes',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
