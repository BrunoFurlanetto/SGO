from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from ordemDeServico.models import OrdemDeServico
from peraltas.models import EscalaAcampamento
from pesquisasSatisfacao.forms import CoordenacaoAvaliandoMonitoriaForm, AvaliacaoIndividualMonitorForm, \
    DestaqueAtividadesForm, DesempenhoAcimaMediaForm, DestaqueAtividadesFormSet
from pesquisasSatisfacao.models import AvaliacaoIndividualMonitor, DestaqueAtividades, DesempenhoAcimaMedia


def avaliacao_coordenacao_monitoria(request, id_ordem_de_servico):
    ordem = get_object_or_404(OrdemDeServico, pk=id_ordem_de_servico)
    escala = get_object_or_404(EscalaAcampamento, ficha_de_evento=ordem.ficha_de_evento)
    monitores = escala.monitores_acampamento.all().order_by('usuario__first_name')

    if request.method == 'POST':
        form = CoordenacaoAvaliandoMonitoriaForm(request.POST)
        avaliacao = AvaliacaoIndividualMonitorForm(request.POST)
        destaque = DestaqueAtividadesForm(request.POST)
        desempenho = DesempenhoAcimaMediaForm(request.POST)

        if form.is_valid() and avaliacao.is_valid() and destaque.is_valid() and desempenho.is_valid():
            pesquisa = form.save(commit=False)
            pesquisa.save()

            # Salva avaliações individuais
            avaliacoes = avaliacao.save(commit=False)

            for avaliacao in avaliacoes:
                avaliacao.avaliacao_geral = pesquisa
                avaliacao.save()

            messages.success(request, 'Pesquisa enviada com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CoordenacaoAvaliandoMonitoriaForm(
            initial={
                'ordem_de_servico': ordem,
                'coordenador': request.user,
                'escala_peraltas': escala,
            }
        )
        monitores = escala.monitores_acampamento.all()
        AvaliacaoIndividualMonitorFormSet = modelformset_factory(
            AvaliacaoIndividualMonitor,
            form=AvaliacaoIndividualMonitorForm,
            extra=0,  # Só mostra os monitores existentes
        )
        avaliacao = AvaliacaoIndividualMonitorFormSet(
            queryset=monitores,
            initial=[{'monitor': monitor.id} for monitor in monitores],
            prefix='avaliacao'
        )

        DestaqueAtividadesFormSet = modelformset_factory(
            DestaqueAtividades,  # Substitua pelo seu modelo
            form=DestaqueAtividadesForm,
            extra=1,  # Número de forms vazios (ajuste conforme necessário)
        )
        destaque = DestaqueAtividadesFormSet(
            queryset=DestaqueAtividades.objects.none(),  # Ou um queryset específico
            initial=[{'posicao': 1}],
            form_kwargs={'escala': escala},  # Passa a escala para cada form
            prefix='destaques'
        )
        desempenho = DesempenhoAcimaMediaForm()

    context = {
        'form': form,
        'avaliacao_formset': avaliacao,
        'destaque_formset': destaque,
        'desempenho_formset': desempenho,
        'ordem': ordem,
        'monitores': monitores,
    }

    return render(request, 'pesquisasSatisfacao/avaliacao_coordenacao_monitoria.html', context)
