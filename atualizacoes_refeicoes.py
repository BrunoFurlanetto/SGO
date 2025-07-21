from django.db import transaction

from peraltas.models import FichaDeEvento


substituicoes = {
    "Café": "cafe_manha",
    "Coffee manhã": "coffee_manha",
    "Almoço": "almoco",
    "Coffee tarde": "coffee_tarde",
    "Lanche tarde": "lanche_tarde",
    "Jantar": "jantar",
    "Lanche noite": "lanche_noite",
}


def atualizar_refeicoes():
    with transaction.atomic():
        fichas = FichaDeEvento.objects.all()

        for ficha in fichas:
            refeicao = ficha.refeicoes
            refeicao_atualizado = {}

            try:
                for data, refeicoes in refeicao.items():
                    refeicao_atualizado[data] = [substituicoes.get(ref, ref) for ref in refeicoes]
            except AttributeError:
                ...
            ficha.refeicoes = refeicao_atualizado
            ficha.save()


if __name__ == '__main__':
    atualizar_refeicoes()
    print("Atualização concluída!")
