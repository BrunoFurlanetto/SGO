import calendar
import datetime
from itertools import chain
from time import sleep

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET

from ceu.models import Atividades
from decorators import require_ajax
from mensagens.models import Mensagem
from peraltas.models import ClienteColegio, RelacaoClienteResponsavel, ProdutosPeraltas, AtividadesEco, Vendedor
from projetoCEU.chatguru.chatguru import Chatguru
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional, Orcamento, StatusOrcamento, CadastroPacotePromocional, \
    DadosDePacotes, ValoresPadrao, Tratativas, OrcamentosPromocionais, HorariosPadroes, TiposDePacote, \
    CategoriaOpcionais, OrcamentoMonitor
from .utils import verify_data, processar_formulario, JsonError, pegar_datas_padroes_pacotes_salvos
from .budget import Budget


@login_required(login_url='login')
def novo_orcamento(request):
    pacote_promocional = CadastroPacotePromocional()
    financeiro = User.objects.filter(pk=request.user.id, groups__name__icontains='financeiro').exists()
    usuarios_gerencia = User.objects.filter(groups__name__icontains='gerência')
    taxas_padrao = ValoresPadrao.objects.all()
    promocionais = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())
    cadastro_orcamento = CadastroOrcamento()
    categorias_so_ceu = CategoriaOpcionais.objects.filter(ceu_sem_hospedagem=True)

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'promocionais': promocionais,
        'pacote_promocional': pacote_promocional,
        'financeiro': financeiro,
        'usuarios_gerencia': usuarios_gerencia,
        'taxas_padrao': ValoresPadrao.mostrar_taxas(),
        'valores_taxas_padrao': ValoresPadrao.retornar_dados_gerencia(),
        'opcionais_staff': CategoriaOpcionais.objects.get(staff=True),
        'zerar_taxas': True,
        'id_categorias_so_ceu': [categoria.id for categoria in categorias_so_ceu],
        'categorias_so_ceu': [categoria.nome_categoria for categoria in categorias_so_ceu],
        'novo_orcamento': True,
    })


@login_required(login_url='login')
def clonar_orcamento(request, id_orcamento):
    financeiro = User.objects.filter(pk=request.user.id, groups__name__icontains='financeiro').exists()
    taxas_padrao = ValoresPadrao.objects.all()
    orcamento = Orcamento.objects.get(pk=id_orcamento)
    tratativa = Tratativas.objects.filter(
        Q(orcamentos__in=[orcamento.id]) | Q(orcamentos_em_previa__in=[orcamento.id])).distinct().first()
    usuarios_gerencia = User.objects.filter(groups__name__icontains='gerência')
    cadastro_orcamento = CadastroOrcamento(instance=orcamento)
    promocionais = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())
    categorias_so_ceu = CategoriaOpcionais.objects.filter(ceu_sem_hospedagem=True)
    opcionais_pacote = []

    if len(tratativa.orcamentos_ganhos()) > 0:
        tratativa = Tratativas.objects.create(colaborador=request.user, cliente=orcamento.cliente)

    if orcamento.orcamento_promocional:
        opcionais_pacote = orcamento.orcamento_promocional.listar_opcionais()

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'orcamento_origem': orcamento,
        'promocionais': promocionais,
        'financeiro': financeiro,
        'taxas_padrao': ValoresPadrao.mostrar_taxas(
            orcamento.orcamento_promocional.orcamento.objeto_gerencia if orcamento.orcamento_promocional else None,
            orcamento.tipo_de_pacote if orcamento.orcamento_promocional or (
                orcamento.tipo_de_pacote.so_ceu if orcamento.tipo_de_pacote else None) else None,
        ),
        'valores_taxas_padrao': ValoresPadrao.retornar_dados_gerencia(),
        'opcionais_staff': CategoriaOpcionais.objects.get(staff=True),
        'usuarios_gerencia': usuarios_gerencia,
        'id_tratativa': tratativa.pk,
        'id_orcamento': id_orcamento,
        'id_orcamento_clonado': id_orcamento,
        'id_categorias_so_ceu': [categoria.id for categoria in categorias_so_ceu],
        'categorias_so_ceu': [categoria.nome_categoria for categoria in categorias_so_ceu],
        'opcionais_pacote': opcionais_pacote,
        'novo_orcamento': True,
    })


@login_required(login_url='login')
def editar_previa(request, id_orcamento, gerente_aprovando=0):
    financeiro = User.objects.filter(pk=request.user.id, groups__name__icontains='financeiro').exists()
    taxas_padrao = ValoresPadrao.objects.all()
    orcamento = Orcamento.objects.get(pk=id_orcamento)
    usuarios_gerencia = User.objects.filter(groups__name__icontains='gerência')
    cadastro_orcamento = CadastroOrcamento(instance=orcamento)
    promocionais = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())
    pacote_promocional = CadastroPacotePromocional()
    orcamento_promocional = id_tratativa = None
    categorias_so_ceu = CategoriaOpcionais.objects.filter(ceu_sem_hospedagem=True)
    orcamento_editavel = True
    opcionais_pacote = {}

    if orcamento.orcamento_promocional:
        opcionais_pacote = orcamento.orcamento_promocional.listar_opcionais()

    if orcamento.promocional:
        orcamento_promocional = OrcamentosPromocionais.objects.get(orcamento=orcamento.id)
        pacote_promocional = CadastroPacotePromocional(instance=orcamento_promocional.dados_pacote)
        orcamento = orcamento_promocional.orcamento
    elif orcamento.orcamento_promocional:
        pacote_promocional = CadastroPacotePromocional(instance=orcamento.orcamento_promocional.dados_pacote)
        orcamento_promocional = orcamento.orcamento_promocional
        id_tratativa = Tratativas.objects.filter(
            Q(orcamentos__in=[orcamento.id]) | Q(orcamentos_em_previa__in=[orcamento.id])).distinct().first().pk

    msgs = Mensagem.objects.filter(object_id=orcamento.id)

    for msg in msgs:
        msg.responsavel = "remetente" if msg.remetente == request.user else "destinatario"

    if orcamento.status_orcamento.analise_gerencia or not orcamento.previa:
        orcamento_editavel = False

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'orcamento_origem': orcamento,
        'promocionais': promocionais,
        'financeiro': financeiro,
        'taxas_padrao': ValoresPadrao.mostrar_taxas(
            orcamento.objeto_gerencia,
            orcamento.tipo_de_pacote if orcamento.orcamento_promocional or (
                orcamento.tipo_de_pacote.so_ceu if orcamento.tipo_de_pacote else None) else None,
        ),
        'valores_taxas_padrao': ValoresPadrao.retornar_dados_gerencia(),
        'opcionais_staff': CategoriaOpcionais.objects.get(staff=True),
        'usuarios_gerencia': usuarios_gerencia,
        'id_orcamento': id_orcamento,
        'previa': True,
        'pacote_promocional': pacote_promocional,
        'gerente_aprovando': bool(gerente_aprovando),
        'dados_pacote': orcamento_promocional.dados_pacote if orcamento_promocional else None,
        'data_vencimento': orcamento.objeto_gerencia['data_vencimento'],
        'id_categorias_so_ceu': [categoria.id for categoria in categorias_so_ceu],
        'categorias_so_ceu': [categoria.nome_categoria for categoria in categorias_so_ceu],
        'opcionais_pacote': opcionais_pacote,
        'mensagens': msgs,
        'id_tratativa': id_tratativa,
        'orcamento_editavel': orcamento_editavel,
    })


def salvar_orcamento(request):
    if is_ajax(request):
        dados = processar_formulario(request.POST, request.user)

        if 'orcamento' not in dados:
            return dados

        data = dados['orcamento']
        print(data)
        valores_op = dados['valores_op']
        gerencia = dados['gerencia']
        business_fee = None
        commission = None
        business_fee = gerencia["taxa_comercial"] if "taxa_comercial" in gerencia else ...
        commission = gerencia["comissao"] if "comissao" in gerencia else ...

        budget = Budget(
            data['periodo_viagem'],
            data['n_dias'],
            data["hora_check_in"],
            data["hora_check_out"],
            data["lista_de_dias"],
            business_fee,
            commission,
        )
        budget.calculate(data, gerencia, valores_op)

        valor_final = budget.total.get_final_value()
        desconto = budget.total.get_adjustiment()

        data['desconto'] = f'{desconto:.2f}'
        data['valor'] = f'{valor_final:.2f}'
        data['data_vencimento'] = datetime.date.today() + datetime.timedelta(days=10)
        data['status_orcamento'] = StatusOrcamento.objects.get(
            analise_gerencia=False,
            aprovacao_cliente=False,
            negado_cliente=False,
            orcamento_vencido=False
        ).id

        if data.get('id_previa_orcamento'):
            previa_orcamento = Orcamento.objects.get(pk=data['id_previa_orcamento'])
            orcamento = CadastroOrcamento(data, instance=previa_orcamento)
        else:
            orcamento = CadastroOrcamento(data)

        pre_orcamento = orcamento.save(commit=False)
        pre_orcamento.objeto_gerencia = dados['gerencia']
        pre_orcamento.objeto_orcamento = budget.return_object()
        pre_orcamento.previa = data.get('salvar_previa') == 'true'
        pre_orcamento.apelido = '' if not pre_orcamento.previa else pre_orcamento.apelido

        if data.get('so_ceu'):
            pre_orcamento.objeto_orcamento['so_ceu'] = True

        if pre_orcamento.aprovacao_diretoria and not data.get('id_orcamento_clonado'):
            pre_orcamento.status_orcamento = StatusOrcamento.objects.get(
                analise_gerencia=True,
                negativa_gerencia=False,
                aprovacao_gerencia=False
            )

        if pre_orcamento.promocional:
            pre_orcamento.data_vencimento = gerencia['data_vencimento']
            pre_orcamento.cliente = pre_orcamento.responsavel = pre_orcamento.orcamento_promocional = None

        if data.get('resposta_diretoria'):
            if bool(int(data.get('resposta_diretoria'))):
                status_resposta = StatusOrcamento.objects.get(analise_gerencia=True, aprovacao_gerencia=True)
            else:
                status_resposta = StatusOrcamento.objects.get(analise_gerencia=True, negativa_gerencia=True)

            pre_orcamento.status_orcamento = status_resposta

        try:
            orcamento_salvo = orcamento.save()
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "data": budget.return_object(),
                "msg": e,
            })
        else:
            if not orcamento_salvo.promocional:
                try:
                    print('Aqui sim')
                    Tratativas.objects.get(
                        Q(id_tratativa=data.get('id_tratativa')) & (
                                Q(orcamentos__in=[orcamento_salvo.id]) | Q(
                            orcamentos_em_previa__in=[orcamento_salvo.id])
                        ),
                    )
                except Tratativas.DoesNotExist:
                    if data.get('id_tratativa'):
                        tratativa, nova = Tratativas.objects.get_or_create(
                            id_tratativa=data['id_tratativa'],
                            defaults={
                                'cliente': orcamento_salvo.cliente,
                                'colaborador': orcamento_salvo.colaborador,
                            }
                        )
                    else:
                        tratativa = Tratativas.objects.create(
                            cliente=orcamento_salvo.cliente,
                            colaborador=orcamento_salvo.colaborador
                        )
                        nova = True

                    if nova:
                        if orcamento_salvo.previa:
                            tratativa.orcamentos_em_previa.set([orcamento_salvo.id])
                        else:
                            tratativa.orcamentos.set([orcamento_salvo.id])
                    else:
                        if orcamento_salvo.previa:
                            tratativa.orcamentos_em_previa.add(orcamento_salvo.id)
                        else:
                            tratativa.orcamentos.add(orcamento_salvo.id)

                    tratativa.save()
                except Exception as e:
                    orcamento_salvo.delete()
                    return JsonResponse({'msg': f'{e}'}, status=400)
                else:
                    if orcamento_salvo.aprovacao_diretoria:
                        gerente = Vendedor.objects.get(usuario__pk=orcamento_salvo.gerente_responsavel.pk)
                        chat = Chatguru()
                        fone_gerente = f'55{gerente.telefone}' if not settings.DEBUG else '5514997348793'
                        chat.send_message(
                            fone_gerente,
                            f"Novo orçamento disponível para análise. Acesse o sistema para mais informações."
                        )
            else:
                promocional, criado = OrcamentosPromocionais.objects.get_or_create(
                    orcamento_id=orcamento_salvo.id,
                    defaults={
                        'orcamento_id': orcamento_salvo.id,
                        'dados_pacote_id': int(data.get('id_pacote_promocional'))
                    })

                if not criado:
                    promocional.liberado_para_venda = bool(data.get('liberado_para_venda', False))
                    promocional.save()

            if orcamento_salvo.status_orcamento.analise_gerencia and data.get('mensagem_gerencia'):
                try:
                    Mensagem.objects.create(
                        remetente=request.user,
                        destinatario=orcamento_salvo.gerente_responsavel,
                        conteudo=data.get('mensagem_gerencia'),
                        content_object=orcamento_salvo,
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f'Erro durante o processo de salvar a mensagem de pedido de desconto ({e}). Tente novamenteo mais tarde.'
                    )
                    orcamento_salvo.status_orcamento = StatusOrcamento.objects.get(
                        analise_gerencia=False,
                        aprovacao_cliente=False,
                        negado_cliente=False,
                        orcamento_vencido=False
                    )
                    orcamento_salvo.save()
                else:
                    messages.success(request, 'Pedido enviado a gerência com sucesso!')

    return JsonResponse({
        "status": "success",
        "msg": "",
    })


def apagar_orcamento(request, id_orcamento):
    tratativa = Tratativas.objects.filter(orcamentos__in=[id_orcamento]).exists()

    try:
        Orcamento.objects.get(pk=id_orcamento).delete()
    except Exception as e:
        messages.error(request, f'Orçamento não apagado ({e}). Tente novamente mais tarde.')

        return redirect('dashboard')
    else:
        messages.success(request, f'Orcamento apagado com sucesso!')

        return redirect('dashboard')


def calc_budget(req):
    if is_ajax(req):
        dados = processar_formulario(req.POST, req.user)

        if 'orcamento' not in dados:
            return dados

        data = dados['orcamento']
        valores_op = dados['valores_op']
        gerencia = dados['gerencia']

        # Verificar parametros obrigatórios
        if verify_data(data):
            return verify_data(data)

        # GERANDO ORÇAMENTO
        business_fee = None
        commission = None

        business_fee = gerencia["taxa_comercial"] if "taxa_comercial" in gerencia else ...
        commission = gerencia["comissao"] if "comissao" in gerencia else ...
        budget = Budget(data['periodo_viagem'], data['n_dias'], data["hora_check_in"],
                        data["hora_check_out"], data["lista_de_dias"], business_fee, commission)
        budget.calculate(data, gerencia, valores_op)

        if not budget.period.values:
            return JsonError('Existem taxas não cadastradas para o periodo em questão')

        if data.get('transporte') and data.get('transporte') == 'sim' and len(
                budget.transport.tranport_go_and_back.values) == 0:
            return JsonError('Transporte não cadastrado para o check in do grupo')

        # RESPONSE BUDGET CLASS
        return JsonResponse({
            "status": "success",
            "data": budget.return_object(),
            # "promocionais": promocionais,
            "limites_taxas": ValoresPadrao.listar_valores(),
            "racionais": {
                'check_in': data['racional_check_in'],
                'check_out': data['racional_check_out'],
            },
            "msg": "",
        })


@login_required(login_url='login')
def editar_pacotes_promocionais(request, id_dados_pacote):
    promocional = OrcamentosPromocionais.objects.get(pk=id_dados_pacote)
    financeiro = User.objects.filter(pk=request.user.id, groups__name__icontains='financeiro').exists()
    taxas_padrao = ValoresPadrao.objects.all()
    usuarios_gerencia = User.objects.filter(groups__name__icontains='gerência')
    cadastro_orcamento = CadastroOrcamento(instance=promocional.orcamento)
    pacote_promocional = CadastroPacotePromocional(instance=promocional.dados_pacote)
    promocional.orcamento.orcamento_promocional = promocional
    categorias_so_ceu = CategoriaOpcionais.objects.filter(ceu_sem_hospedagem=True)

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'orcamento_origem': promocional.orcamento,
        'financeiro': financeiro,
        'taxas_padrao': ValoresPadrao.mostrar_taxas(
            promocional.orcamento.objeto_gerencia,
            promocional.orcamento.tipo_de_pacote
        ),
        'valores_taxas_padrao': ValoresPadrao.retornar_dados_gerencia(),
        'opcionais_staff': CategoriaOpcionais.objects.get(staff=True),
        'usuarios_gerencia': usuarios_gerencia,
        'id_orcamento': promocional.orcamento.id,
        'previa': True,
        'pacote_promocional': pacote_promocional,
        'gerente_aprovando': False,
        'dados_pacote': promocional.dados_pacote,
        'editando_pacote': True,
        'data_vencimento': promocional.orcamento.objeto_gerencia['data_vencimento'],
        'promocional': promocional,
        'categorias_so_ceu': [categoria.id for categoria in categorias_so_ceu],
        'novo_orcamento': True,
    })


def veriricar_gerencia(request):
    id_usuario = request.POST.get('id_usuario')
    senha = request.POST.get('senha')

    try:
        user = User.objects.get(pk=id_usuario).username
        login = auth.authenticate(username=user, password=senha)
    except Exception as e:
        return JsonResponse({'msg': f'Erro interno do sistema ({e}), tente novamente mais tarde!'}, status=500)
    else:
        user = User.objects.get(pk=id_usuario).username
        login = auth.authenticate(username=user, password=senha)

        if login is not None:
            return JsonResponse({'msg': ''}, status=200)
        else:
            return JsonResponse({'msg': 'Senha incorreta'}, status=401)


@login_required(login_url='login')
def gerar_pdf(request, id_orcamento):
    orcamento = Orcamento.objects.get(pk=id_orcamento)

    return render(request, 'orcamento/pdf_orcamento.html', {
        'tratativa': orcamento,
    })


@login_required(login_url='login')
def gerar_pdf_previa(request, id_orcamento):
    orcamento = Orcamento.objects.get(pk=id_orcamento)

    return render(request, 'orcamento/pdf_orcamento.html', {
        'previa_orcamento': orcamento,
    })


def preencher_op_extras(request):
    if is_ajax(request):
        if request.GET.get('id_orcamento_extras'):
            orcamento = Orcamento.objects.get(pk=request.GET.get('id_orcamento_extras'))

            return JsonResponse({'opcionais_extra': orcamento.op_extra_formatado()})


def preencher_orcamento_promocional(request):
    if is_ajax(request):
        orcamento_promocional = OrcamentosPromocionais.objects.get(pk=request.GET.get('id_promocional')).orcamento
        lista_ops = {}

        for op in orcamento_promocional.opcionais.all():
            if op.categoria.id not in lista_ops:
                lista_ops[op.categoria.id] = []

            lista_ops[op.categoria.id].append(op.id)

        return JsonResponse({
            'obj': orcamento_promocional.objeto_orcamento,
            'gerencia': orcamento_promocional.objeto_gerencia,
            'check_in': orcamento_promocional.check_in.astimezone().strftime('%d/%m/%Y %H:%M'),
            'check_out': orcamento_promocional.check_out.astimezone().strftime('%d/%m/%Y %H:%M'),
            'tipo_de_pacote': orcamento_promocional.tipo_de_pacote.id if orcamento_promocional.tipo_de_pacote is not None else '',
            'monitoria': orcamento_promocional.tipo_monitoria.id,
            'transporte': orcamento_promocional.transporte,
            'opcionais': lista_ops,
            'opcionais_extra': orcamento_promocional.opcionais_extra,
        })


def validar_produtos(request):
    if is_ajax(request):
        check_in = datetime.datetime.strptime(request.GET.get('check_in'), '%d/%m/%Y %H:%M')
        check_out = datetime.datetime.strptime(request.GET.get('check_out'), '%d/%m/%Y %H:%M')
        n_pernoites = (check_out.date() - check_in.date()).days
        produtos = list(chain(ProdutosPeraltas.objects.filter(n_dias=n_pernoites)))
        produtos.append(ProdutosPeraltas.objects.get(produto__icontains='all party'))
        tipos_de_pacote = TiposDePacote.objects.filter(n_diarias=n_pernoites + 1)

        if n_pernoites == 0:
            if request.GET.get('so_ceu') == 'true':
                produtos.append(ProdutosPeraltas.objects.get(produto__icontains='ceu'))

            produtos.append(ProdutosPeraltas.objects.get(produto__icontains='visita técnica'))

        if n_pernoites >= 2:
            produtos.append(ProdutosPeraltas.objects.get(produto__icontains='ac 3 dias ou mais'))

        return JsonResponse({
            'ids_produtos': [produto.id for produto in produtos],
            'ids_tipo_de_pacote': [tipo.id for tipo in tipos_de_pacote],
        })


def verificar_responsaveis(request):
    if is_ajax(request):
        cliente = ClienteColegio.objects.get(pk=request.GET.get('id_cliente'))

        try:
            relacoes = RelacaoClienteResponsavel.objects.get(cliente=cliente)
        except RelacaoClienteResponsavel.DoesNotExist:
            return JsonResponse({'responsaveis': []})
        else:
            return JsonResponse({
                'responsaveis': [responsavel.id for responsavel in relacoes.responsavel.all()]
            })


def pesquisar_op(request):
    if is_ajax(request):
        return JsonResponse({'valor': OrcamentoOpicional.objects.get(pk=request.GET.get('id')).valor})


def pegar_dados_pacote(request):
    if is_ajax(request):
        orcamento_promocional = OrcamentosPromocionais.objects.get(pk=request.GET.get('id_pacote'))

        return JsonResponse({
            'orcamento_promocional': orcamento_promocional.orcamento.serializar_objetos(),
            'dados_promocionais': orcamento_promocional.dados_pacote.serializar_objetos()
        })


def salvar_pacote(request):
    if is_ajax(request):
        dados = DadosDePacotes.tratar_dados(request.POST)
        promocionais = OrcamentosPromocionais.objects.filter(
            orcamento__data_vencimento__year__gte=datetime.datetime.today().year - 1,
        )
        pacotes = [promocional.dados_pacote.nome_do_pacote for promocional in promocionais]

        if request.POST.get('id_pacote') != '':
            pacote_promocional = DadosDePacotes.objects.get(pk=request.POST.get('id_pacote'))
            dados_pacote_promocional = CadastroPacotePromocional(dados, instance=pacote_promocional)
        else:
            if dados['nome_do_pacote'] in pacotes:
                return JsonError('Nome do pacote já existente.', status_code=409)

            dados_pacote_promocional = CadastroPacotePromocional(dados)

        try:
            pacote = dados_pacote_promocional.save(commit=False)
            pacote.save()
        except ValueError:
            return JsonError('Exitem dados fantantes no cadastro do pacote.', status_code=400)
        except Exception as e:
            return JsonError(f'Erro ao salvar os dados do pacote ({e})! Tente novavemente mais tarde.', status_code=500)
        else:
            diarias = TiposDePacote.objects.get(pk=pacote.tipos_de_pacote_elegivel.id).n_diarias
            menor_horario = dados.get('check_in_permitido_1[]')
            maior_horario = dados.get('check_out_permitido_1[]')

            data_inicial, data_final = pegar_datas_padroes_pacotes_salvos(
                request.POST.get('periodo_1').split(' - ')[0],
                list(map(int, request.POST.getlist('dias_periodo_1[]'))),
                menor_horario,
                maior_horario,
                diarias
            )

            return JsonResponse({
                'id_pacote': pacote.id,
                'data_inicial': data_inicial,
                'data_final': data_final,
            })


def pegar_orcamentos_tratativa(request):
    if is_ajax(request) and request.method == "GET":
        if request.GET.get('id_tratativa'):
            tratativa = Tratativas.objects.get(pk=request.GET.get('id_tratativa'))

            return JsonResponse({'orcamentos': tratativa.pegar_orcamentos()})


def verificar_validade_opcionais(request):
    if is_ajax(request) and request.method == "GET":
        check_in = datetime.datetime.strptime(request.GET.get('check_in'), '%d/%m/%Y %H:%M').date()

        return JsonResponse({'id_opcionais': [
            op.id for op in
            OrcamentoOpicional.objects.filter(
                inicio_vigencia__lte=check_in,
                final_vigencia__gte=check_in,
                liberado=True
            )
        ]})


def verificar_pacotes_promocionais(request):
    if is_ajax(request):
        promocionais = OrcamentosPromocionais.pegar_pacotes_promocionais(
            int(request.GET.get('n_dias')),
            request.GET.get('id_tipo_de_pacote'),
            request.GET.get('data_check_in'),
            request.GET.get('data_check_out'),
        )

        if request.GET.get('id_tipo_de_pacote') != '':
            dados_taxas = TiposDePacote.objects.get(pk=request.GET.get('id_tipo_de_pacote')).retornar_dados_gerencia()
        else:
            dados_taxas = ValoresPadrao.retornar_dados_gerencia()

        return JsonResponse({
            'promocionais': promocionais,
            'dados_taxas': dados_taxas,
        })


def pegar_dados_tipo_pacote(request):
    if is_ajax(request):
        return


def verificar_dados_so_ceu(request):
    if is_ajax(request):
        data = datetime.datetime.strptime(request.GET.get('check_in'), '%d/%m/%Y %H:%M').date()
        id_produto = ProdutosPeraltas.objects.get(produto__icontains='só ceu').id
        ids_monitoria = OrcamentoMonitor.objects.filter(
            inicio_vigencia__lte=data,
            final_vigencia__gte=data,
            sem_monitoria=True,
            liberado=True
        )
        pacotes_so_ceu = TiposDePacote.objects.filter(so_ceu=True)

        return JsonResponse({
            'id_produto': id_produto,
            'ids_monitoria': [monitoria.id for monitoria in ids_monitoria],
            'id_pacotes_so_ceu': [pacote.id for pacote in pacotes_so_ceu],
        })


def pegar_monitoria_valida(request):
    if is_ajax(request):
        check_in = datetime.datetime.strptime(request.GET.get('check_in'), '%d/%m/%Y %H:%M').date()

        try:
            if request.user.groups.filter(name__icontains='financeiro').exists():
                monitorias_validas = OrcamentoMonitor.objects.filter(
                    inicio_vigencia__lte=check_in,
                    final_vigencia__gte=check_in,
                )
            else:
                monitorias_validas = OrcamentoMonitor.objects.filter(
                    inicio_vigencia__lte=check_in,
                    final_vigencia__gte=check_in,
                    liberado=True
                )
        except OrcamentoMonitor.DoesNotExist:
            return JsonError('Sem tarifário de monitoria para o período em questão', status_code=404)

        return JsonResponse({
            'monitorias': [{'id': monitoria.id, 'nome': monitoria.nome_monitoria, 'sem': monitoria.sem_monitoria} for
                           monitoria in monitorias_validas]
        })


@require_POST
@require_ajax
def reenvio_pedido_gerencia(request):
    try:
        orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))
        orcamento.status_orcamento = StatusOrcamento.objects.get(
            analise_gerencia=True,
            negativa_gerencia=False,
            aprovacao_gerencia=False
        )
        orcamento.save()
    except Exception as e:
        return JsonError(e, status_code=500)
    else:
        gerente = Vendedor.objects.get(usuario__pk=orcamento.gerente_responsavel.pk)
        chat = Chatguru()
        fone_gerente = f'55{gerente.telefone}' if not settings.DEBUG else '5514997348793'
        chat.send_message(
            fone_gerente,
            f"Novo orçamento disponível para análise. Acesse o sistema para mais informações."
        )

        return JsonResponse({}, status=200)


@require_POST
@require_ajax
def negar_orcamento(request):
    try:
        orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))
        orcamento.status_orcamento = StatusOrcamento.objects.get(analise_gerencia=True, negativa_gerencia=True)
        orcamento.save()
    except Exception as e:
        return JsonError(e, status_code=500)
    else:
        return JsonResponse({}, status=200)


@require_POST
@require_ajax
def trocar_gerente_responsavel(request):
    try:
        orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))
        gerente = User.objects.get(pk=request.POST.get('id_novo_gerente'))
        orcamento.gerente_responsavel = gerente
        orcamento.save()
    except Exception as e:
        return JsonError(e, status_code=500)
    else:
        return JsonResponse({}, status=200)


@require_GET
@login_required(login_url='login')
def transformar_em_tratativa(request, id_orcamento):
    try:
        orcamento = Orcamento.objects.get(pk=id_orcamento)
        tratativa = Tratativas.objects.get(orcamentos_em_previa__in=[orcamento.id])
        tratativa.orcamentos.add(orcamento)
        tratativa.orcamentos_em_previa.remove(orcamento)
        tratativa.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ({e}). Tente novamente mais tarde.')
        return redirect('dashboard')
    else:
        orcamento.status_orcamento = StatusOrcamento.objects.get(
            analise_gerencia=False,
            aprovacao_cliente=False,
            negado_cliente=False,
            orcamento_vencido=False
        )
        orcamento.previa = False
        orcamento.save()
        messages.success(request, f'Orçamento de {orcamento.cliente.__str__()} transformado em tratativa com sucesso!')

        return redirect('dashboard')


def verificar_validade_apelido(request):
    if request.POST.get('fase_orcamento') == 'novo':
        if len(Orcamento.objects.filter(
                colaborador=request.user, apelido=request.POST.get('apelido'),
                status_orcamento__orcamento_vencido=False,
                status_orcamento__aprovacao_cliente=False,
                status_orcamento__negado_cliente=False,
        )) > 0:
            return JsonResponse({}, status=409)
    else:
        if len(Orcamento.objects.filter(
                colaborador=request.user, apelido=request.POST.get('apelido'),
                status_orcamento__orcamento_vencido=False,
                status_orcamento__aprovacao_cliente=False,
                status_orcamento__negado_cliente=False,
        )) > 1:
            return JsonResponse({}, status=409)

    return JsonResponse({}, status=200)


@require_ajax
@require_POST
def ganhar_orcamento(request):
    try:
        orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))
        status_ganho = StatusOrcamento.objects.get(aprovacao_cliente=True)
        orcamento.status_orcamento = status_ganho
        orcamento.save()
    except Exception as e:
        return JsonResponse({'msg': f'Erro ao tentar ganhar orçamento ({e}). Tente novamente mais tarde.'}, status=500)

    return JsonResponse({}, status=200)


@require_ajax
@require_POST
def perder_orcamento(request):
    try:
        orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))
        status_perdido = StatusOrcamento.objects.get(negado_cliente=True)
        orcamento.status_orcamento = status_perdido
        orcamento.motivo_recusa = request.POST.get('motivo_recusa')
        orcamento.save()
    except Exception as e:
        return JsonResponse({'msg': f'Erro ao dar baixa no orçamento ({e}). Tente novamente mais tarde.'}, status=500)

    return JsonResponse({}, status=200)
