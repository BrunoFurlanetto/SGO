function pegar_dados_evento(){
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_cliente': $(`#clientes option:selected`).val()},
        success: function (response) {
            let eventos = []
            let hora_maxima = ''
            let hora_minima = ''

            for(let atividade in response['atividades']){
               if(hora_maxima === ''){
                   let hora = parseInt(response['atividades'][atividade]['data_e_hora'].split(' ')[1]) + 2
                   hora_maxima = String(hora + ':00:00')
               } else {
                   let hora = parseInt(response['atividades'][atividade]['data_e_hora'].split(' ')[1]) + 2

                   if(hora > hora_maxima.split(':')[0]){
                       hora_maxima = String(hora + ':00:00')
                   }
               }

                if(hora_minima === ''){
                   let hora = parseInt(response['atividades'][atividade]['data_e_hora'].split(' ')[1]) - 1
                   hora_minima = String(hora + ':00:00')
               } else {
                   let hora = parseInt(response['atividades'][atividade]['data_e_hora'].split(' ')[1]) - 1

                   if(hora > hora_maxima.split(':')[0]){
                       hora_minima = String(hora + ':00:00')
                   }
               }

                eventos.push({
                    title: response['atividades'][atividade]['atividade'],
                    start: response['atividades'][atividade]['data_e_hora'],
                })
            }

            detector_de_bombas(
                response['data_evento'].split('T')[0],
                response['dias_evento'], eventos,
                hora_minima,
                hora_maxima
            )
        }
    })

}

function detector_de_bombas (data_evento, dias_evento, eventos, hora_minima, hora_maxima) {
    const calendarUI = document.getElementById('detector_de_bombas');
    const detector = new FullCalendar.Calendar(calendarUI, {
        headerToolbar: {
            left: '',
            center: 'title',
            right: '',
        },

        eventClick: function(info){
            $('#ModalProfessoresEvento .modal-title').text(`Professores para: ${info.event.title} (${moment(info.event.start).format('DD/MM')} as ${moment(info.event.start).format('HH:mm')})`)
            $('#ModalProfessoresEvento').modal('show')
        },

        initialDate: data_evento,
        initialView: 'timeGrid',
        duration: {days: dias_evento},
        eventOrderStrict: true,
        locale: 'pt-br',
        allDaySlot: false,
        slotMinTime: hora_minima,
        slotMaxTime: hora_maxima,
        nowIndicator: true,
        slotDuration: '00:15:00',
        slotEventOverlap: false,
        events: eventos,

    })

    detector.render();
    detector.setOption('locale', 'pt-br')
}