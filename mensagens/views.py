from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.http import require_GET, require_POST

import orcamento
from decorators import require_ajax
from mensagens.models import Mensagem
from orcamento.models import Orcamento
from projetoCEU.utils import is_ajax

@require_ajax
def salvar_mensagens(request):
    nova_mensagem = Mensagem.objects.create(
        remetente=request.user,
        destinatario=User.objects.get(pk=request.POST.get(''))
    )


@require_GET
@require_ajax
def encontrar_chat_orcamento(request):
    """Retorna todas as mensagens de um orçamento específico em JSON."""
    id_orcamento = request.GET.get('id_orcamento')

    if not id_orcamento:
        return JsonResponse({"erro": "ID do orçamento não fornecido"}, status=400)

    content_type = ContentType.objects.get_for_model(Orcamento)
    mensagens = Mensagem.objects.filter(content_type=content_type, object_id=id_orcamento).order_by("data_hora_envio")

    mensagens_json = []
    for mensagem in mensagens:
        # Atualiza a data de leitura se o usuário for o destinatário e a mensagem ainda não foi lida
        if mensagem.destinatario == request.user and not mensagem.data_hora_leitura:
            mensagem.data_hora_leitura = now()
            mensagem.save()
        print(mensagem.remetente, mensagem.remetente == request.user)
        mensagens_json.append({
            "remetente": mensagem.remetente.get_full_name() or mensagem.remetente.username,
            "destinatario": mensagem.destinatario.get_full_name() or mensagem.destinatario.username,
            'responsavel_msg': mensagem.nome_remetente if request.user == mensagem.remetente else mensagem.nome_destinatario,
            "conteudo": mensagem.conteudo,
            "data_hora_envio": mensagem.data_hora_envio.strftime("%d/%m/%Y %H:%M"),
            "responsavel": "remetente" if mensagem.remetente == request.user else "destinatario",
            "lida": bool(mensagem.data_hora_leitura),
        })

    return JsonResponse({
        "mensagens": mensagens_json,
        'ultimo_destinatario': {
                'id': mensagens.last().destinatario.pk,
                'nome': mensagens.last().destinatario.get_full_name(),
        },
        'cliente': Orcamento.objects.get(pk=id_orcamento).cliente.__str__(),
    })


@require_POST
@require_ajax
def salvar_mensagem(request):
    try:
        Mensagem.objects.create(
            remetente=request.user,
            destinatario=User.objects.get(pk=request.POST.get('id_destinatario')),
            conteudo=request.POST.get('mensagem'),
            content_object=Orcamento.objects.get(pk=request.POST.get('id_orcamento')),
        )
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)
    else:
        return JsonResponse({}, status=200)
