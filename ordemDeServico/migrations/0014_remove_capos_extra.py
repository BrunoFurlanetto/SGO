
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordemDeServico', '0013_alter_dadostransporte_telefone_motorista'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemdeservico',
            name='data_preenchimento',
            field=models.DateField(default=datetime.date.today),
        ),

        migrations.RemoveField(
            model_name='ordemdeservico',
            name='data_preenchimento',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
