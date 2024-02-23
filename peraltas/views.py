import datetime

from django.http import JsonResponse

from peraltas.models import ClienteColegio, Responsavel, FichaDeEvento


def empresas_sgo(request):
    clientes_json = []

    for cliente in ClienteColegio.objects.all():
        clientes_json.append({
            'razao_social': cliente.razao_social,
            'cnpj': cliente.cnpj,
            'endereco': cliente.endereco,
            'bairro': cliente.bairro,
            'cidade': cliente.cidade,
            'estado': cliente.estado,
            'cep': cliente.cep,
            'colaborador_cadastro': {
                'id': cliente.responsavel_cadastro.id if cliente.responsavel_cadastro else None,
                'nome_completo': cliente.responsavel_cadastro.get_full_name() if cliente.responsavel_cadastro else None,
            }
        })

    return JsonResponse(clientes_json, safe=False)


def responsaveis_sgo(request):
    responsaveis_json = []

    for responsavel in Responsavel.objects.all():
        responsaveis_json.append({
            'nome_completo': responsavel.nome,
            'telefone': responsavel.fone,
            'email': responsavel.email_responsavel_evento,
            'cargos': responsavel.listar_cargos(),
            'colaborador_cadastro': {
                'id': responsavel.responsavel_cadastro.id if responsavel.responsavel_cadastro else None,
                'nome_completo': responsavel.responsavel_cadastro.get_full_name() if responsavel.responsavel_cadastro else None,
            }
        })

    return JsonResponse(responsaveis_json, safe=False)


def fichas_sgo(request):
    fichas_json = []

    for ficha in FichaDeEvento.objects.filter(pre_reserva=False):
        fichas_json.append({
            'produto_peraltas': {
                'id': ficha.produto.id,
                'produto': ficha.produto.produto,
            },
            'check_in': ficha.check_in.strftime('%Y-%m-%d %H:%M'),
            'check_out': ficha.check_out.strftime('%Y-%m-%d %H:%M'),
            'qtd': ficha.qtd_convidada,
            'atividades_ceu': ficha.listar_atividades_ceu(),
            'codigos': {
                'pj': ficha.codigos_app.cliente_pj,
                'pf': ficha.codigos_app.cliente_pf,
                'e-ficha': ficha.codigos_app.evento,
            },
            'colaborador_cadastro': {
                'id': ficha.vendedora.usuario.id,
                'nome_completo': ficha.vendedora.usuario.get_full_name()
            },
            'observacoes': ficha.observacoes
        })

    return JsonResponse(fichas_json)
