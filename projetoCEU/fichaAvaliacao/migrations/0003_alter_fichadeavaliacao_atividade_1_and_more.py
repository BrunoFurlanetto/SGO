# Generated by Django 4.0.1 on 2022-01-14 14:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0015_ordemdeservico_solicitado'),
        ('fichaAvaliacao', '0002_alter_fichadeavaliacao_data_preenchimento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='atividade_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_1', to='cadastro.atividades'),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='avaliacao_professor_1',
            field=models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='data_atividade_1',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='instituicao',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='fichadeavaliacao',
            name='professor_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_1', to='cadastro.professores'),
        ),
    ]