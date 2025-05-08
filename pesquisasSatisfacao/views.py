from django.contrib import messages
from django.shortcuts import render, redirect

from ordemDeServico.models import OrdemDeServico
from peraltas.models import EscalaAcampamento
from pesquisasSatisfacao.forms import CoordenacaoAvaliandoMonitoriaForm, AvaliacaoIndividualMonitorFormSet, \
    DestaqueAtividadesFormSet, DesempenhoAcimaMediaFormSet
from pesquisasSatisfacao.models import AvaliacaoIndividualMonitor


def avaliacao_coordenacao_monitoria(request, id_ordem_de_servico):
    # Inicializa todos os forms
    form = CoordenacaoAvaliandoMonitoriaForm(request.POST or None)
    avaliacao_formset = AvaliacaoIndividualMonitorFormSet(
        request.POST or None,
        prefix='avaliacoes'
    )
    destaque_formset = DestaqueAtividadesFormSet(
        request.POST or None,
        prefix='destaques'
    )
    desempenho_formset = DesempenhoAcimaMediaFormSet(
        request.POST or None,
        prefix='desempenho'
    )
    ordem = OrdemDeServico.objects.get(pk=id_ordem_de_servico)
    monitores = EscalaAcampamento.objects.get(ficha_de_evento=ordem.ficha_de_evento).monitores_acampamento.all()

    if request.method == 'POST':
        # Valida todos os formulários
        if (form.is_valid() and
                avaliacao_formset.is_valid() and
                destaque_formset.is_valid() and
                desempenho_formset.is_valid()):

            # Salva a pesquisa principal
            pesquisa = form.save(commit=False)
            pesquisa.coordenador = request.user
            pesquisa.save()

            # Salva os formsets associados
            avaliacao_formset.instance = pesquisa
            avaliacao_formset.save()

            destaque_formset.instance = pesquisa
            destaque_formset.save()

            desempenho_formset.instance = pesquisa
            desempenho_formset.save()

            messages.success(request, 'Pesquisa enviada com sucesso!')

            return redirect('pagina_de_sucesso')  # Altere para sua URL de sucesso

        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CoordenacaoAvaliandoMonitoriaForm()
        # Cria um form para cada monitor
        initial_data = [{'monitor': monitor} for monitor in monitores]
        avaliacao_formset = AvaliacaoIndividualMonitorFormSet(
            queryset=AvaliacaoIndividualMonitor.objects.none(),
            initial=initial_data
        )

    return render(request, 'pesquisasSatisfacao/avaliacao_coordenacao_monitoria.html', {
        'form': form,
        'avaliacao_formset': avaliacao_formset,
        'destaque_formset': destaque_formset,
        'desempenho_formset': desempenho_formset,
    })
