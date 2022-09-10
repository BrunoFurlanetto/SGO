from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ceu.models import Professores
from detector.funcoes import pegar_dados_evento, pegar_escalas, juntar_dados_detector, tratar_dados_detector_selecionado
from detector.models import DetectorDeBombas
from ordemDeServico.models import OrdemDeServico
from projetoCEU.utils import verificar_grupo, is_ajax, email_error


@login_required(login_url='login')
def detector_de_bombas(request, id_detector=None):
    grupos = verificar_grupo(request.user.groups.all())
    professores = Professores.objects.all()
    detectores_salvos = DetectorDeBombas.objects.filter(data_inicio__lte=datetime.now())

    if request.method == 'GET':
        if request.GET.get('data_inicio'):
            data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d')
            data_final = datetime.strptime(request.GET.get('data_final'), '%Y-%m-%d')

            ordens_intervalo = (OrdemDeServico.objects
                                .filter(escala_ceu=True)
                                .filter(check_in__date__gte=data_inicio, check_in__date__lte=data_final)
                                )

            return render(request, 'detector/detector_de_bombas.html', {'grupos': grupos,
                                                                        'eventos': ordens_intervalo,
                                                                        'pesquisado': True,
                                                                        'professores': professores
                                                                        })

    if is_ajax(request):

        if request.method == 'POST':
            atividades_eventos = pegar_dados_evento(request.POST, request.POST.get('editando'))
            escalas = pegar_escalas(request.POST)
            return JsonResponse({'atividades_eventos': atividades_eventos, 'escalas': escalas})

        detector_selecionado = DetectorDeBombas.objects.get(id=int(request.GET.get('id_detector')))
        return JsonResponse(tratar_dados_detector_selecionado(detector_selecionado))

    if request.method != 'POST':
        if not id_detector:
            return render(request, 'detector/detector_de_bombas.html', {'grupos': grupos,
                                                                        'detectores': detectores_salvos})

        detector_editando = DetectorDeBombas.objects.get(id=id_detector)
        data_inicio = detector_editando.data_inicio.strftime('%Y-%m-%d')
        data_final = detector_editando.data_final.strftime('%Y-%m-%d')

        return render(request, 'detector/detector_de_bombas.html', {'grupos': grupos,
                                                                    'editar': True,
                                                                    'id_detector': detector_editando.id,
                                                                    'data_inicio': data_inicio,
                                                                    'data_final': data_final,
                                                                    'eventos': detector_editando.grupos.all()})

    if request.POST.get('detector_excluir'):
        try:
            detector_excluir = DetectorDeBombas.objects.get(id=int(request.POST.get('detector_excluir')))
            detector_excluir.delete()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, f'Houve um erro inesperado: {e}')
            return redirect('dashboard')
        else:
            messages.success(request, 'Detector de bombas, excluído com sucesso!!')
            return redirect('detector')

    try:
        data_inicio = datetime.strptime(request.POST.get('inicio'), '%Y-%m-%d')
        data_final = datetime.strptime(request.POST.get('final'), '%Y-%m-%d')
        grupos, dados_atividades = juntar_dados_detector(request.POST)

        if not request.POST.get('id_detector'):
            novo_detector_de_bombas = DetectorDeBombas.objects.create(
                data_inicio=data_inicio,
                data_final=data_final,
                dados_atividades=dados_atividades
            )

            novo_detector_de_bombas.grupos.set(grupos)
            novo_detector_de_bombas.save()
        else:
            detector_editado = DetectorDeBombas.objects.get(id=int(request.POST.get('id_detector')))
            detector_editado.dados_atividades = dados_atividades
            detector_editado.save()

    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, f'Houve um erro inesperado: {e}')
        return redirect('dashboard')
    else:
        messages.success(request, 'Detector de bombas, salvo com sucesso!!')
        return redirect('detector')
