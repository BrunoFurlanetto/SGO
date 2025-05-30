from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from ceu.models import Locaveis
from ordemDeServico.models import OrdemDeServico
from peraltas.models import EscalaAcampamento, AtividadesEco
from pesquisasSatisfacao.forms_coordenadores import CoordenacaoAvaliandoMonitoriaForm, AvaliacaoIndividualMonitorForm, \
    DestaqueAtividadesForm, DesempenhoAcimaMediaForm
from pesquisasSatisfacao.forms_corporativo import AvaliacaoCorporativoForm, AvaliacaoIndividualSalaForm
from pesquisasSatisfacao.forms_escolas import AvaliacaoColegioForm, AvaliacaoIndividualAtividadeForm
from pesquisasSatisfacao.forms_monitores import MonitoriaAvaliandoCoordenacaoForm, AvaliacaoIndividualCoordenadorForm
from pesquisasSatisfacao.models import AvaliacaoIndividualMonitor, DestaqueAtividades, DesempenhoAcimaMedia, \
    MonitorAvaliandoCoordenacao, AvaliacaoIndividualCoordenador, AvaliacaoIndividualAtividade, AvaliacaoIndividualSala, \
    AvaliacaoColegio, AvaliacaoCorporativo, CoordenacaoAvaliandoMonitoria


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
                ordem.cliente_avaliou = True
                ordem.save()
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
                'nome_avaliador': ordem.responsavel_grupo,
                'cargo_avaliador': ordem.ficha_de_evento.responsavel_evento.listar_cargos,
                'telefone_avaliador': ordem.ficha_de_evento.responsavel_evento.fone,
                'email_avaliador': ordem.ficha_de_evento.responsavel_evento.email_responsavel_evento,
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
            'nome_avaliador',
            'cargo_avaliador',
            'telefone_avaliador',
            'email_avaliador',
        ]
    })


def avaliacao_corporativo(request, id_ordem_de_servico):
    ordem = get_object_or_404(OrdemDeServico, pk=id_ordem_de_servico)
    coordenadores = ordem.monitor_responsavel.all().order_by('usuario__first_name')
    dados_iniciais = []

    try:
        escala = EscalaAcampamento.objects.get(ficha_de_evento=ordem.ficha_de_evento)
    except EscalaAcampamento.DoesNotExist:
        escala = None

    if request.method == 'POST':
        form = AvaliacaoCorporativoForm(request.POST)
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
        AvaliacaoIndividualSalaFormSet = modelformset_factory(
            AvaliacaoIndividualSala,
            form=AvaliacaoIndividualSalaForm,
            extra=0,
        )
        avaliacao_salas = AvaliacaoIndividualSalaFormSet(
            request.POST,
            queryset=AvaliacaoIndividualSala.objects.none(),
            prefix='avaliacao_sala'
        )

        if form.is_valid() and avaliacao_coordenadores.is_valid() and avaliacao_salas.is_valid():
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
                    avaliacoes_atividade = avaliacao_salas.save(commit=False)

                    for avaliacao_sala_obj in avaliacoes_atividade:
                        # Atribui os campos do GenericForeignKey
                        avaliacao_sala_obj.pesquisa_corporativo_content_type = content_type
                        avaliacao_sala_obj.pesquisa_corporativo_object_id = pesquisa.id
                        avaliacao_sala_obj.save()

            except Exception as e:
                messages.error(
                    request,
                    f'Aconteceu um erro durante o salvamento da avaliação ({e}). Por favor tente novamente mais tade!'
                )
            else:
                ordem.cliente_avaliou = True
                ordem.save()
                messages.success(request, 'Pesquisa enviada com sucesso!')

                return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AvaliacaoCorporativoForm(
            initial={
                'ordem_de_servico': ordem,
                'avaliador': ordem.ficha_de_evento.responsavel_evento,
                'escala_peraltas': escala,
                'nome_avaliador': ordem.responsavel_grupo,
                'cargo_avaliador': ordem.ficha_de_evento.responsavel_evento.listar_cargos,
                'telefone_avaliador': ordem.ficha_de_evento.responsavel_evento.fone,
                'email_avaliador': ordem.ficha_de_evento.responsavel_evento.email_responsavel_evento,
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

        dados_iniciais.extend(AvaliacaoIndividualSala.process_salas(ordem.locacao_ceu, Locaveis))
        AvaliacaoIndividualSalaFormSet = modelformset_factory(
            AvaliacaoIndividualSala,
            form=AvaliacaoIndividualSalaForm,
            extra=len(dados_iniciais),
        )
        avaliacao_salas = AvaliacaoIndividualSalaFormSet(
            queryset=AvaliacaoIndividualAtividade.objects.none(),
            initial=dados_iniciais,
            prefix='avaliacao_sala'
        )

    return render(request, 'pesquisasSatisfacao/avaliacao_corporativo.html', {
        'form': form,
        'avaliacao_coordenadores_formset': avaliacao_coordenadores,
        'avaliacao_salas_formset': avaliacao_salas,
        'ordem': ordem,
        'campos_nao_tabelaveis': [
            'mais_valorizou',
            'sugestoes',
            'material_divigulgacao',
            'interesse_hospedar_com_familia',
            'nome_avaliador',
            'cargo_avaliador',
            'telefone_avaliador',
            'email_avaliador',
        ]
    })


@login_required(login_url='login')
def ver_avaliacao_colegio(request, id_avaliacao):
    avaliacao = get_object_or_404(AvaliacaoColegio, pk=id_avaliacao)
    ordem = get_object_or_404(OrdemDeServico, pk=avaliacao.ordem_de_servico.pk)
    content_type = ContentType.objects.get_for_model(AvaliacaoColegio)

    # Form principal preenchido com instância, não com initial
    form = AvaliacaoColegioForm(instance=avaliacao)

    # Desabilita todos os campos do form
    for field in form.fields.values():
        field.disabled = True

    # Coordenadores
    coordenadores_qs = AvaliacaoIndividualCoordenador.objects.filter(content_type=content_type, object_id=avaliacao.pk)
    AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
        AvaliacaoIndividualCoordenador,
        form=AvaliacaoIndividualCoordenadorForm,
        extra=0,
        can_delete=False
    )
    avaliacao_coordenadores = AvaliacaoIndividualCoordenadorFormSet(
        queryset=coordenadores_qs,
        prefix='avaliacao_coordenadores'
    )
    for formset_form in avaliacao_coordenadores:
        for field in formset_form.fields.values():
            field.disabled = True

    # Atividades
    atividades_qs = AvaliacaoIndividualAtividade.objects.filter(
        pesquisa_content_type=content_type,
        pesquisa_object_id=avaliacao.pk
    )
    AvaliacaoIndividualatividadeFormSet = modelformset_factory(
        AvaliacaoIndividualAtividade,
        form=AvaliacaoIndividualAtividadeForm,
        extra=0,
        can_delete=False
    )
    avaliacao_atividades = AvaliacaoIndividualatividadeFormSet(
        queryset=atividades_qs,
        prefix='avaliacao_atividade'
    )
    for formset_form in avaliacao_atividades:
        for field in formset_form.fields.values():
            field.disabled = True

    return render(request, 'pesquisasSatisfacao/avaliacao_colegios.html', {
        'form': form,
        'avaliacao_coordenadores_formset': avaliacao_coordenadores,
        'avaliacao_atividades_formset': avaliacao_atividades,
        'ordem': ordem,
        'visualizacao': True,  # Flag para template tratar como visualização
        'campos_nao_tabelaveis': [
            'destaque',
            'sugestoes',
            'motivo_trazer_grupo',
            'outros_motivos',
            'material_divigulgacao',
            'interesse_hospedar_com_familia',
            'nome_avaliador',
            'cargo_avaliador',
            'telefone_avaliador',
            'email_avaliador',
        ]
    })


@login_required(login_url='login')
def ver_avaliacao_corporativo(request, id_avaliacao):
    avaliacao = get_object_or_404(AvaliacaoCorporativo, pk=id_avaliacao)
    ordem = get_object_or_404(OrdemDeServico, pk=avaliacao.ordem_de_servico.pk)
    content_type = ContentType.objects.get_for_model(AvaliacaoCorporativo)

    # Form principal preenchido com instância, não com initial
    form = AvaliacaoCorporativoForm(instance=avaliacao)

    # Desabilita todos os campos do form
    for field in form.fields.values():
        field.disabled = True

    # Coordenadores
    coordenadores_qs = AvaliacaoIndividualCoordenador.objects.filter(content_type=content_type, object_id=avaliacao.pk)
    AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
        AvaliacaoIndividualCoordenador,
        form=AvaliacaoIndividualCoordenadorForm,
        extra=0,
        can_delete=False
    )
    avaliacao_coordenadores = AvaliacaoIndividualCoordenadorFormSet(
        queryset=coordenadores_qs,
        prefix='avaliacao_coordenadores'
    )
    for formset_form in avaliacao_coordenadores:
        for field in formset_form.fields.values():
            field.disabled = True

    # Atividades
    salas_qs = AvaliacaoIndividualSala.objects.filter(
        pesquisa_corporativo_content_type=content_type,
        pesquisa_corporativo_object_id=avaliacao.pk
    )
    AvaliacaoIndividualSalaFormSet = modelformset_factory(
        AvaliacaoIndividualSala,
        form=AvaliacaoIndividualSalaForm,
        extra=0,
        can_delete=False
    )
    avaliacao_salas = AvaliacaoIndividualSalaFormSet(
        queryset=salas_qs,
        prefix='avaliacao_salas'
    )
    for formset_form in avaliacao_salas:
        for field in formset_form.fields.values():
            field.disabled = True

    return render(request, 'pesquisasSatisfacao/avaliacao_corporativo.html', {
        'form': form,
        'avaliacao_coordenadores_formset': avaliacao_coordenadores,
        'avaliacao_salas_formset': avaliacao_salas,
        'ordem': ordem,
        'visualizacao': True,  # Flag para template tratar como visualização
        'campos_nao_tabelaveis': [
            'mais_valorizou',
            'sugestoes',
            'material_divigulgacao',
            'interesse_hospedar_com_familia',
            'nome_avaliador',
            'cargo_avaliador',
            'telefone_avaliador',
            'email_avaliador',
        ]
    })


@login_required(login_url='login')
def ver_avaliacao_monitores(request, id_avaliacao):
    pesquisa = get_object_or_404(CoordenacaoAvaliandoMonitoria, pk=id_avaliacao)
    ordem = pesquisa.ordem_de_servico
    escala = get_object_or_404(EscalaAcampamento, ficha_de_evento=ordem.ficha_de_evento)
    monitores = escala.monitores_acampamento.all().exclude(usuario=request.user).order_by('usuario__first_name')

    # Formulário principal com dados e campos desabilitados
    form = CoordenacaoAvaliandoMonitoriaForm(instance=pesquisa, monitores=monitores)
    for field in form.fields.values():
        field.disabled = True

    # Formset Avaliação Individual Monitor
    AvaliacaoIndividualMonitorFormSet = modelformset_factory(
        AvaliacaoIndividualMonitor,
        form=AvaliacaoIndividualMonitorForm,
        extra=0,
    )
    avaliacao_qs = AvaliacaoIndividualMonitor.objects.filter(avaliacao_geral=pesquisa.id)
    avaliacao = AvaliacaoIndividualMonitorFormSet(queryset=avaliacao_qs, prefix='avaliacao')
    for formset_form in avaliacao:
        for field in formset_form.fields.values():
            field.disabled = True

    # Formset Destaque Atividades
    DestaqueAtividadesFormSet = modelformset_factory(
        DestaqueAtividades,
        form=DestaqueAtividadesForm,
        extra=0,
    )
    destaque_qs = DestaqueAtividades.objects.filter(avaliacao=pesquisa.id)
    destaque = DestaqueAtividadesFormSet(queryset=destaque_qs, prefix='destaques', form_kwargs={'monitores': monitores})
    for formset_form in destaque:
        for field in formset_form.fields.values():
            field.disabled = True

    # Formset Desempenho Acima da Média
    DesempenhoAcimaMediaFormSet = modelformset_factory(
        DesempenhoAcimaMedia,
        form=DesempenhoAcimaMediaForm,
        extra=0,
    )
    desempenho_qs = DesempenhoAcimaMedia.objects.filter(avaliacao=pesquisa)
    desempenho = DesempenhoAcimaMediaFormSet(queryset=desempenho_qs, prefix='desempenho',
                                             form_kwargs={'monitores': monitores})
    for formset_form in desempenho:
        for field in formset_form.fields.values():
            field.disabled = True

    return render(request, 'pesquisasSatisfacao/avaliacao_coordenacao_monitoria.html', {
        'form': form,
        'avaliacao_formset': avaliacao,
        'destaque_formset': destaque,
        'desempenho_formset': desempenho,
        'ordem': ordem,
        'monitores': monitores,
        'visualizacao': True,
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


def ver_avaliacao_coordenadores(request, id_avaliacao):
    # Busca a avaliação (modelo CoordenacaoAvaliandoMonitoria, ou o seu modelo correto) pelo ID
    pesquisa = get_object_or_404(MonitorAvaliandoCoordenacao, pk=id_avaliacao)

    # Obtém a ordem e a escala relacionados para contexto
    ordem = pesquisa.ordem_de_servico
    escala = get_object_or_404(EscalaAcampamento, ficha_de_evento=ordem.ficha_de_evento)
    coordenadores = ordem.monitor_responsavel.all().order_by('usuario__first_name')

    # Form principal desabilitado (somente leitura)
    form = MonitoriaAvaliandoCoordenacaoForm(instance=pesquisa)
    for field in form.fields.values():
        field.disabled = True

    # Formset das avaliações individuais do coordenador, desabilitado também
    AvaliacaoIndividualCoordenadorFormSet = modelformset_factory(
        AvaliacaoIndividualCoordenador,
        form=AvaliacaoIndividualCoordenadorForm,
        extra=0,
    )
    avaliacao_qs = AvaliacaoIndividualCoordenador.objects.filter(
        content_type=ContentType.objects.get_for_model(pesquisa),
        object_id=pesquisa.id
    )
    avaliacao = AvaliacaoIndividualCoordenadorFormSet(queryset=avaliacao_qs, prefix='avaliacao')
    for formset_form in avaliacao:
        for field in formset_form.fields.values():
            field.disabled = True

    return render(request, 'pesquisasSatisfacao/avaliacao_monitoria_coordenacao.html', {
        'form': form,
        'avaliacao_formset': avaliacao,
        'ordem': ordem,
        'visualizacao': True,
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
