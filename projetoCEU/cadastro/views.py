from time import sleep

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .funcoes import is_ajax, analisar_tabela_atividade, verificar_tabela, indice_formulario
from .models import Professores, Atividades, Tipo, OrdemDeServicoPublico, OrdemDeServicoColegio


def publico(request):
    if not request.user.is_authenticated:
        return redirect('login')

    ordem_publico = OrdemDeServicoPublico()
    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()
    range_i = range(1, 6)
    range_j = range(1, 5)

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {'formulario': ordem_publico, 'rangei': range_i,
                                                         'rangej': range_j, 'atividades': atividades,
                                                         'professores': professores})

    if is_ajax(request) and request.method == 'POST':
        return HttpResponse(Professores.objects.get(id=request.POST.get('id_professor')))

    ordem_publico = OrdemDeServicoPublico(request.POST)
    erro_de_preenchimento, mensagem_erro = verificar_tabela(request.POST)

    if not erro_de_preenchimento:
        os = ordem_publico.save(commit=False)
        os.tipo = Tipo.objects.get(tipo='Público')
        analisar_tabela_atividade(os, request.POST)
        try:
            os.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor,tentar mais tarde')
            return redirect('dashboard')
        else:
            messages.success(request, 'Ordem de serviço salva com sucesso!')
            return redirect('dashboard')
    else:
        ordem_publico = OrdemDeServicoPublico(request.POST)
        messages.error(request, mensagem_erro)
        return render(request, 'cadastro/publico.html', {'formulario': ordem_publico, 'rangei': range_i,
                                                         'rangej': range_j, 'atividades': atividades,
                                                         'professores': professores})


def colegio(request):
    if not request.user.is_authenticated:
        return redirect('login')

    ordem_colegio = OrdemDeServicoColegio()
    atividades = indice_formulario(ordem_colegio, 'atividade_')
    horas = indice_formulario(ordem_colegio, 'hora')
    professores = Professores.objects.all()
    range_j = range(1, 5)

    if request.method != 'POST':
        return render(request, 'cadastro/colegio.html', {'formulario': ordem_colegio, 'atividades': atividades,
                                                         'horas': horas, 'professores': professores,
                                                         'rangej': range_j})

    # --- TESTES PARA A EXISTÊNCIA DAS ATIVIDADES E JÁ CHAMAR FUNÇÃO PRA JUNTAR OS PROFESSORES
    # --- DAS ATIVIDADES EXISTÊNTES.

    return redirect('dashboard')


def empresa(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html')

    # --- TESTES PARA EXISTÊNCIA DE ALGUMA ATIVIDADE E JÁ CHAMAR FUNÇÃO PRA JUNTAR OS PROFESSORES
    # --- DAS ATIVIDADES EXISTÊNTES.

    # --- PRIMEIRA ENTRADA E SAIDA DA EMPRESA NO CEU, PEGAR HORÁRIOS DE ENTRADAS E SAÍDAS,
    # --- FAZER CONTA DE HORAS DA PRIMEIRA LOCAÇÃO, TUDO COM FUNCÕES

    return redirect('dashboard')
