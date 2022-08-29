from cadastro.models import RelatorioDeAtendimentoCeu
from cadastro import views


def criarOrdem(request):
    teste = request.POST.get('coordenador')
    print(teste)
