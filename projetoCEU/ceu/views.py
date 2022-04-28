from django.shortcuts import render

from django.http import FileResponse

from ceu.funcoes import criar_pdf_relatorio


def resumo_financeiro_ceu(request):

    if request.method != 'POST':
        return render(request, 'ceu/resumo_financeiro_ceu.html')

    return FileResponse(criar_pdf_relatorio(), as_attachment=True, filename='resumo financeiro.pdf')


