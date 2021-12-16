from django.shortcuts import render, redirect
from .models import OrdemDeServico, Professores, Atividades, FormularioOrdem, Tipo


def publico(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    atividades = Atividades.objects.all()
    rangei = range(1, 6)
    rangej = range(1, 5)

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {'professores': professores, 'rangei': rangei,
                                                         'rangej': rangej, 'atividades': atividades})
    else:
        tipo = Tipo.objects.get(pk=1)
        coordenador = Professores.objects.get(nome=request.POST.get('coordenador'))
        participantes_previa = request.POST.get('previaParticipantes')
        participantes_confirmados = request.POST.get('participantes')
        data_atendimento = request.POST.get('dataAtendimento')
        professor_2 = Professores.objects.get(nome=request.POST.get('prf2'))
        professor_3 = None if request.POST.get('prf3') == '' else Professores.objects.get(
            nome=request.POST.get('prf3'))
        professor_4 = None if request.POST.get('prf4') == '' else Professores.objects.get(
            nome=request.POST.get('prf4'))
        hora_entrada = request.POST.get('horaEntrada')

        # ------------------------------ TESTES PARA ATIVIDADE 1 -----------------------------------------
        atividade_1 = Atividades.objects.get(atividade=request.POST.get('ativ1'))
        hora_atividade_1 = request.POST.get('horaAtividade_1')
        prf_1_atv_1 = Professores.objects.get(nome=request.POST.get('prf1atv1'))
        prf_2_atv_1 = None if request.POST.get('prf2atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf2atv1'))
        prf_3_atv_1 = None if request.POST.get('prf3atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf3atv1'))
        prf_4_atv_1 = None if request.POST.get('prf4atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf4atv1'))

        # ------------------------------ TESTES PARA ATIVIDADE 2 -----------------------------------------
        atividade_2 = Atividades.objects.get(atividade=request.POST.get('ativ2'))
        hora_atividade_2 = request.POST.get('horaAtividade_2')
        prf_1_atv_2 = Professores.objects.get(nome=request.POST.get('prf1atv2'))
        prf_2_atv_2 = None if request.POST.get('prf2atv2') == '' else Professores.objects.get(
            nome=request.POST.get('prf2atv2'))
        prf_3_atv_2 = None if request.POST.get('prf3atv2') == '' else Professores.objects.get(
            nome=request.POST.get('prf3atv1'))
        prf_4_atv_2 = None if request.POST.get('prf4atv2') == '' else Professores.objects.get(
            nome=request.POST.get('prf4atv1'))

        # ------------------------------ TESTES PARA ATIVIDADE 3 -----------------------------------------
        if request.POST.get('ativ3') != '':
            atividade_3 = Atividades.objects.get(atividade=request.POST.get('ativ3'))
            hora_atividade_3 = request.POST.get('horaAtividade_3')
            prf_1_atv_3 = Professores.objects.get(nome=request.POST.get('prf1atv3'))
            prf_2_atv_3 = None if request.POST.get('prf2atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv3'))
            prf_3_atv_3 = None if request.POST.get('prf3atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv3'))
            prf_4_atv_3 = None if request.POST.get('prf4atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv3'))
        else:
            atividade_3 = hora_atividade_3 = prf_1_atv_3 = prf_2_atv_3 = prf_3_atv_3 = prf_4_atv_3 = None

        # ------------------------------ TESTES PARA ATIVIDADE 4 -----------------------------------------
        if request.POST.get('ativ4') != '':
            atividade_4 = Atividades.objects.get(atividade=request.POST.get('ativ4'))
            hora_atividade_4 = request.POST.get('horaAtividade_4')
            prf_1_atv_4 = Professores.objects.get(nome=request.POST.get('prf1atv4'))
            prf_2_atv_4 = None if request.POST.get('prf2atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv4'))
            prf_3_atv_4 = None if request.POST.get('prf3atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv4'))
            prf_4_atv_4 = None if request.POST.get('prf4atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv4'))
        else:
            atividade_4 = hora_atividade_4 = prf_1_atv_4 = prf_2_atv_4 = prf_3_atv_4 = prf_4_atv_4 = None

        # ------------------------------ TESTES PARA ATIVIDADE 5 -----------------------------------------
        if request.POST.get('ativ5') == '':
            atividade_5 = Atividades.objects.get(atividade=request.POST.get('ativ5'))
            hora_atividade_5 = request.POST.get('horaAtividade_5')
            prf_1_atv_5 = Professores.objects.get(nome=request.POST.get('prf1atv5'))
            prf_2_atv_5 = None if request.POST.get('prf2atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv5'))
            prf_3_atv_5 = None if request.POST.get('prf3atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv5'))
            prf_4_atv_5 = None if request.POST.get('prf4atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv5'))
        else:
            atividade_5 = hora_atividade_5 = prf_1_atv_5 = prf_2_atv_5 = prf_3_atv_5 = prf_4_atv_5 = None

        relatorio = request.POST.get('relatorio')

        os = OrdemDeServico.objects.create(tipo=tipo, coordenador=coordenador,
                                           participantes_previa=participantes_previa,
                                           participantes_confirmados=participantes_confirmados,
                                           data_atendimento=data_atendimento,
                                           professor_2=professor_2, professor_3=professor_3, professor_4=professor_4,
                                           hora_entrada=hora_entrada, atividade_1=atividade_1,
                                           hora_atividade_1=hora_atividade_1,
                                           prf_1_atv_1=prf_1_atv_1, prf_2_atv_1=prf_2_atv_1, prf_3_atv_1=prf_3_atv_1,
                                           prf_4_atv_1=prf_4_atv_1, atividade_2=atividade_2,
                                           hora_atividade_2=hora_atividade_2,
                                           prf_1_atv_2=prf_1_atv_2, prf_2_atv_2=prf_2_atv_2, prf_3_atv_2=prf_3_atv_2,
                                           prf_4_atv_2=prf_4_atv_2, atividade_3=atividade_3,
                                           hora_atividade_3=hora_atividade_3,
                                           prf_1_atv_3=prf_1_atv_3, prf_2_atv_3=prf_2_atv_3, prf_3_atv_3=prf_3_atv_3,
                                           prf_4_atv_3=prf_4_atv_3, atividade_4=atividade_4,
                                           hora_atividade_4=hora_atividade_4,
                                           prf_1_atv_4=prf_1_atv_4, prf_2_atv_4=prf_2_atv_4, prf_3_atv_4=prf_3_atv_4,
                                           prf_4_atv_4=prf_4_atv_4, atividade_5=atividade_5,
                                           hora_atividade_5=hora_atividade_5,
                                           prf_1_atv_5=prf_1_atv_5, prf_2_atv_5=prf_2_atv_5, prf_3_atv_5=prf_3_atv_5,
                                           prf_4_atv_5=prf_4_atv_5, relatorio=relatorio)
        os.save()
        return redirect('dashboard')


def colegio(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    atividades = Atividades.objects.all()
    rangei = range(1, 6)
    rangej = range(1, 5)

    if request.method != 'POST':
        return render(request, 'cadastro/colegio.html', {'professores': professores, 'rangei': rangei,
                                                         'rangej': rangej, 'atividades': atividades})
    else:
        tipo = Tipo.objects.get(pk=2)
        instituicao = request.POST.get('instituicao')
        responsaveis = None if request.POST.get('responsaveis') == '' else request.POST.get('responsaveis')
        serie = None if request.POST.get('serie') == '' else request.POST.get('serie')
        coordenador_peraltas = None if request.POST.get('coordenadorPeraltas') == '' else request.POST.get(
            'coordenadorPeraltas')
        coordenador = Professores.objects.get(nome=request.POST.get('coordenador'))
        participantes_previa = request.POST.get('previaParticipantes')
        participantes_confirmados = request.POST.get('participantes')
        data_atendimento = request.POST.get('dataAtendimento')
        professor_2 = None if request.POST.get('prf2') == '' else Professores.objects.get(
            nome=request.POST.get('prf2'))
        professor_3 = None if request.POST.get('prf3') == '' else Professores.objects.get(
            nome=request.POST.get('prf3'))
        professor_4 = None if request.POST.get('prf4') == '' else Professores.objects.get(
            nome=request.POST.get('prf4'))
        hora_entrada = None if request.POST.get('horaEntrada') == '' else request.POST.get('horaEntrada')

        # ------------------------------ TESTES PARA ATIVIDADE 1 -----------------------------------------
        atividade_1 = Atividades.objects.get(atividade=request.POST.get('ativ1'))
        hora_atividade_1 = request.POST.get('horaAtividade_1')
        prf_1_atv_1 = Professores.objects.get(nome=request.POST.get('prf1atv1'))
        prf_2_atv_1 = None if request.POST.get('prf2atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf2atv1'))
        prf_3_atv_1 = None if request.POST.get('prf3atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf3atv1'))
        prf_4_atv_1 = None if request.POST.get('prf4atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf4atv1'))

        # ------------------------------ TESTES PARA ATIVIDADE 2 -----------------------------------------
        if request.POST.get('ativ2') != '':
            atividade_2 = Atividades.objects.get(atividade=request.POST.get('ativ2'))
            hora_atividade_2 = request.POST.get('horaAtividade_2')
            prf_1_atv_2 = Professores.objects.get(nome=request.POST.get('prf1atv2'))
            prf_2_atv_2 = None if request.POST.get('prf2atv2') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv2'))
            prf_3_atv_2 = None if request.POST.get('prf3atv2') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv1'))
            prf_4_atv_2 = None if request.POST.get('prf4atv2') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv1'))
        else:
            atividade_2 = hora_atividade_2 = prf_1_atv_2 = prf_2_atv_2 = prf_3_atv_2 = prf_4_atv_2 = None

        # ------------------------------ TESTES PARA ATIVIDADE 3 -----------------------------------------
        if request.POST.get('ativ3') != '':
            atividade_3 = Atividades.objects.get(atividade=request.POST.get('ativ3'))
            hora_atividade_3 = request.POST.get('horaAtividade_3')
            prf_1_atv_3 = Professores.objects.get(nome=request.POST.get('prf1atv3'))
            prf_2_atv_3 = None if request.POST.get('prf2atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv3'))
            prf_3_atv_3 = None if request.POST.get('prf3atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv3'))
            prf_4_atv_3 = None if request.POST.get('prf4atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv3'))
        else:
            atividade_3 = hora_atividade_3 = prf_1_atv_3 = prf_2_atv_3 = prf_3_atv_3 = prf_4_atv_3 = None

        # ------------------------------ TESTES PARA ATIVIDADE 4 -----------------------------------------
        if request.POST.get('ativ4') != '':
            atividade_4 = Atividades.objects.get(atividade=request.POST.get('ativ4'))
            hora_atividade_4 = request.POST.get('horaAtividade_4')
            prf_1_atv_4 = Professores.objects.get(nome=request.POST.get('prf1atv4'))
            prf_2_atv_4 = None if request.POST.get('prf2atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv4'))
            prf_3_atv_4 = None if request.POST.get('prf3atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv4'))
            prf_4_atv_4 = None if request.POST.get('prf4atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv4'))
        else:
            atividade_4 = hora_atividade_4 = prf_1_atv_4 = prf_2_atv_4 = prf_3_atv_4 = prf_4_atv_4 = None

        # ------------------------------ TESTES PARA ATIVIDADE 5 -----------------------------------------
        if request.POST.get('ativ5') != '':
            atividade_5 = Atividades.objects.get(atividade=request.POST.get('ativ5'))
            hora_atividade_5 = request.POST.get('horaAtividade_5')
            prf_1_atv_5 = Professores.objects.get(nome=request.POST.get('prf1atv5'))
            prf_2_atv_5 = None if request.POST.get('prf2atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv5'))
            prf_3_atv_5 = None if request.POST.get('prf3atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf3atv5'))
            prf_4_atv_5 = None if request.POST.get('prf4atv3') == '' else Professores.objects.get(
                nome=request.POST.get('prf4atv5'))
        else:
            atividade_5 = hora_atividade_5 = prf_1_atv_5 = prf_2_atv_5 = prf_3_atv_5 = prf_4_atv_5 = None

        relatorio = request.POST.get('relatorio')

        os = OrdemDeServico.objects.create(tipo=tipo, coordenador=coordenador, instituicao=instituicao,
                                           responsaveis=responsaveis, serie=serie,
                                           coordenador_peraltas=coordenador_peraltas,
                                           participantes_previa=participantes_previa,
                                           participantes_confirmados=participantes_confirmados,
                                           data_atendimento=data_atendimento,
                                           professor_2=professor_2, professor_3=professor_3, professor_4=professor_4,
                                           hora_entrada=hora_entrada, atividade_1=atividade_1,
                                           hora_atividade_1=hora_atividade_1,
                                           prf_1_atv_1=prf_1_atv_1, prf_2_atv_1=prf_2_atv_1, prf_3_atv_1=prf_3_atv_1,
                                           prf_4_atv_1=prf_4_atv_1, atividade_2=atividade_2,
                                           hora_atividade_2=hora_atividade_2,
                                           prf_1_atv_2=prf_1_atv_2, prf_2_atv_2=prf_2_atv_2, prf_3_atv_2=prf_3_atv_2,
                                           prf_4_atv_2=prf_4_atv_2, atividade_3=atividade_3,
                                           hora_atividade_3=hora_atividade_3,
                                           prf_1_atv_3=prf_1_atv_3, prf_2_atv_3=prf_2_atv_3, prf_3_atv_3=prf_3_atv_3,
                                           prf_4_atv_3=prf_4_atv_3, atividade_4=atividade_4,
                                           hora_atividade_4=hora_atividade_4,
                                           prf_1_atv_4=prf_1_atv_4, prf_2_atv_4=prf_2_atv_4, prf_3_atv_4=prf_3_atv_4,
                                           prf_4_atv_4=prf_4_atv_4, atividade_5=atividade_5,
                                           hora_atividade_5=hora_atividade_5,
                                           prf_1_atv_5=prf_1_atv_5, prf_2_atv_5=prf_2_atv_5, prf_3_atv_5=prf_3_atv_5,
                                           prf_4_atv_5=prf_4_atv_5, relatorio=relatorio)
        os.save()
        return redirect('dashboard')


def empresa(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html')
