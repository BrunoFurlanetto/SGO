from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import FileResponse

from ceu.funcoes import criar_pdf_relatorio


@login_required(login_url='login')
def resumo_financeiro_ceu(request):

    if request.method != 'POST':
        criar_pdf_relatorio()
        return render(request, 'ceu/resumo_financeiro_ceu.html')


