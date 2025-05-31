from datetime import datetime, timedelta

from orcamento.models import Orcamento, StatusOrcamento


def verificar_validade_orcamento():
    orcamentos = Orcamento.objects.filter(
        data_vencimento=datetime.today().date() - timedelta(days=1),
    ).filter(
        status_orcamento__orcamento_vencido=False,
        status_orcamento__aprovacao_cliente=False,
        status_orcamento__negado_cliente=False,
    ).update(
        status_orcamento=StatusOrcamento.objects.get(orcamento_vencido=True)
    )


def excluir_previas_antigas():
    Orcamento.objects.filter(previa=True, data_ultima_edicao__date__lt=datetime.today().date() - timedelta(days=90)).delete()
