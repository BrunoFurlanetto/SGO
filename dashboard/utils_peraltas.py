import hashlib
from datetime import datetime, timedelta


def campos_necessarios_aprovacao(orcamento):
    gerencia_default = {
        "desconto_produto": [0.0, 'Desconto no produto'],
        "desconto_monitoria": [0.0, 'Desconto na monitoria'],
        "desconto_trasnporte": [0.0, 'Desconto no transporte'],
        "desconto_geral": [0.0, 'Desconto geral'],
        "observacoes_desconto": ["", 'observacoes'],
        "comissao": [9.0, 'Comissão de vendas'],
        "taxa_comercial": [5.0, 'Taxa comercial'],
        "minimo_onibus": [30.0, 'Mínimo no ônibus'],
        "data_pagamento": [(orcamento.data_preenchimento + timedelta(days=15)).strftime('%d/%m/%Y'), 'Data de pagamento']
    }

    campos_alterados = {'pedidos': [], 'opcionais': []}
    gerencia = orcamento.objeto_gerencia

    for chave in gerencia_default:
        if chave != 'data_pagamento' and (gerencia_default[chave][0] != gerencia[chave]):
            campos_alterados['pedidos'].append({
                gerencia_default[chave][1]: [gerencia[chave], gerencia_default[chave][0], chave]
            })
        elif chave == 'data_pagamento':
            data_pagamento = datetime.strptime(gerencia[chave], '%Y-%m-%d').strftime('%d/%m/%Y')

            if data_pagamento != gerencia_default[chave][1]:
                campos_alterados['pedidos'].append({
                    gerencia_default[chave][1]: [data_pagamento, gerencia_default[chave][0], chave]
                })

    campos_alterados['observacoes'] = gerencia['observacoes_desconto']
    campos_alterados['valor_com_desconto'] = float(orcamento.valor)
    campos_alterados['valor_sem_desconto'] = orcamento.objeto_orcamento['total']['valor']
    campos_alterados['valor_base'] = orcamento.objeto_orcamento['total']['valor_base']
    campos_alterados['opcionais'] = verifricar_descontos_opcionais(orcamento.objeto_orcamento['descricao_opcionais'])

    return campos_alterados


def verifricar_descontos_opcionais(opcionais):
    opcionais_com_descontos = []

    for opcional in opcionais:
        if opcional['desconto'] != 0.00:
            opcionais_com_descontos.append(opcional)

    return opcionais_com_descontos
