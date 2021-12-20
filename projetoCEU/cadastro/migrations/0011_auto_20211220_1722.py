# Generated by Django 3.2.9 on 2021-12-20 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0010_alter_ordemdeservico_soma_horas_1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='empresa_entrada_1',
            new_name='atividade_1_entrada_1',
        ),
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='empresa_entrada_2',
            new_name='atividade_1_entrada_2',
        ),
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='empresa_entrada_3',
            new_name='atividade_1_entrada_3',
        ),
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='empresa_saida_1',
            new_name='atividade_1_saida_1',
        ),
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='empresa_saida_2',
            new_name='atividade_1_saida_2',
        ),
        migrations.RenameField(
            model_name='ordemdeservico',
            old_name='empresa_saida_3',
            new_name='atividade_1_saida_3',
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_2_entrada_1',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_2_entrada_2',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_2_entrada_3',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_2_saida_1',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_2_saida_2',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_2_saida_3',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_3_entrada_1',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_3_entrada_2',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_3_entrada_3',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_3_saida_1',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_3_saida_2',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='atividade_3_saida_3',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='soma_horas_2',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='soma_horas_3',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ordemdeservico',
            name='soma_horas_1',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
