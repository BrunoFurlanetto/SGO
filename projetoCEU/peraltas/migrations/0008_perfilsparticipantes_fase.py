# Generated by Django 4.0.1 on 2022-03-19 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peraltas', '0007_remove_fichadeevento_cargo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilsparticipantes',
            name='fase',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
