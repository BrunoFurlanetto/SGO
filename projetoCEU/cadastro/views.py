from django.shortcuts import render, redirect
from .models import OrdemDeServico, Professores, Atividades, Tipo
import datetime


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
            nome=request.POST.get('prf3atv2'))
        prf_4_atv_2 = None if request.POST.get('prf4atv2') == '' else Professores.objects.get(
            nome=request.POST.get('prf4atv2'))

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

        os = OrdemDeServico(tipo=tipo, coordenador=coordenador,
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

    professores = Professores.objects.all()
    atividades = Atividades.objects.all()
    rangei = range(1, 10)
    rangej = range(1, 3)
    soma_total_atividade_1 = soma_total_atividade_2 = datetime.timedelta(days=0, hours=0, minutes=0)
    soma_total_atividade_3 = horas_totais = datetime.timedelta(days=0, hours=0, minutes=0)

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html', {'professores': professores, 'rangei': rangei,
                                                         'rangej': rangej, 'atividades': atividades})
    else:
        tipo = Tipo.objects.get(pk=3)
        instituicao = request.POST.get('instituicao')
        responsaveis = None if request.POST.get('responsaveis') == '' else request.POST.get('responsaveis')
        coordenador_peraltas = None if request.POST.get('coordenadorPeraltas') == '' else request.POST.get(
            'coordenadorPeraltas')
        coordenador = Professores.objects.get(nome=request.POST.get('coordenador'))
        participantes_previa = request.POST.get('previaParticipantes')
        participantes_confirmados = None if request.POST.get('participantes') == '' else request.POST.get(
            'participantes')
        data_atendimento = request.POST.get('dataAtendimento')
        professor_2 = None if request.POST.get('prf2') == '' else Professores.objects.get(
            nome=request.POST.get('prf2'))
        hora_entrada = None if request.POST.get('horaEntrada') == '' else request.POST.get('horaEntrada')

        # ------------------------------ TESTES PARA ATIVIDADE 1 -----------------------------------------
        atividade_1 = Atividades.objects.get(atividade=request.POST.get('ativ1'))
        prf_1_atv_1 = Professores.objects.get(nome=request.POST.get('prf1atv1'))
        prf_2_atv_1 = None if request.POST.get('prf2atv1') == '' else Professores.objects.get(
            nome=request.POST.get('prf2atv1'))

        # ------------------ PRIMEIRA ENTRADA E SAIDA DA EMPRESA NO CEU -----------------------
        atividade_1_entrada_1 = datetime.datetime.strptime(request.POST.get('horaEntrada1'), '%H:%M')
        atividade_1_saida_1 = datetime.datetime.strptime(request.POST.get('horaSaida1'), '%H:%M')
        hora_1_atividade_1 = atividade_1_saida_1 - atividade_1_entrada_1
        soma_total_atividade_1 += hora_1_atividade_1

        # ------------------ SEGUNDA ENTRADA E SAIDA DA EMPRESA NO CEU -----------------------------------------
        atividade_1_entrada_2 = None if request.POST.get('horaEntrada2') == '' else request.POST.get('horaEntrada2')
        atividade_1_saida_2 = None if request.POST.get('horaSaida2') == '' else request.POST.get('horaSaida2')

        if atividade_1_entrada_2 is not None:
            atividade_1_entrada_2 = datetime.datetime.strptime(request.POST.get('horaEntrada2'), '%H:%M')
            atividade_1_saida_2 = datetime.datetime.strptime(request.POST.get('horaSaida2'), '%H:%M')
            hora_2_atividade_1 = atividade_1_saida_2 - atividade_1_entrada_2
            soma_total_atividade_1 += hora_2_atividade_1

        # ------------------ TERCEIRA ENTRADA E SAIDA DA EMPRESA NO CEU ---------------------------------------
        atividade_1_entrada_3 = None if request.POST.get('horaEntrada3') == '' else request.POST.get('horaEntrada3')
        atividade_1_saida_3 = None if request.POST.get('horaSaida3') == '' else request.POST.get('horaSaida3')

        if atividade_1_entrada_3 is not None:
            atividade_1_entrada_3 = datetime.datetime.strptime(request.POST.get('horaEntrada3'), '%H:%M')
            atividade_1_saida_3 = datetime.datetime.strptime(request.POST.get('horaSaida3'), '%H:%M')
            hora_3_atividade_1 = atividade_1_saida_2 - atividade_1_entrada_3
            soma_total_atividade_1 += hora_3_atividade_1

        horas_totais += soma_total_atividade_1

        # ------------------------------ TESTES PARA ATIVIDADE 2 -----------------------------------------
        if request.POST.get('ativ4') != '':
            atividade_2 = Atividades.objects.get(atividade=request.POST.get('ativ4'))
            prf_1_atv_2 = Professores.objects.get(nome=request.POST.get('prf1atv4'))
            prf_2_atv_2 = None if request.POST.get('prf2atv4') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv2'))

            # -------------------------- QUARTA ENTRADA DA EMPRESA NO CEU ------------------------------------
            atividade_2_entrada_1 = datetime.datetime.strptime(request.POST.get('horaEntrada4'), '%H:%M')
            atividade_2_saida_1 = datetime.datetime.strptime(request.POST.get('horaSaida4'), '%H:%M')
            hora_1_atividade_2 = atividade_2_saida_1 - atividade_2_entrada_1
            soma_total_atividade_2 += hora_1_atividade_2

            # ------------------------- QUINTA ENTRADA DA EMPRESA NO CEU -------------------------------------
            atividade_2_entrada_2 = None if request.POST.get('horaEntrada5') == '' else request.POST.get('horaEntrada5')
            atividade_2_saida_2 = None if request.POST.get('horaSaida5') == '' else request.POST.get('horaSaida5')

            if atividade_2_entrada_2 is not None:
                atividade_2_entrada_2 = datetime.datetime.strptime(request.POST.get('horaEntrada5'), '%H:%M')
                atividade_2_saida_2 = datetime.datetime.strptime(request.POST.get('horaSaida5'), '%H:%M')
                hora_2_atividade_2 = atividade_2_saida_2 - atividade_2_entrada_2
                soma_total_atividade_2 += hora_2_atividade_2

            # --------------------------- SEXTA ENTRADA DA EMPRESA NO CEU ---------------------------------------
            atividade_2_entrada_3 = None if request.POST.get('horaEntrada6') == '' else request.POST.get('horaEntrada6')
            atividade_2_saida_3 = None if request.POST.get('horaSaida6') == '' else request.POST.get('horaSaida6')

            if atividade_2_entrada_3 is not None:
                atividade_2_entrada_3 = datetime.datetime.strptime(request.POST.get('horaEntrada6'), '%H:%M')
                atividade_2_saida_3 = datetime.datetime.strptime(request.POST.get('horaSaida6'), '%H:%M')
                hora_3_atividade_2 = atividade_2_saida_2 - atividade_2_entrada_2
                soma_total_atividade_2 += hora_3_atividade_2

            horas_totais += soma_total_atividade_2

        else:
            atividade_2 = prf_1_atv_2 = prf_2_atv_2 = None
            atividade_2_entrada_1 = atividade_2_saida_1 = atividade_2_entrada_2 = atividade_2_saida_2 = None
            atividade_2_entrada_3 = atividade_2_saida_3 = None

        # ------------------------------ TESTES PARA ATIVIDADE 3 -----------------------------------------
        if request.POST.get('ativ7') != '':
            atividade_3 = Atividades.objects.get(atividade=request.POST.get('ativ7'))
            hora_atividade_3 = request.POST.get('horaAtividade_7')
            prf_1_atv_3 = Professores.objects.get(nome=request.POST.get('prf1atv7'))
            prf_2_atv_3 = None if request.POST.get('prf2atv7') == '' else Professores.objects.get(
                nome=request.POST.get('prf2atv7'))

        # -------------------------- SÉTIMA ENTRADA DA EMPRESA NO CEU ------------------------------------
            atividade_3_entrada_1 = datetime.datetime.strptime(request.POST.get('horaEntrada7'), '%H:%M')
            atividade_3_saida_1 = datetime.datetime.strptime(request.POST.get('horaSaida7'), '%H:%M')
            hora_1_atividade_3 = atividade_3_saida_1 - atividade_3_entrada_1
            soma_total_atividade_3 += hora_1_atividade_3

            # ------------------------- OITAVA ENTRADA DA EMPRESA NO CEU -------------------------------------
            atividade_3_entrada_2 = None if request.POST.get('horaEntrada8') == '' else request.POST.get('horaEntrada8')
            atividade_3_saida_2 = None if request.POST.get('horaSaida8') == '' else request.POST.get('horaSaida8')

            if atividade_3_entrada_2 is not None:
                atividade_3_entrada_2 = datetime.datetime.strptime(request.POST.get('horaEntrada8'), '%H:%M')
                atividade_3_saida_2 = datetime.datetime.strptime(request.POST.get('horaSaida8'), '%H:%M')
                hora_2_atividade_3 = atividade_3_saida_2 - atividade_3_entrada_2
                soma_total_atividade_3 += hora_2_atividade_3

            # ------------------------ NONA ENTRADA DA EMPRESA NO CEU ----------------------------------------
            atividade_3_entrada_3 = None if request.POST.get('horaEntrada9') == '' else request.POST.get('horaEntrada9')
            atividade_3_saida_3 = None if request.POST.get('horaSaida9') == '' else request.POST.get('horaSaida9')

            if atividade_3_entrada_3 is not None:
                atividade_3_entrada_3 = datetime.datetime.strptime(request.POST.get('horaEntrada9'), '%H:%M')
                atividade_3_saida_3 = datetime.datetime.strptime(request.POST.get('horaSaida9'), '%H:%M')
                hora_3_atividade_3 = atividade_3_saida_3 - atividade_3_entrada_3
                soma_total_atividade_3 += hora_3_atividade_3

            horas_totais += soma_total_atividade_3

        else:
            atividade_3 = prf_1_atv_3 = prf_2_atv_3 = None
            atividade_3_entrada_1 = atividade_3_saida_1 = atividade_3_entrada_2 = atividade_3_saida_2 = None
            atividade_3_entrada_3 = atividade_3_saida_3 = None

        relatorio = request.POST.get('relatorio')

        os = OrdemDeServico.objects.create(tipo=tipo, coordenador=coordenador, instituicao=instituicao,
                                           responsaveis=responsaveis,
                                           coordenador_peraltas=coordenador_peraltas,
                                           participantes_previa=participantes_previa,
                                           participantes_confirmados=participantes_confirmados,
                                           data_atendimento=data_atendimento,
                                           professor_2=professor_2, hora_entrada=hora_entrada, atividade_1=atividade_1,
                                           prf_1_atv_1=prf_1_atv_1, prf_2_atv_1=prf_2_atv_1,
                                           hora_atividade_1=atividade_1_entrada_1,
                                           atividade_1_entrada_1=atividade_1_entrada_1,
                                           atividade_1_saida_1=atividade_1_saida_1,
                                           atividade_1_entrada_2=atividade_1_entrada_2,
                                           atividade_1_saida_2=atividade_1_saida_2,
                                           atividade_1_entrada_3=atividade_1_entrada_3,
                                           atividade_1_saida_3=atividade_1_saida_3,
                                           soma_horas_1=soma_total_atividade_1, atividade_2=atividade_2,
                                           hora_atividade_2=atividade_2_entrada_1,
                                           atividade_2_entrada_1=atividade_2_entrada_1,
                                           atividade_2_saida_1=atividade_2_saida_1,
                                           atividade_2_entrada_2=atividade_2_entrada_2,
                                           atividade_2_saida_2=atividade_2_saida_2,
                                           atividade_2_entrada_3=atividade_2_entrada_3,
                                           atividade_2_saida_3=atividade_2_saida_3, soma_horas_2=soma_total_atividade_2,
                                           prf_1_atv_2=prf_1_atv_2,
                                           prf_2_atv_2=prf_2_atv_2,
                                           atividade_3=atividade_3, hora_atividade_3=atividade_3_entrada_1,
                                           atividade_3_entrada_1=atividade_3_entrada_1,
                                           atividade_3_saida_1=atividade_3_saida_1,
                                           atividade_3_entrada_2=atividade_3_entrada_2,
                                           atividade_3_saida_2=atividade_3_saida_2,
                                           atividade_3_entrada_3=atividade_3_entrada_3,
                                           atividade_3_saida_3=atividade_3_saida_3, soma_horas_3=soma_total_atividade_3,
                                           prf_1_atv_3=prf_1_atv_3,
                                           prf_2_atv_3=prf_2_atv_3,
                                           horas_totais=horas_totais, relatorio=relatorio)
        os.save()
        return redirect('dashboard')
