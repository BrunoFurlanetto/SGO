# Generated by Django 4.0.1 on 2022-02-06 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0023_alter_ordemdeservico_coordenador'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemdeservico',
            name='coordenador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='coordenador', to='cadastro.professores'),
        ),
    ]
