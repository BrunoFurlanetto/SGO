# Generated by Django 4.0.1 on 2022-03-23 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0022_alter_informacoesadcionais_atividades_eco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informacoesadcionais',
            name='atividades_eco',
            field=models.ManyToManyField(blank=True, to='peraltas.AtividadesEco'),
        ),
        migrations.AlterField(
            model_name='responsavel',
            name='fone',
            field=models.IntegerField(),
        ),
    ]
