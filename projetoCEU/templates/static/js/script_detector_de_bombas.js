function pegar_dados_evento(){
    if ( $(`#clientes option:selected`).length === 0 ){
        if ($('.alert-warning').length === 0) {
            $('.grupos').prepend('<p style="margin-left: 1%; width: 98%" class="alert-warning">Nenhum grupo selecionado</p>')
        }

        return
    } else {
        $('.alert-warning').remove()
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_grupos': $('#clientes').val(), 'data_inicio': $('#id_data_inicio').val(), 'data_final': $('#id_data_final').val()},
        success: function (response) {
            let eventos = []
            let classes_select_selecionados = $('.select2-selection__choice')

            if (response['atividades'].length > 0){
                for (let i = 0; i < response['atividades'].length; i++){
                    eventos.push(pegar_dados_atividades(response['atividades'][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++){
                        if (classes_select_selecionados[j].title == response['atividades'][i]['grupo']){
                            classes_select_selecionados[j].style.backgroundColor = response['atividades'][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['atividades'][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }

                }
            }

            if (response['locacoes'].length > 0){
                for (let i = 0; i < response['locacoes'].length; i++){
                    eventos.push(pegar_dados_locacoes(response['locacoes'][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++){
                        if (classes_select_selecionados[j].title == response['locacoes'][i]['grupo']){
                            classes_select_selecionados[j].style.backgroundColor = response['locacoes'][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['locacoes'][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }
                }
            }

            detector_de_bombas(eventos)
        }
    })

}

function pegar_dados_atividades(dados_atividade) {
    return {
        title: dados_atividade['atividade'],
        start: dados_atividade['inicio_atividade'],
        end: dados_atividade['fim_atividade'],
        color: dados_atividade['color']
    }
}


function pegar_dados_locacoes(dados_locacao){
    return {
        title: dados_locacao['local'],
        start: dados_locacao['check_in'],
        end: dados_locacao['check_out'],
        color: dados_locacao['color']
    }
}

function detector_de_bombas (eventos) {
    const calendarUI = document.getElementById('detector_de_bombas');
    const data_1 = moment($('#id_data_inicio').val())
    const data_2 = moment($('#id_data_final').val())
    var intervalo = data_2.diff(data_1);
    var dias_evento = moment.duration(intervalo).asDays() + 1;
    const detector = new FullCalendar.Calendar(calendarUI, {
        headerToolbar: {
            left: '',
            center: 'title',
            right: '',
        },

        eventClick: function(info){

            $('#ModalProfessoresEvento .modal-title').text(`Professores para: ${info.event.title} (${moment(info.event.start).format('DD/MM [às] HH:mm)')}`)
            $('#ModalProfessoresEvento').modal('show')
        },

        initialDate: $('#id_data_inicio').val(),
        initialView: 'timeGrid',
        duration: {days: dias_evento},
        eventOrderStrict: true,
        locale: 'pt-br',
        allDaySlot: false,
        slotMinTime: '07:00:00',
        nowIndicator: true,
        slotDuration: '00:15:00',
        slotEventOverlap: false,
        events: eventos,

    })

    detector.render();
    detector.setOption('locale', 'pt-br')
}