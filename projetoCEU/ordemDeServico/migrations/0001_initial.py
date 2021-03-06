# Generated by Django 4.0.1 on 2022-04-21 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('peraltas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdemDeServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('Colégio', 'Colégio'), ('Empresa', 'Empresa')], max_length=7)),
                ('instituicao', models.CharField(max_length=300)),
                ('cidade', models.CharField(max_length=255)),
                ('check_in', models.DateTimeField()),
                ('check_out', models.DateTimeField()),
                ('n_participantes', models.IntegerField()),
                ('serie', models.CharField(blank=True, max_length=255, null=True)),
                ('n_professores', models.IntegerField(blank=True, null=True)),
                ('responsavel_grupo', models.CharField(max_length=255)),
                ('empresa', models.CharField(choices=[('Peraltas', 'Peraltas'), ('CEU', 'Fundação CEU')], max_length=15)),
                ('check_in_ceu', models.DateTimeField(blank=True, null=True)),
                ('check_out_ceu', models.DateTimeField(blank=True, null=True)),
                ('atividades_ceu', models.JSONField(blank=True, null=True)),
                ('locacao_ceu', models.JSONField(blank=True, null=True)),
                ('cronograma_peraltas', models.FileField(blank=True, upload_to='cronogramas/%Y/%m/%d')),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('relatorio_ceu_entregue', models.BooleanField(default=False)),
                ('atividades_eco', models.ManyToManyField(blank=True, to='peraltas.AtividadesEco')),
                ('atividades_peraltas', models.ManyToManyField(blank=True, to='peraltas.AtividadePeraltas')),
                ('ficha_de_evento', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='peraltas.fichadeevento')),
                ('monitor_responsavel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='peraltas.monitor')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='peraltas.vendedor')),
            ],
        ),
    ]
