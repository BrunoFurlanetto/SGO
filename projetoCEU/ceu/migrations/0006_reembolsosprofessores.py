# Generated by Django 4.0.1 on 2022-04-30 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ceu', '0005_rename_valor_atividade_valores_valor_pago_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReembolsosProfessores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes_referente', models.IntegerField()),
                ('ano_referente', models.IntegerField()),
                ('valor_reembolso', models.FloatField()),
                ('comprovante_reembolso', models.FileField(upload_to='comprovantes/<django.db.models.fields.related.ForeignKey>/%Y/%m')),
                ('usuario_professor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ceu.professores')),
            ],
        ),
    ]
