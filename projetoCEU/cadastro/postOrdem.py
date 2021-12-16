from cadastro.models import OrdemDeServico
from cadastro import views


def criarOrdem(request):
    teste = request.POST.get('coordenador')
    print(teste)
