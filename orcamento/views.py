import calendar
import datetime
from itertools import chain

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from ceu.models import Atividades
from peraltas.models import ClienteColegio, RelacaoClienteResponsavel, ProdutosPeraltas, AtividadesEco
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional, Orcamento, StatusOrcamento, CadastroPacotePromocional, \
    DadosDePacotes, ValoresPadrao, Tratativas, OrcamentosPromocionais, HorariosPadroes
from .utils import verify_data, processar_formulario, JsonError
from .budget import Budget


@login_required(login_url='login')
def novo_orcamento(request):
    pacote_promocional = CadastroPacotePromocional()
    financeiro = User.objects.filter(pk=request.user.id, groups__name__icontains='financeiro').exists()
    usuarios_gerencia = User.objects.filter(groups__name__icontains='gerência')
    taxas_padrao = ValoresPadrao.objects.all()
    promocionais = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())
    cadastro_orcamento = CadastroOrcamento()

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'promocionais': promocionais,
        'pacote_promocional': pacote_promocional,
        'financeiro': financeiro,
        'taxas_padrao': taxas_padrao,
        'usuarios_gerencia': usuarios_gerencia,
        'zerar_taxas': True,
    })


@login_required(login_url='login')
def clonar_orcamento(request, id_tratativa, ):
    financeiro = User.objects.filter(pk=request.user.id, groups__name__icontains='financeiro').exists()
    tratativa = Tratativas.objects.get(id_tratativa=id_tratativa)
    taxas_padrao = ValoresPadrao.objects.all()
    id_orcamento = tratativa.orcamentos.last().id
    orcamento = Orcamento.objects.get(pk=id_orcamento)
    usuarios_gerencia = User.objects.filter(groups__name__icontains='gerência')
    cadastro_orcamento = CadastroOrcamento(instance=orcamento)
    tratativa = Tratativas.objects.get(orcamentos__in=[id_orcamento])
    promocionais = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'orcamento_origem': orcamento,
        'promocionais': promocionais,
        'financeiro': financeiro,
        'taxas_padrao': taxas_padrao,
        'usuarios_gerencia': usuarios_gerencia,
        'tratativa': tratativa,
        'id_orcamento': id_orcamento,
        'zerar_taxas': True,
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
    orcamento_promocional = None

    if orcamento.promocional:
        orcamento_promocional = OrcamentosPromocionais.objects.get(orcamento=orcamento.id)
        pacote_promocional = CadastroPacotePromocional(instance=orcamento_promocional.dados_pacote)
        orcamento = orcamento_promocional.orcamento
    elif orcamento.orcamento_promocional:
        pacote_promocional = CadastroPacotePromocional(instance=orcamento.orcamento_promocional.dados_pacote)
        orcamento_promocional = orcamento.orcamento_promocional

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'orcamento_origem': orcamento,
        'promocionais': promocionais,
        'financeiro': financeiro,
        'taxas_padrao': taxas_padrao,
        'usuarios_gerencia': usuarios_gerencia,
        'id_orcamento': id_orcamento,
        'previa': True,
        'pacote_promocional': pacote_promocional,
        'gerente_aprovando': bool(gerente_aprovando),
        'dados_pacote': orcamento_promocional.dados_pacote if orcamento_promocional else None,
    })


def salvar_orcamento(request, id_tratativa=None):
    if is_ajax(request):
        dados = processar_formulario(request.POST, request.user)

        if 'orcamento' not in dados:
            return dados

        data = dados['orcamento']
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
        data['status_orcamento'] = StatusOrcamento.objects.get(status__contains='aberto').id
        print(data)
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

        if pre_orcamento.aprovacao_diretoria:
            pre_orcamento.status_orcamento = StatusOrcamento.objects.get(status__icontains='análise')

        if pre_orcamento.promocional:
            pre_orcamento.data_vencimento = gerencia['data_vencimento']
            pre_orcamento.cliente = pre_orcamento.responsavel = pre_orcamento.orcamento_promocional = None

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
                    tratativa_existente = Tratativas.objects.get(orcamentos__in=[orcamento_salvo.id])
                except Tratativas.DoesNotExist:
                    if id_tratativa or not orcamento_salvo.previa:
                        nova_tratativa, criado = Tratativas.objects.get_or_create(
                            id_tratativa=id_tratativa,
                            defaults={
                                'cliente': orcamento_salvo.cliente,
                                'colaborador': orcamento_salvo.colaborador,
                            }
                        )

                        if criado:
                            nova_tratativa.orcamentos.set([orcamento_salvo])
                        else:
                            nova_tratativa.orcamentos.add(orcamento_salvo)

                        nova_tratativa.save()
                else:
                    tratativa = Tratativas.objects.get(id_tratativa=tratativa_existente.id_tratativa)
                    tratativa.orcamentos.add(orcamento_salvo.id)
                    tratativa.save()
            else:
                OrcamentosPromocionais.objects.get_or_create(
                    orcamento_id=orcamento_salvo.id,
                    defaults={
                        'orcamento_id': orcamento_salvo.id,
                        'dados_pacote_id': int(data.get('id_pacote_promocional'))
                    })

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

    return render(request, 'orcamento/orcamento.html', {
        'orcamento': cadastro_orcamento,
        'orcamento_origem': promocional.orcamento,
        'financeiro': financeiro,
        'taxas_padrao': taxas_padrao,
        'usuarios_gerencia': usuarios_gerencia,
        'id_orcamento': promocional.orcamento.id,
        'previa': True,
        'pacote_promocional': pacote_promocional,
        'gerente_aprovando': False,
        'dados_pacote': promocional.dados_pacote,
        'editando_pacote': True,
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
def gerar_pdf(request, id_tratativa):
    tratativa = Tratativas.objects.get(id_tratativa=id_tratativa)

    return render(request, 'orcamento/pdf_orcamento.html', {
        'tratativa': tratativa,
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
            'produto': orcamento_promocional.produto.id if orcamento_promocional.produto is not None else '',
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

        if n_pernoites == 0:
            produtos.append(ProdutosPeraltas.objects.get(produto__icontains='ceu'))
            produtos.append(ProdutosPeraltas.objects.get(produto__icontains='visita técnica'))

        if n_pernoites >= 2:
            produtos.append(ProdutosPeraltas.objects.get(produto__icontains='ac 3 dias ou mais'))

        return JsonResponse({'ids': [produto.id for produto in produtos]})


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

        if request.POST.get('id_pacote') != '':
            pacote_promocional = DadosDePacotes.objects.get(pk=request.POST.get('id_pacote'))
            dados_pacote_promocional = CadastroPacotePromocional(dados, instance=pacote_promocional)
        else:
            dados_pacote_promocional = CadastroPacotePromocional(dados)

        try:
            pacote = dados_pacote_promocional.save(commit=False)
            pacote.save()
        except Exception as e:
            return JsonError(f'Erro ao salvar os dados do pacote ({e})! Tente novavemente mais tarde.')
        else:
            DadosDePacotes.objects.get(pk=pacote.id).produtos_elegiveis.set(dados['produtos_elegiveis'])
            menor_horario = dados.get('check_in_permitido_1[]')
            maior_horario = dados.get('check_out_permitido_1[]')

            return JsonResponse(
                {'id_pacote': pacote.id, 'menor_horario': menor_horario, 'maior_horario': maior_horario}
            )


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
            OrcamentoOpicional.objects.filter(inicio_vigencia__lte=check_in, final_vigencia__gte=check_in)
        ]})


def verificar_pacotes_promocionais(request):
    if is_ajax(request):
        promocionais = OrcamentosPromocionais.pegar_pacotes_promocionais(
            int(request.GET.get('n_dias')),
            int(request.GET.get('id_produto')),
            request.GET.get('data_check_in'),
            request.GET.get('data_check_out'),
        )

        return JsonResponse({'promocionais': promocionais})
