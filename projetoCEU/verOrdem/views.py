from django.shortcuts import render, get_object_or_404
from cadastro.models import RelatorioDeAtendimentoCeu
from verOrdem.funcoes import juntar_equipe, contar_atividades


def verOrdem(request, ordemdeservico_id):
    os = get_object_or_404(RelatorioDeAtendimentoCeu, id=ordemdeservico_id)
    rangei = range(1, 6)
    rangej = range(1, 5)

    os.equipe = juntar_equipe(os)
    os.n_atividades = range(contar_atividades(os)[0])
    os.atividades = contar_atividades(os)[1]
    os.horas_atividades = contar_atividades(os)[2]
    # os.profs = contar_atividades(os)[3]

    return render(request, 'verOrdem/verOrdem.html', {'ordem': os, 'rangei': rangei, 'rangej': rangej})
