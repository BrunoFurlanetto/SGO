# Generated by Django 3.2.9 on 2021-12-30 02:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0014_alter_ordemdeservico_coordenador'),
        ('escala', '0002_alter_escala_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='escala',
            name='escalados',
        ),
        migrations.AddField(
            model_name='escala',
            name='coordenador',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, related_name='coordenador_escala', to='cadastro.professores'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='escala',
            name='professor_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='professor_2_escala', to='cadastro.professores'),
        ),
        migrations.AddField(
            model_name='escala',
            name='professor_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='professor_3_escala', to='cadastro.professores'),
        ),
        migrations.AddField(
            model_name='escala',
            name='professor_4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='professor_4_escala', to='cadastro.professores'),
        ),
        migrations.AlterField(
            model_name='escala',
            name='data',
            field=models.DateField(default=datetime.datetime(2021, 12, 29, 23, 1, 15, 369371)),
        ),
    ]
