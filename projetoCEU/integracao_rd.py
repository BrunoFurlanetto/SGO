import requests
from local_settings import TOKEN_RD
from peraltas.models import FichaDeEvento, CodigosPadrao

url_padrao = 'https://crm.rdstation.com/api/v1/deals/'

def alterar_status(id_negocio, id_novo_status, corporativo=False):
    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]

    if id_negocio in codigos_padrao:
        return

    url = url_padrao + id_negocio + f'?token={TOKEN_RD}'
    payload = {"deal_stage_id": id_novo_status}
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    requests.put(url, json=payload, headers=headers)


def alterar_campos_personalizados(id_negocio, ficha_de_evento):
    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]

    if id_negocio in codigos_padrao:
        return

    url = url_padrao + id_negocio + f'?token={TOKEN_RD}'
    payload = {"deal": formatar_envio_valores('', ficha_de_evento)}
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    requests.put(url, json=payload, headers=headers)


def formatar_envio_valores(id_negocio, ficha_de_evento):
    id_campos_alteraveis = {
        'check_in': '64ff4e1f2ab269001b8bb10f',
        'check_out': '64ff4e32966cc10022693bc2',
        'qtd_convidada': '653c27705253a1000fb45eef',
        'produto': '653c288d31239700134b43a8',
        'qtd_confirmada': '653c278977bcad00157545b2',
        'adesao': '653c279bd2c439000f97865b'
    }
    url = url_padrao + id_negocio + f'?token={TOKEN_RD}'
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    try:
        campos_personalizados = response.json()['deal_custom_fields']
    except KeyError as e:
        raise e
    except Exception as e:
        ...

    campos = {d['custom_field_id']: d['value'] for d in campos_personalizados}

    for campo, id_campo_id in id_campos_alteraveis.items():
        valor = getattr(ficha_de_evento, campo, None)
        campo_objeto = FichaDeEvento._meta.get_field(campo)
        tipo_do_campo = campo_objeto.get_internal_type()

        if tipo_do_campo == 'DateTimeField':
            campos[id_campo_id] = valor.strftime('%Y-%m-%d %H:%M')
        elif tipo_do_campo == 'ForeignKey':
            campos[id_campo_id] = valor.__str__() if valor else ''
        else:
            campos[id_campo_id] = str(valor if valor else 0)

    return {"deal_custom_fields": [{'value': valor, 'custom_field_id': id_campo} for id_campo, valor in campos.items()]}

def verificar_id(id_negocio):
    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]

    if id_negocio in codigos_padrao:
        return True

    url = f'https://crm.rdstation.com/api/v1/deals?token={TOKEN_RD}&closed_at=false&limit=200'
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    negocios_total = response.json()['total']
    paginas = int(negocios_total // 200) if negocios_total % 200 == 0 else int(negocios_total // 200) + 1
    negocios = response.json()['deals']
    ids_negocios = [negocio['id'] for negocio in negocios]

    if id_negocio in ids_negocios:
        return True

    for pagina in range(2, paginas + 1):
        url = f'https://crm.rdstation.com/api/v1/deals?token={TOKEN_RD}&closed_at=false&limit=200&page={pagina}'
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        negocios = response.json()['deals']
        ids_negocios = [negocio['id'] for negocio in negocios]

        if id_negocio in ids_negocios:
            return True

    return False
