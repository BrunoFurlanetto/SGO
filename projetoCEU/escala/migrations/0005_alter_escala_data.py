# Generated by Django 3.2.9 on 2021-12-30 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escala', '0004_alter_escala_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escala',
            name='data',
            field=models.DateField(),
        ),
    ]