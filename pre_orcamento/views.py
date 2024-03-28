from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pre_orcamento.models import PreCadastroFormulario, CadastroPreOrcamento


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'pre_orcamento/dashoboard.html')


@login_required(login_url='login')
def nova_previa(request):
    pre_cadastro = PreCadastroFormulario()
    previa = CadastroPreOrcamento()

    return render(request, 'pre_orcamento/nova_previa.html', {
        'pre_cadastro': pre_cadastro,
        'previa': previa
    })
