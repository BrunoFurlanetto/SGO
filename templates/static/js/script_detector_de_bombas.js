function pegar_dados_eventos(){
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

            if (response['atividades_eventos']['atividades'].length > 0){
                for (let i = 0; i < response['atividades_eventos']['atividades'].length; i++){
                    eventos.push(pegar_dados_atividades(response['atividades_eventos']['atividades'][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++){
                        if (classes_select_selecionados[j].title == response['atividades_eventos']['atividades'][i]['grupo']){
                            classes_select_selecionados[j].style.backgroundColor = response['atividades_eventos']['atividades'][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['atividades_eventos']['atividades'][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }

                }
            }

            if (response['atividades_eventos']['locacoes'].length > 0){
                for (let i = 0; i < response['atividades_eventos']['locacoes'].length; i++){
                    eventos.push(pegar_dados_locacoes(response['atividades_eventos']['locacoes'][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++){
                        if (classes_select_selecionados[j].title == response['atividades_eventos']['locacoes'][i]['grupo']){
                            classes_select_selecionados[j].style.backgroundColor = response['atividades_eventos']['locacoes'][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['atividades_eventos']['locacoes'][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }
                }
            }

            detector_de_bombas(eventos)
            mostrar_por_atividade(response['atividades_eventos'], response['escalas'])
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
    $('.div-btn-escalar-professores').removeClass('none')
}

function mostrar_por_atividade(dados_eventos, escalados){
    const grupos = []
    $('#formulario-escala-professores-atividades').empty()
    let grupos_teste = Array()
    console.log(escalados)
    for (let i = 0; i < dados_eventos['atividades'].length; i++){
        if (!grupos.includes(dados_eventos['atividades'][i]['grupo'])){
            grupos.push(dados_eventos['atividades'][i]['grupo'])

            $('#formulario-escala-professores-atividades').append(
                `
                <hr>
                <div id="${dados_eventos['atividades'][i]['grupo'].replaceAll(' ', '-')}" class="atividades-locacoes-grupo row">
                    <div class="titulo-botao" style="display: flex">
                        <h5 class="titulo-secao">${dados_eventos['atividades'][i]['grupo']}</h5>
                        <button type="button" class="btn-mostrar-atividades-locacoes" onclick="mostrar_esconder_tividades(this)"><i class='bx bx-plus'></i></button>
                    </div>                    
                    <div class="atividades none"></div>
                    <div class="locacoes none"></div>
                </div>`
            )
        }
    }

    for (let i = 0; i < dados_eventos['locacoes'].length; i++){
        if (!grupos.includes(dados_eventos['locacoes'][i]['grupo'])){
            grupos.push(dados_eventos['locacoes'][i]['grupo'])

            $('#formulario-escala-professores-atividades').append(
                `
                <hr>
                <div id="${dados_eventos['locacoes'][i]['grupo'].replaceAll(' ', '-')}" class="atividades-locacoes-grupo row">
                    <div class="titulo-botao" style="display: flex">
                        <h5 class="titulo-secao">${dados_eventos['locacoes'][i]['grupo']}</h5>
                        <button type="button" class="btn-mostrar-atividades-locacoes" onclick="mostrar_esconder_tividades(this)"><i class='bx bx-plus'></i></button>
                    </div>                    
                    <div class="atividades none"></div>
                    <div class="locacoes none"></div>
                </div>`
            )
        }
    }

//--------------------------------------------- Adição de todos os inputs ------------------------------------------------------

    for (let i = 0; i < dados_eventos['atividades'].length; i++){
        if (grupos_teste === []){
            grupos_teste.push(dados_eventos['atividades'][i]['grupo'])
        } else if (!grupos_teste.includes(dados_eventos['atividades'][i]['grupo'])){
            grupos_teste.push(dados_eventos['atividades'][i]['grupo'])
        }
        let j = grupos_teste.length

        $(`#${dados_eventos['atividades'][i]['grupo'].replaceAll(' ', '-')} .atividades`).append(
            `
                <label>${dados_eventos['atividades'][i]['atividade']} (${moment(dados_eventos['atividades'][i]['inicio_atividade']).format('D [às] HH:mm')})</label>
                <input type="hidden" name="grupo_${j}" value="${dados_eventos['atividades'][i]['grupo']}">
                <input type="hidden" name="atividade_${i+1}_grupo_${j}" value="${dados_eventos['atividades'][i]['grupo']}">
                <select name="professores_atividade_${i+1}_grupo_{j}" id="professores_atividade_${i+1}_grupo_${j}" multiple></select>
            `
        )

        try {
            if (escalados[j-1]['grupo'] === dados_eventos['atividades'][i]['grupo']){
                for (let k = 0; k < escalados[j-1]['escalados'].length; k++){
                    $(`#professores_atividade_${i+1}_grupo_${j}`).append(`<option value="${escalados[j-1]['escalados'][k]['id']}">${escalados[j-1]['escalados'][k]['nome']}</option>`)
                }

                $(`#professores_atividade_${i+1}_grupo_${j}`).select2()
            }
        } catch (e) {}

    }

    for (let i = 0; i < dados_eventos['locacoes'].length; i++){
        if (grupos_teste === []){
            grupos_teste.push(dados_eventos['locacoes'][i]['grupo'])
        } else if (!grupos_teste.includes(dados_eventos['locacoes'][i]['grupo'])){
            grupos_teste.push(dados_eventos['locacoes'][i]['grupo'])
        }
        let j = grupos_teste.length

        $(`#${dados_eventos['locacoes'][i]['grupo'].replaceAll(' ', '-')} .locacoes`).append(
            `
                <label>Locacão ${dados_eventos['locacoes'][i]['local']} (${moment(dados_eventos['locacoes'][i]['check_in']).format('D [das] HH:mm')} às ${moment(dados_eventos['locacoes'][i]['check_out']).format('HH:mm')})</label>
                <input type="hidden" name="grupo_${j}" value="${dados_eventos['locacoes'][i]['grupo']}">
                <input type="hidden" name="locacao_${i+1}_grupo_${j}" value="${dados_eventos['locacoes'][i]['grupo']}">
                <select name="professores_locacao_${i+1}_grupo_${j}" id="professores_locacao_${i+1}_grupo_${j}" multiple></select>
            `
        )

         try {
            if (escalados[j-1]['grupo'] === dados_eventos['locacoes'][i]['grupo']){
                for (let k = 0; k < escalados[j-1]['escalados'].length; k++){
                    $(`#professores_locacao_${i+1}_grupo_${j}`).append(`<option value="${escalados[j-1]['escalados'][k]['id']}">${escalados[j-1]['escalados'][k]['nome']}</option>`)
                }

                $(`#professores_locacao_${i+1}_grupo_${j}`).select2()
            }
        } catch (e) {}
    }
}

function mostrar_esconder_tividades(div){
    const id_div_avo = div.parentNode.parentNode.id

    $(`#${id_div_avo} .atividades, #${id_div_avo} .locacoes`).toggleClass('none')
}