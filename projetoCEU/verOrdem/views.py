from django.shortcuts import render, get_object_or_404
from cadastro.models import OrdemDeServico


def verOrdem(request, ordemdeservico_id):
    os = get_object_or_404(OrdemDeServico, id=ordemdeservico_id)
    rangei = range(1, 6)
    rangej = range(1, 5)

    return render(request, 'verOrdem/verOrdem.html', {'ordem': os, 'rangei': rangei, 'rangej': rangej})
