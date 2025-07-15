import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from financeiro.models import CadastroFichaFinanceira, CadastroDadosEvento, \
    CadastroPlanosPagamento, CadastroNotaFiscal, DadosPagamento, FichaFinanceira, DadosEvento, PlanosPagamento
from mensagens.models import Mensagem
from orcamento.models import Orcamento, Tratativas
from peraltas.models import RelacaoClienteResponsavel, Responsavel, CadastroResponsavel


@login_required(login_url='login')
def ficha_financeira(request, id_orcamento):
    orcamento = Orcamento.objects.get(pk=id_orcamento)
    cadastro_ficha_financeira = CadastroFichaFinanceira(initial=orcamento.dados_iniciais())
    cadastro_dados_evento = CadastroDadosEvento(initial=orcamento.dados_iniciais())
    cadastro_planos_pagamento = CadastroPlanosPagamento(initial=orcamento.dados_iniciais())
    cadastro_nota_fiscal = CadastroNotaFiscal(initial=orcamento.dados_iniciais())
    cadastro_responsavel = CadastroResponsavel()
    relacoes = RelacaoClienteResponsavel.objects.filter(cliente=orcamento.cliente)
    responaveis = Responsavel.objects.filter(id__in=relacoes.values_list("responsavel", flat=True)).distinct()

    return render(request, 'financeiro/ficha_financeira.html', {
        'orcamento': orcamento,
        'ficha_financeira': cadastro_ficha_financeira,
        'dados_evento': cadastro_dados_evento,
        'planos_pagamento': cadastro_planos_pagamento,
        'nota_fiscal': cadastro_nota_fiscal,
        'cadastro_responsavel': cadastro_responsavel,
        'ids_responsaveis': list(responaveis.values_list('id', flat=True)),
    })


@login_required(login_url='login')
def salvar_ficha_financeiro(request, id_orcamento, id_ficha_financeira=None):
    ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira) if id_ficha_financeira else None
    orcamento = Orcamento.objects.get(pk=id_orcamento)
    erros = []

    if id_ficha_financeira:
        cadastro_ficha_financeira = CadastroFichaFinanceira(request.POST, instance=ficha)
        cadastro_dados_evento = CadastroDadosEvento(request.POST, instance=ficha.dados_evento)
        cadastro_planos_pagamento = CadastroPlanosPagamento(request.POST, instance=ficha.planos_pagamento)
        cadastro_nota_fiscal = CadastroNotaFiscal(request.POST, instance=ficha.dados_nota_fiscal)
    else:
        cadastro_ficha_financeira = CadastroFichaFinanceira(request.POST)
        cadastro_dados_evento = CadastroDadosEvento(request.POST)
        cadastro_planos_pagamento = CadastroPlanosPagamento(request.POST)
        cadastro_nota_fiscal = CadastroNotaFiscal(request.POST)

    if request.POST.get('nf'):
        if request.POST.get('nf') == 'on':
            if not cadastro_nota_fiscal.is_valid():
                erros.append(cadastro_nota_fiscal.errors)
    else:
        cadastro_nota_fiscal = None

    if not cadastro_planos_pagamento.is_valid():
        erros.append(cadastro_planos_pagamento.errors)

    if not cadastro_dados_evento.is_valid():
        erros.append(cadastro_dados_evento.errors)

    if len(erros) > 0:
        messages.warning(request, erros)

        return render(request, 'financeiro/ficha_financeira.html', {
            'orcamento': orcamento,
            'ficha_financeira': cadastro_ficha_financeira,
            'dados_evento': cadastro_dados_evento,
            'planos_pagamento': cadastro_planos_pagamento,
            'nota_fiscal': cadastro_nota_fiscal,
        })
    else:
        try:
            dados_evento = cadastro_dados_evento.save(commit=False)
            dados_evento.cortesias_externas = DadosEvento.preencher_cortesias_externas(request.POST)
            dados_evento.save()
            dados_nota = cadastro_nota_fiscal.save() if cadastro_nota_fiscal else None
            planos_pagamento = cadastro_planos_pagamento.save(commit=False)
            planos_pagamento.comissoes_externas = PlanosPagamento.preencher_dados_comissionados(request.POST)
            planos_pagamento.save()
            dados_pagamento = DadosPagamento.auto_preenchimento(orcamento)
            responsavel = Responsavel.objects.get(pk=request.POST.get('enviado_ac'))

            if not id_ficha_financeira:
                FichaFinanceira.objects.create(
                    orcamento=orcamento,
                    cliente=orcamento.cliente,
                    enviado_ac=responsavel,
                    dados_evento=dados_evento,
                    dados_pagamento=dados_pagamento,
                    planos_pagamento=planos_pagamento,
                    nf=request.POST.get('nf', False) == 'on',
                    dados_nota_fiscal=dados_nota,
                    valor_final=planos_pagamento.valor_a_vista,
                    observacoes_ficha_financeira=request.POST.get('observacoes_ficha_financeira'),
                    descritivo_ficha_financeira=orcamento.objeto_orcamento,
                    data_preenchimento_comercial=datetime.datetime.now()
                )
            else:
                ficha.enviado_ac = request.POST.get('enviado_ac')
                ficha.nf = request.POST.get('nf', False) == 'on'
                ficha.valor_final = planos_pagamento.valor_a_vista
                ficha.observacoes_ficha_financeira = request.POST.get('observacoes_ficha_financeira')
                ficha.negado = False
                ficha.motivo_recusa = ''
                ficha.save()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado durante o cadastro da ficha financeira ({e})')
            return render(request, 'financeiro/ficha_financeira.html', {
                'orcamento': orcamento,
                'ficha_financeira': cadastro_ficha_financeira,
                'dados_evento': cadastro_dados_evento,
                'planos_pagamento': cadastro_planos_pagamento,
                'nota_fiscal': cadastro_nota_fiscal,
            })
        else:
            tratativa = Tratativas.objects.get(orcamentos__in=[id_orcamento])
            tratativa.ficha_financeira = True
            tratativa.save()
            messages.success(request, f'Ficha financeira de {orcamento.cliente} salva com sucesso. Aguardando aprovação da diretoria.')

            return redirect('dashboardPeraltas')


@login_required(login_url='login')
def revisar_ficha_financeira(request, id_ficha_financeira):
    if not User.objects.filter(pk=request.user.id, groups__name__in=['Diretoria', 'Financeiro']).exists():
        return redirect('dashboard')

    ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira)
    orcamento = Orcamento.objects.get(pk=ficha.orcamento.id)
    mensagens = Mensagem.objects.filter(object_id=orcamento.id)
    cadastro_ficha_financeira = CadastroFichaFinanceira(instance=ficha)
    cadastro_dados_evento = CadastroDadosEvento(instance=ficha.dados_evento)
    cadastro_planos_pagamento = CadastroPlanosPagamento(instance=ficha.planos_pagamento)
    cadastro_nota_fiscal = CadastroNotaFiscal(instance=ficha.dados_nota_fiscal)
    responsavel_financeiro = ficha.dados_evento.responsavel_financeiro

    return render(request, 'financeiro/ficha_financeira.html', {
        'ficha': ficha,
        'orcamento': orcamento,
        'ficha_financeira': cadastro_ficha_financeira,
        'dados_evento': cadastro_dados_evento,
        'planos_pagamento': cadastro_planos_pagamento,
        'nota_fiscal': cadastro_nota_fiscal,
        'revisando': True,
        'financeiro': User.objects.filter(pk=request.user.id, groups__name__in=['Financeiro']).exists(),
        'pagamento_eficha': ficha.planos_pagamento.verficar_eficha(),
        'telefone_financeiro': responsavel_financeiro.fone,
        'whats_financeiro': responsavel_financeiro.whats or '',
        'email_financeiro': responsavel_financeiro.email_responsavel_evento,
        'mensagens': mensagens,
    })


@login_required(login_url='login')
def aprovar_ficha_financeira(request, id_ficha_financeira):
    ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira)

    try:
        ficha.autorizado_diretoria = True
        ficha.comentario_diretoria = request.POST.get('comentario_diretoria')
        ficha.data_aprovacao_diretoria = datetime.datetime.now()
        ficha.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ({e}). Tente novamente mais tarde.')
    else:
        messages.success(request, f'Ficha financeira de {ficha.cliente} aprovado com sucesso.')

    return redirect('dashboard')


@login_required(login_url='login')
def negar_ficha_financeira(request, id_ficha_financeira):
    ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira)

    try:
        ficha.negado = True
        ficha.motivo_recusa = request.POST.get('motivo_recusa')
        ficha.data_aprovacao_diretoria = datetime.datetime.now()
        ficha.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ({e}). Tente novamente mais tarde.')
    else:
        messages.success(request, f'Ficha financeira de {ficha.cliente} voltou para o colaborador responsável.')

        return redirect('dashboard')


@login_required(login_url='login')
def editar_ficha_financeira(request, id_ficha_financeira):
    ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira)
    orcamento = Orcamento.objects.get(pk=ficha.orcamento.id)
    cadastro_ficha_financeira = CadastroFichaFinanceira(instance=ficha)
    cadastro_dados_evento = CadastroDadosEvento(instance=ficha.dados_evento)
    cadastro_planos_pagamento = CadastroPlanosPagamento(instance=ficha.planos_pagamento)
    cadastro_nota_fiscal = CadastroNotaFiscal(instance=ficha.dados_nota_fiscal)

    return render(request, 'financeiro/ficha_financeira.html', {
        'ficha': ficha,
        'orcamento': orcamento,
        'ficha_financeira': cadastro_ficha_financeira,
        'dados_evento': cadastro_dados_evento,
        'planos_pagamento': cadastro_planos_pagamento,
        'nota_fiscal': cadastro_nota_fiscal,
        'pagamento_eficha': ficha.planos_pagamento.verficar_eficha(),
    })


@login_required(login_url='login')
def faturar_ficha_financeira(request, id_ficha_financeira):
    try:
        ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira)

        if not ficha.faturado:
            ficha.faturado = True
            ficha.data_faturamento = datetime.datetime.now()
        else:
            ficha.faturado = False
            ficha.data_faturamento = None

        ficha.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ({e}), por favor tente novamente mais tarde!')
        return redirect('revisar_ficha_financeira', id_ficha_financeira)
    else:
        messages.success(request, 'Ficha financeira faturada com sucesso!')
        return redirect('dashboard')


def buscar_dados_responsavel(request):
    responsavel = Responsavel.objects.get(pk=request.GET.get('id_responsavel'))

    return JsonResponse({
        'telefone': responsavel.fone,
        'email': responsavel.email_responsavel_evento,
        'whats': responsavel.whats,
    })

