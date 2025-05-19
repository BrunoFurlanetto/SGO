from django.contrib import messages
from django.db import transaction
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
    monitores = escala.monitores_acampamento.all().exclude(usuario=request.user).order_by('usuario__first_name')

    if request.method == 'POST':
        form = CoordenacaoAvaliandoMonitoriaForm(request.POST)
        AvaliacaoIndividualMonitorFormSet = modelformset_factory(
            AvaliacaoIndividualMonitor,
            form=AvaliacaoIndividualMonitorForm,
            extra=0,
        )
        avaliacao = AvaliacaoIndividualMonitorFormSet(
            request.POST,
            queryset=AvaliacaoIndividualMonitor.objects.none(),
            prefix='avaliacao'
        )

        DestaqueAtividadesFormSet = modelformset_factory(
            DestaqueAtividades,
            form=DestaqueAtividadesForm,
            extra=1,
        )
        destaque = DestaqueAtividadesFormSet(
            request.POST,
            queryset=DestaqueAtividades.objects.none(),
            form_kwargs={'monitores': monitores},
            prefix='destaques'
        )

        DesempenhoAcimaMediaFormSet = modelformset_factory(
            DesempenhoAcimaMedia,
            form=DesempenhoAcimaMediaForm,
            extra=1,
        )
        desempenho = DesempenhoAcimaMediaFormSet(
            request.POST,
            queryset=DesempenhoAcimaMedia.objects.none(),
            form_kwargs={'monitores': monitores},
            prefix='desempenho'
        )

        if form.is_valid() and avaliacao.is_valid() and destaque.is_valid() and desempenho.is_valid():
            try:
                with transaction.atomic():
                    pesquisa = form.save(commit=False)
                    pesquisa.save()

                    # Salva avaliações individuais
                    avaliacoes = avaliacao.save(commit=False)
                    for avaliacao_obj in avaliacoes:
                        avaliacao_obj.avaliacao_geral = pesquisa
                        avaliacao_obj.save()

                    # Salva destaques
                    destaques = destaque.save(commit=False)
                    for destaque_obj in destaques:
                        destaque_obj.avaliacao = pesquisa
                        destaque_obj.save()

                    # Salva desempenhos acima da média
                    desempenhos = desempenho.save(commit=False)
                    for desempenho_obj in desempenhos:
                        desempenho_obj.avaliacao = pesquisa
                        desempenho_obj.save()
            except Exception as e:
                messages.error(request, f'Aconteceu um erro durante o salvamento da avaliação ({e}). Por favor tente novamente mais tade!')
            else:
                ordem.avaliou_monitoria.add(request.user.monitor.id)
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
            },
            monitores=monitores
        )

        AvaliacaoIndividualMonitorFormSet = modelformset_factory(
            AvaliacaoIndividualMonitor,
            form=AvaliacaoIndividualMonitorForm,
            extra=len(monitores),
        )
        avaliacao = AvaliacaoIndividualMonitorFormSet(
            queryset=AvaliacaoIndividualMonitor.objects.none(),
            initial=[{'monitor': monitor.id} for monitor in monitores if monitor.usuario != request.user],
            prefix='avaliacao'
        )

        DestaqueAtividadesFormSet = modelformset_factory(
            DestaqueAtividades,
            form=DestaqueAtividadesForm,
            extra=1,
        )
        destaque = DestaqueAtividadesFormSet(
            queryset=DestaqueAtividades.objects.none(),
            initial=[{'posicao': 1}],
            form_kwargs={'monitores': monitores},
            prefix='destaques'
        )

        DesempenhoAcimaMediaFormSet = modelformset_factory(
            DesempenhoAcimaMedia,
            form=DesempenhoAcimaMediaForm,
            extra=1,
        )
        desempenho = DesempenhoAcimaMediaFormSet(
            queryset=DesempenhoAcimaMedia.objects.none(),
            initial=[{'posicao': 1}],
            form_kwargs={'monitores': monitores},
            prefix='desempenho'
        )

    context = {
        'form': form,
        'avaliacao_formset': avaliacao,
        'destaque_formset': destaque,
        'desempenho_formset': desempenho,
        'ordem': ordem,
        'monitores': monitores,
        'campos_nao_tabelaveis': [
            'observacoes_equipe',
            'palavras_descricao',
            'palavra_1',
            'palavra_2',
            'palavra_3',
            'palavra_4',
            'palavra_5',
            'monitores_destaque_pedagogicas',
            'monitores_destaque_evento',
        ]
    }

    return render(request, 'pesquisasSatisfacao/avaliacao_coordenacao_monitoria.html', context)
