import hashlib
from datetime import datetime, timedelta

from orcamento.models import ValoresPadrao


def campos_necessarios_aprovacao(orcamento):
    def valor_padrao():
        if campo != 'data_pagamento':
            try:
                return float(ValoresPadrao.objects.get(id_taxa=campo).valor)
            except ValoresPadrao.DoesNotExist:
                return 0.00
        else:
            return (orcamento.data_preenchimento + timedelta(days=int(ValoresPadrao.objects.get(id_taxa=campo).valor))).strftime('%d/%m/%Y')

    def valor_tratativa():
        if campo != 'data_pagamento':
            print(gerencia[campo])
            return gerencia[campo]
        else:
            return datetime.strptime(gerencia[campo], '%Y-%m-%d').strftime('%d/%m/%Y')

    alteraveis_gerencia = ['comissao', 'taxa_comercial', 'minimo_onibus', 'data_pagamento', 'desconto_geral']
    campos_alterados = {'pedidos': [], 'opcionais': []}
    gerencia = orcamento.objeto_gerencia
    valor_op = 0

    for campo in alteraveis_gerencia:
        if gerencia[f'{campo}_alterado']:
            campo_split = campo.split('_')
            verbose = f'{campo_split[0].capitalize()} {campo_split[1].capitalize()}' if len(campo_split) > 1 else campo_split[0].capitalize()
            campos_alterados['pedidos'].append({
                'campo': campo,
                'valor_tratativa': valor_tratativa(),
                'valor_padrao': valor_padrao(),
                'verbose': verbose,
            })

    for op in orcamento.objeto_orcamento['descricao_opcionais']:
        try:
            campos_alterados['outros'] = op['outros']
        except KeyError:
            campos_alterados['outros'] = []
        else:
            for op_extra in op['outros']:
                valor_op += op_extra['valor']
    print(valor_op)
    try:
        if len(orcamento.opcionais_extra) > 0:
            soma_opcionais = 0

            for opcional in orcamento.opcionais_extra:
                campos_alterados['opcionais'].append(opcional)
    except TypeError:
        ...

    campos_alterados['observacoes'] = gerencia['observacoes_gerencia']
    campos_alterados['valor_com_desconto'] = float(orcamento.valor)
    campos_alterados['valores_padrao'] = ValoresPadrao.listar_valores()
    campos_alterados['valor_base'] = orcamento.objeto_orcamento['total']['valor'] - valor_op
    campos_alterados['id_orcamento'] = orcamento.id

    return campos_alterados
