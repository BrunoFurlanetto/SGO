from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ceu.models import Atividades, Locaveis
from detector.funcoes import pegar_dados_evento, pegar_escalas, juntar_dados_detector, \
    tratar_dados_detector_selecionado, salvar_alteracoes_de_atividade_locacao
from detector.models import DetectorDeBombas
from ordemDeServico.models import OrdemDeServico
from projetoCEU.utils import is_ajax, email_error


@login_required(login_url='login')
def detector_de_bombas(request, id_detector=None):
    setor = 'CEU' if request.user.has_perm('cadastro.add_relatoriodeatendimentopublicoceu') else 'Peraltas'
    atividades = Atividades.objects.all()
    espacos = Locaveis.objects.all()

    detectores_salvos = DetectorDeBombas.objects.filter(
        data_final__gte=datetime.now().date(),
        setor=setor.lower()
    )

    if request.method == 'GET':
        if request.GET.get('data_inicio'):
            data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d')
            data_final = datetime.strptime(request.GET.get('data_final'), '%Y-%m-%d')

            if setor == 'CEU':
                ordens_intervalo = OrdemDeServico.objects.filter(
                    check_in_ceu__date__gte=data_inicio,
                    check_in_ceu__date__lte=data_final
                )
            else:
                ordens_intervalo = OrdemDeServico.objects.filter(
                    check_in__date__gte=data_inicio,
                    check_in__date__lte=data_final
                )

            return render(request, 'detector/detector_de_bombas.html', {
                'eventos': ordens_intervalo,
                'pesquisado': True,
            })

    if is_ajax(request):
        if request.method == 'POST':
            if request.POST.get('data'):
                detector_selecionado = DetectorDeBombas.objects.get(id=int(request.POST.get('id_detector')))

                return HttpResponse(request.POST.get('data') in detector_selecionado.observacoes)

            if request.POST.get('id_detector') and request.POST.get('observacoes'):
                try:
                    detector_selecionado = DetectorDeBombas.objects.get(id=int(request.POST.get('id_detector')))
                    detector_selecionado.observacoes += f"\n\nObservação de {request.POST.get('data_observacao')}: " \
                                                        f"{request.POST.get('observacoes')}"
                    detector_selecionado.save()
                except Exception as e:
                    return JsonResponse({
                        'tipo': 'error',
                        'msg': f'Houve um erro inesperado: {e}. Tente novamente mais tarde'
                    })
                else:
                    return JsonResponse({
                        'tipo': 'success',
                        'msg': 'Observações salvas com sucesso'
                    })

            if request.POST.get('atividade_local'):
                try:
                    atividade = Atividades.objects.get(atividade=request.POST.get('atividade_local'))
                except Atividades.DoesNotExist:
                    espaco = Locaveis.objects.get(local__estrutura=request.POST.get('atividade_local'))

                    return JsonResponse({'id_local': espaco.id})
                else:
                    return JsonResponse({'id_atividade': atividade.id})

            atividades_eventos, grupos = pegar_dados_evento(request.POST, request.POST.get('editando'), setor)
            escalas = pegar_escalas(request.POST, setor)

            return JsonResponse({'atividades_eventos': atividades_eventos, 'escalas': escalas, 'grupos': grupos})

        if request.GET.get('id_detector'):
            detector_selecionado = DetectorDeBombas.objects.get(pk=request.GET.get('id_detector'))
            return JsonResponse(tratar_dados_detector_selecionado(detector_selecionado))

    if request.method != 'POST':
        if not id_detector:
            return render(request, 'detector/detector_de_bombas.html', {
                'detectores': detectores_salvos
            })

        detector_editando = DetectorDeBombas.objects.get(id=id_detector)
        data_inicio = detector_editando.data_inicio.strftime('%Y-%m-%d')
        data_final = detector_editando.data_final.strftime('%Y-%m-%d')

        return render(request, 'detector/detector_de_bombas.html', {
            'editar': True,
            'id_detector': detector_editando.id,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'atividades': atividades,
            'espacos': espacos,
            'eventos': detector_editando.grupos.all()
        })

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

    if request.POST.get('observacoes_da_alteracao'):
        salvar_alteracoes_de_atividade_locacao(request.POST)

        return redirect('detector')

    grupos, dados_atividades = juntar_dados_detector(request.POST, setor)

    try:
        data_inicio = datetime.strptime(request.POST.get('inicio'), '%Y-%m-%d')
        data_final = datetime.strptime(request.POST.get('final'), '%Y-%m-%d')

        if not request.POST.get('id_detector'):
            novo_detector_de_bombas = DetectorDeBombas.objects.create(
                data_inicio=data_inicio,
                data_final=data_final,
                dados_atividades=dados_atividades
            )

            novo_detector_de_bombas.grupos.set(grupos)
            novo_detector_de_bombas.setor = setor.lower()
            novo_detector_de_bombas.save()
        else:
            detector_editado = DetectorDeBombas.objects.get(id=int(request.POST.get('id_detector')))
            detector_editado.dados_atividades = dados_atividades
            detector_editado.save()
    except Exception as e:
        return redirect('dashboard')
    else:
        messages.success(request, 'Detector de bombas, salvo com sucesso!!')
        return redirect('detector')
