# Generated by Django 4.0.1 on 2022-05-20 17:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0005_disponibilidadehotelaria_disponibilidadeacampamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmpresaOnibus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viacao', models.CharField(max_length=255)),
                ('CNPJ', models.CharField(max_length=18, unique=True)),
                ('endereco', models.CharField(max_length=255)),
                ('bairro', models.CharField(max_length=255)),
                ('cidade', models.CharField(max_length=255)),
                ('estado', models.CharField(max_length=255)),
                ('cep', models.CharField(max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='disponibilidadeacampamento',
            name='mes',
            field=models.IntegerField(choices=[(9, 'Setembro'), (5, 'Maio'), (10, 'Outubro'), (7, 'Julho'), (12, 'Dezembro'), (6, 'Junho'), (8, 'Agosto'), (11, 'Novembro'), (2, 'Fevereiro'), (1, 'Janeiro'), (4, 'Abril'), (3, 'Março')]),
        ),
        migrations.AlterField(
            model_name='disponibilidadehotelaria',
            name='mes',
            field=models.IntegerField(choices=[(9, 'Setembro'), (5, 'Maio'), (10, 'Outubro'), (7, 'Julho'), (12, 'Dezembro'), (6, 'Junho'), (8, 'Agosto'), (11, 'Novembro'), (2, 'Fevereiro'), (1, 'Janeiro'), (4, 'Abril'), (3, 'Março')]),
        ),
        migrations.AddField(
            model_name='informacoesadcionais',
            name='viacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='peraltas.empresaonibus'),
        ),
    ]