from django.shortcuts import render

from financeiro.models import CadastroFichaFinanceira, CadastroDadosEvento, CadastroDadosPagamento, \
    CadastroPlanosPagamento, CadastroNotaFiscal
from orcamento.models import Orcamento


def ficha_financeira(request, id_orcamento):
    orcamento = Orcamento.objects.get(pk=id_orcamento)
    cadastro_ficha_financeira = CadastroFichaFinanceira(initial=orcamento.dados_iniciais())
    cadastro_dados_evento = CadastroDadosEvento(initial=orcamento.dados_iniciais())
    cadastro_dados_pagamento = CadastroDadosPagamento(initial=orcamento.dados_iniciais())
    cadastro_planos_pagamento = CadastroPlanosPagamento(initial=orcamento.dados_iniciais())
    cadastro_nota_fiscal = CadastroNotaFiscal(initial=orcamento.dados_iniciais())

    return render(request, 'financeiro/ficha_financeira.html', {
        'orcamento': orcamento,
        'ficha_financeira': cadastro_ficha_financeira,
        'dados_evento': cadastro_dados_evento,
        'dados_pagamento': cadastro_dados_pagamento,
        'planos_pagamento': cadastro_planos_pagamento,
        'nota_fiscal': cadastro_nota_fiscal,
    })
