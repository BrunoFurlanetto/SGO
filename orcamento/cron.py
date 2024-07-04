from datetime import datetime, timedelta

from orcamento.models import Orcamento, StatusOrcamento


def verificar_validade_orcamento():
    orcamentos = Orcamento.objects.filter(data_vencimento=datetime.today().date() - timedelta(days=1))

    for orcamento in orcamentos:
        if 'aberto' in orcamento.status_orcamento.status.lower() or 'analise' in orcamento.status_orcamento.status.lower():
            status = StatusOrcamento.objects.get(status__icontains='vencido')
            orcamento.status_orcamento = status
            orcamento.save()


def excluir_previas_antigas():
    Orcamento.objects.filter(previa=True, data_ultima_edicao__lt=datetime.today().date() - timedelta(days=90)).delete()
