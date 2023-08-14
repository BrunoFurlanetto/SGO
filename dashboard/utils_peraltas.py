import hashlib
from datetime import datetime, timedelta


def campos_necessarios_aprovacao(orcamento):
    gerencia_default = {
        "desconto_produto": {'base': 0.0, 'verbose': 'Desconto no produto'},
        "desconto_monitoria": {'base': 0.0,'verbose':  'Desconto na monitoria'},
        "desconto_trasnporte": {'base': 0.0,'verbose':  'Desconto no transporte'},
        "desconto_geral": {'base': 0.0,'verbose':  'Desconto geral'},
        "comissao": {'base': 9.0,'verbose':  'Comissão de vendas'},
        "taxa_comercial": {'base': 5.0,'verbose':  'Taxa comercial'},
        "minimo_onibus": {'base': 30.0,'verbose':  'Mínimo no ônibus'},
        "data_pagamento": {'base': (orcamento.data_preenchimento + timedelta(days=15)).strftime('%d/%m/%Y'),
                           'verbose': 'Data de pagamento'}
    }

    campos_alterados = {'pedidos': [], 'opcionais': []}
    gerencia = orcamento.objeto_gerencia

    for chave in gerencia_default:
        if chave != 'data_pagamento' and (gerencia_default[chave]['base'] != gerencia[chave]):
            campos_alterados['pedidos'].append({
                'campo': chave,
                'valor_tratativa': gerencia[chave],
                'base': gerencia_default[chave]['base'],
                'verbose': gerencia_default[chave]['verbose']
            })
        elif chave == 'data_pagamento':
            data_pagamento = datetime.strptime(gerencia[chave], '%Y-%m-%d').strftime('%d/%m/%Y')

            if data_pagamento != gerencia_default[chave]['base']:
                campos_alterados['pedidos'].append({
                    'campo': chave,
                    'valor_tratativa': data_pagamento,
                    'base': gerencia_default[chave]['base'],
                    'verbose': gerencia_default[chave]['verbose']
                })

    campos_alterados['observacoes'] = gerencia['observacoes_desconto']
    campos_alterados['valor_com_desconto'] = float(orcamento.valor)
    campos_alterados['valor_base'] = orcamento.objeto_orcamento['total']['valor']
    campos_alterados['opcionais'] = verifricar_descontos_opcionais(orcamento.objeto_orcamento['descricao_opcionais'])
    campos_alterados['id_orcamento'] = orcamento.id

    return campos_alterados


def verifricar_descontos_opcionais(opcionais):
    opcionais_com_descontos = []

    for opcional in opcionais:
        if not 'outros' in opcional.keys() and opcional['desconto'] != 0.00:
            opcionais_com_descontos.append(opcional)

    return opcionais_com_descontos
