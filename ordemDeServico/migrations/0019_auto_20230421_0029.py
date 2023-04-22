from django.db import migrations

from ordemDeServico.models import OrdemDeServico, DadosTransporte


def popular_dados_transporte_e_monitor_embarque(apps, schema_editor):
    ordens = OrdemDeServico.objects.all()

    for ordem in ordens:
        if ordem.dados_transporte:
            transporte = DadosTransporte.objects.get(id=ordem.dados_transporte.id)
            transporte.monitor_embarque = ordem.monitor_embarque
            transporte.save()
            ordem.dados_transporte_temp.set([ordem.dados_transporte.id])


class Migration(migrations.Migration):

    dependencies = [
        ('ordemDeServico', '0018_dadostransporte_monitor_embarque_and_more'),
    ]

    operations = [
        migrations.RunPython(popular_dados_transporte_e_monitor_embarque),
    ]
