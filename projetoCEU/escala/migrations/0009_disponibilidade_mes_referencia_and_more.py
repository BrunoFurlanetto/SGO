# Generated by Django 4.0.1 on 2022-01-24 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0008_disponibilidade'),
    ]

    operations = [
        migrations.AddField(
            model_name='disponibilidade',
            name='mes_referencia',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='disponibilidade',
            name='n_dias',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
