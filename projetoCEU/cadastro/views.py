from django.shortcuts import render, redirect
from .models import OrdemDeServico, Professores, Atividades, FormularioOrdem


def publico(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    atividades = Atividades.objects.all()
    rangei = range(1, 6)
    rangej = range(1, 5)

    OrdemDeServico.tipo = 'Público'
    OrdemDeServico.coordenador = request.POST.get('coordenador')
    OrdemDeServico.participantes_previa = request.POST.get('previaParticipantes')
    OrdemDeServico.participantes_confirmados = request.POST.get('participantes')
    OrdemDeServico.data_atendimento = request.POST.get('dataAtendimento')

    for i in range(2, 5):
        OrdemDeServico.professor_i = request.POST.get(f'prf{i}')

    OrdemDeServico.hora_entrada = request.POST.get('horaEntrada')

    for i in rangei:
        OrdemDeServico.atividade_i = request.POST.get(f'atv{i}')
        for j in rangej:
            OrdemDeServico.prf_j_atv_i = request.POST.get(f'prf{j}atv{i}')

    OrdemDeServico.relatorio = request.POST.get('relatorio')

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {'professores': professores, 'rangei': rangei,
                                                         'rangej': rangej, 'atividades': atividades})


def colegio(request):
    if not request.user.is_authenticated:
        return redirect('login')


def empresa(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html')
