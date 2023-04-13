
from django.http import JsonResponse
from .mock import mock_optional


def JsonError(msg):
    return JsonResponse({
        "status": "error",
        "data": {},
        "msg": msg
    }, status=422)


def verify_data(data):
    if not "period" in data:
        return JsonError("É necessario informar o 'periodo' como parametro!")

    if not "days" in data:
        return JsonError("É necessario informar a 'quantidade de dias' da estada!")

    # if data['days'] < 2:
    #     return JsonError("No minimo 2 dias na")

    if not "comming" in data:
        return JsonError("É necessario informar a hora de chegada do evento")

    if not "exit" in data:
        return JsonError("É necessario informar a hora de saida!")

    if "optional" in data:
        # todo: VERIFICAR SE OS IDs dos OPCIONAIS ESTÃO CADASTRADOS
        ids_optional_db = []
        for optional in mock_optional:
            ids_optional_db.append(optional['id'])

        for target_id in data['optional']:
            if not target_id in ids_optional_db:
                return JsonError('O opcional_id ' + f'{target_id}' + ' não foi encontrado')

# REMOVE LATER:


def get_optional_pk(id):
    for optional in mock_optional:
        if optional['id'] == id:
            return optional
