# Generated by Django 4.0.1 on 2022-03-19 21:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0009_alter_perfilsparticipantes_ano'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichadeevento',
            name='codigos_app',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='peraltas.codigosapp'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fichadeevento',
            name='vendedora',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='peraltas.vendedor'),
        ),
    ]
