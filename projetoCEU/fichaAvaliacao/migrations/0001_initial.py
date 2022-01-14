# Generated by Django 4.0.1 on 2022-01-14 14:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cadastro', '0015_ordemdeservico_solicitado'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichaDeAvaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instituicao', models.CharField(max_length=400)),
                ('cidade', models.CharField(max_length=300)),
                ('n_alunos', models.IntegerField(default=0)),
                ('n_educadores', models.IntegerField(default=0)),
                ('serie', models.CharField(max_length=300)),
                ('nome_educador_1', models.CharField(max_length=400)),
                ('cargo_educador_1', models.CharField(max_length=400)),
                ('email_educador_1', models.EmailField(max_length=254)),
                ('nome_educador_2', models.CharField(blank=True, max_length=400, null=True)),
                ('cargo_educador_2', models.CharField(blank=True, max_length=400, null=True)),
                ('email_educador_2', models.EmailField(blank=True, max_length=254, null=True)),
                ('nome_vendedor', models.CharField(blank=True, max_length=400, null=True)),
                ('avaliacao_vendedor', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('justificativa_avaliacao_vendedor', models.TextField(max_length=300)),
                ('data_atividade_1', models.DateField(default=django.utils.timezone.now)),
                ('avaliacao_atividade_1', models.CharField(choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('data_atividade_2', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_2', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('data_atividade_3', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_3', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('data_atividade_4', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_4', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('data_atividade_5', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_5', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('data_atividade_6', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_6', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('data_atividade_7', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_7', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('data_atividade_8', models.DateField(blank=True, null=True)),
                ('avaliacao_atividade_8', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10, null=True)),
                ('justificativa_avaliacao_atividades', models.TextField(max_length=400)),
                ('avaliacao_professor_1', models.CharField(choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('avaliacao_professor_2', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('avaliacao_professor_3', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('avaliacao_professor_4', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('avaliacao_professor_5', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('avaliacao_professor_6', models.CharField(blank=True, choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('justificativa_avaliacao_professores', models.TextField(max_length=400)),
                ('motivo_trazer_grupo', models.TextField(max_length=400)),
                ('avaliacao_conteudo_pedagogico', models.CharField(choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('limpeza_instalacoes', models.CharField(choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('estado_jardim', models.CharField(choices=[('', ''), ('Excelente', 'Excelente'), ('Ótimo', 'Ótimo'), ('Bom', 'Bom'), ('Regular', 'Regular'), ('Ruim', 'Ruim')], max_length=10)),
                ('observacoes', models.TextField(max_length=400)),
                ('data_preenchimento', models.DateField(default=django.utils.timezone.now)),
                ('atividade_1', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_1', to='cadastro.atividades')),
                ('atividade_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_2', to='cadastro.atividades')),
                ('atividade_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_3', to='cadastro.atividades')),
                ('atividade_4', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_4', to='cadastro.atividades')),
                ('atividade_5', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_5', to='cadastro.atividades')),
                ('atividade_6', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_6', to='cadastro.atividades')),
                ('atividade_7', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_7', to='cadastro.atividades')),
                ('atividade_8', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_atividade_8', to='cadastro.atividades')),
                ('professor_1', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_1', to='cadastro.professores')),
                ('professor_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_2', to='cadastro.professores')),
                ('professor_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_3', to='cadastro.professores')),
                ('professor_4', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_4', to='cadastro.professores')),
                ('professor_5', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_5', to='cadastro.professores')),
                ('professor_6', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='avaliacao_professor_6', to='cadastro.professores')),
            ],
        ),
    ]
