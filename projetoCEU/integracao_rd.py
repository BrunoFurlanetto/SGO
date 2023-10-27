import requests
from local_settings import TOKEN_RD


url_padrao = 'https://crm.rdstation.com/api/v1/deals/'

def alterar_status(id_negocio, id_novo_status):
    url = url_padrao + id_negocio + f'?token={TOKEN_RD}'
    payload = {"deal_stage_id": id_novo_status}
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.put(url, json=payload, headers=headers)

    print(response.text)
