from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from ordemDeServico.models import OrdemDeServico
from peraltas.models import EscalaAcampamento, AtividadesEco
from pesquisasSatisfacao.forms_coordenadores import CoordenacaoAvaliandoMonitoriaForm, AvaliacaoIndividualMonitorForm, \
    DestaqueAtividadesForm, DesempenhoAcimaMediaForm
from pesquisasSatisfacao.forms_escolas import AvaliacaoColegioForm, AvaliacaoIndividualAtividadeForm
from pesquisasSatisfacao.forms_monitores import MonitoriaAvaliandoCoordenacaoForm, AvaliacaoIndividualCoordenadorForm
from pesquisasSatisfacao.models import AvaliacaoIndividualMonitor, DestaqueAtividades, DesempenhoAcimaMedia, \
    MonitorAvaliandoCoordenacao, AvaliacaoIndividualCoordenador, AvaliacaoIndividualAtividade


@login_required(login_url='login')
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
                    form.save_m2m()

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
                messages.error(
                    request,
                    f'Aconteceu um erro durante o salvamento da avaliação ({e}). Por favor tente novamente mais tade!'
                )
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

    return render(request, 'pesquisasSatisfacao/avaliacao_coordenacao_monitoria.html', {
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
    })


@login_required(login_url='login')
def avaliacao_monitoria_coordenacao(request, id_ordem_de_servico):
    ordem = get_object_or_404(OrdemDeServico, pk=id_ordem_de_servico)
    escala = get_object_or_404(EscalaAcampamento, ficha_de_evento=ordem.ficha_de_evento)
    coordenadores = ordem.monitor_responsavel.all().order_by('usuario__first_name')

    if request.method == 'POST':
        form = MonitoriaAvaliandoCoordenacaoForm(request.POST)
        AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
            AvaliacaoIndividualCoordenador,
            form=AvaliacaoIndividualCoordenadorForm,
            extra=0,
        )
        avaliacao = AvaliacaoIndividualCoordenadorFormSet(
            request.POST,
            queryset=AvaliacaoIndividualCoordenador.objects.none(),
            prefix='avaliacao'
        )

        if form.is_valid() and avaliacao.is_valid():
            try:
                with transaction.atomic():
                    # 1. Salva a pesquisa (qualquer um dos modelos permitidos)
                    pesquisa = form.save(commit=False)
                    pesquisa.save()

                    # 2. Obtém o ContentType da pesquisa dinamicamente
                    content_type = ContentType.objects.get_for_model(pesquisa)

                    # 3. Salva as avaliações individuais
                    avaliacoes = avaliacao.save(commit=False)  # Assumindo que `avaliacao` é um formset
                    for avaliacao_obj in avaliacoes:
                        # Atribui os campos do GenericForeignKey
                        avaliacao_obj.content_type = content_type  # Define o modelo relacionado
                        avaliacao_obj.object_id = pesquisa.id  # Define o ID do objeto
                        avaliacao_obj.save()

            except Exception as e:
                messages.error(
                    request,
                    f'Aconteceu um erro durante o salvamento da avaliação ({e}). Por favor tente novamente mais tade!'
                )
            else:
                escala.avaliou_coordenadores.add(request.user.monitor.id)
                messages.success(request, 'Pesquisa enviada com sucesso!')

                return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = MonitoriaAvaliandoCoordenacaoForm(
            initial={
                'ordem_de_servico': ordem,
                'monitor': request.user,
                'escala_peraltas': escala,
            },
        )

        AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
            AvaliacaoIndividualCoordenador,
            form=AvaliacaoIndividualCoordenadorForm,
            extra=len(coordenadores),
        )
        avaliacao = AvaliacaoIndividualCoordenadorFormSet(
            queryset=AvaliacaoIndividualCoordenador.objects.none(),
            initial=[{'coordenador': coordenador.id} for coordenador in coordenadores],
            prefix='avaliacao'
        )

    return render(request, 'pesquisasSatisfacao/avaliacao_monitoria_coordenacao.html', {
        'form': form,
        'avaliacao_formset': avaliacao,
        'ordem': ordem,
        'campos_nao_tabelaveis': [
            'palavra_1',
            'palavra_2',
            'palavra_3',
            'palavra_4',
            'palavra_5',
            'palavras_chave',
            'tem_consideracoes_pedagogicas',
            'teve_briefing',
            'teve_feedback',
            'coordenador_participou',
        ]
    })


@login_required(login_url='login')
def avaliacao_colegio(request, id_ordem_de_servico):
    ordem = get_object_or_404(OrdemDeServico, pk=id_ordem_de_servico)
    escala = get_object_or_404(EscalaAcampamento, ficha_de_evento=ordem.ficha_de_evento)
    coordenadores = ordem.monitor_responsavel.all().order_by('usuario__first_name')
    dados_iniciais = []

    if request.method == 'POST':
        form = AvaliacaoColegioForm(request.POST)
        AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
            AvaliacaoIndividualCoordenador,
            form=AvaliacaoIndividualCoordenadorForm,
            extra=0,
        )
        avaliacao_coordenadores = AvaliacaoIndividualCoordenadorFormSet(
            request.POST,
            queryset=AvaliacaoIndividualCoordenador.objects.none(),
            prefix='avaliacao_coordenadores'
        )
        AvaliacaoIndividualatividadeFormSet = modelformset_factory(
            AvaliacaoIndividualAtividade,
            form=AvaliacaoIndividualAtividadeForm,
            extra=0,
        )
        avaliacao_atividades = AvaliacaoIndividualatividadeFormSet(
            request.POST,
            queryset=AvaliacaoIndividualAtividade.objects.none(),
            prefix='avaliacao_atividade'
        )

        print(avaliacao_atividades.errors)
        print(avaliacao_coordenadores.errors)
        if form.is_valid() and avaliacao_coordenadores.is_valid() and avaliacao_atividades.is_valid():
            try:
                with transaction.atomic():
                    # 1. Salva a pesquisa (qualquer um dos modelos permitidos)
                    pesquisa = form.save(commit=False)
                    pesquisa.save()

                    # 2. Obtém o ContentType da pesquisa dinamicamente
                    content_type = ContentType.objects.get_for_model(pesquisa)

                    # 3. Salva as avaliações individuais
                    avaliacoes = avaliacao_coordenadores.save(commit=False)

                    for avaliacao_obj in avaliacoes:
                        # Atribui os campos do GenericForeignKey
                        avaliacao_obj.content_type = content_type  # Define o modelo relacionado
                        avaliacao_obj.object_id = pesquisa.id  # Define o ID do objeto
                        avaliacao_obj.save()

                    # 4. Salva as avaliações das atividades
                    avaliacoes_atividade = avaliacao_atividades.save(commit=False)

                    for avaliacao_ativ_obj in avaliacoes_atividade:
                        # Atribui os campos do GenericForeignKey
                        avaliacao_ativ_obj.pesquisa_content_type = content_type
                        avaliacao_ativ_obj.pesquisa_object_id = pesquisa.id
                        avaliacao_ativ_obj.save()

            except Exception as e:
                messages.error(
                    request,
                    f'Aconteceu um erro durante o salvamento da avaliação ({e}). Por favor tente novamente mais tade!'
                )
            else:
                escala.avaliou_coordenadores.add(request.user.monitor.id)
                messages.success(request, 'Pesquisa enviada com sucesso!')

                return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AvaliacaoColegioForm(
            initial={
                'ordem_de_servico': ordem,
                'avaliador': ordem.ficha_de_evento.responsavel_evento,
                'escala_peraltas': escala,
            },
            refeicoes_realizadas=ordem.ficha_de_evento.refeicoes_realizadas,
        )

        AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
            AvaliacaoIndividualCoordenador,
            form=AvaliacaoIndividualCoordenadorForm,
            extra=len(coordenadores),
        )
        avaliacao_coordenadores = AvaliacaoIndividualCoordenadorFormSet(
            queryset=AvaliacaoIndividualCoordenador.objects.none(),
            initial=[{'coordenador': coordenador.id} for coordenador in coordenadores],
            prefix='avaliacao_coordenadores'
        )

        dados_iniciais.extend(AvaliacaoIndividualAtividade.process_atividades(ordem.atividades_eco, AtividadesEco))
        AvaliacaoIndividualatividadeFormSet = modelformset_factory(
            AvaliacaoIndividualAtividade,
            form=AvaliacaoIndividualAtividadeForm,
            extra=len(dados_iniciais),
        )
        avaliacao_atividades = AvaliacaoIndividualatividadeFormSet(
            queryset=AvaliacaoIndividualAtividade.objects.none(),
            initial=dados_iniciais,
            prefix='avaliacao_atividade'
        )

    return render(request, 'pesquisasSatisfacao/avaliacao_colegios.html', {
        'form': form,
        'avaliacao_coordenadores_formset': avaliacao_coordenadores,
        'avaliacao_atividades_formset': avaliacao_atividades,
        'ordem': ordem,
        'campos_nao_tabelaveis': [
            'destaque',
            'sugestoes',
            'motivo_trazer_grupo',
            'outros_motivos',
            'material_divigulgacao',
            'interesse_hospedar_com_familia',
        ]
    })


def avaliacao_corporativo(request, id_ordem_de_servico):
    ...
