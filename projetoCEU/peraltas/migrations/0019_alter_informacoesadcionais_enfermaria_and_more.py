# Generated by Django 4.0.1 on 2022-03-22 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0018_remove_responsavel_responsavel_por_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informacoesadcionais',
            name='enfermaria',
            field=models.IntegerField(blank=True, choices=[(1, 'Padrão'), (2, 'Garantia')], null=True),
        ),
        migrations.AlterField(
            model_name='responsavel',
            name='fone',
            field=models.IntegerField(max_length=11),
        ),
    ]