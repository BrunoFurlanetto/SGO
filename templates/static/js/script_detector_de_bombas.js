function selecionar_tudo() {
    if ($("#select_all").is(':checked')) {
        $("#clientes > option").prop("selected", "selected");
        $("#clientes").trigger("change");
    } else {
        $("#clientes > option").prop("selected", false);
        $("#clientes").trigger("change");
    }
}

function pegar_dados_eventos(editando=false) {
    let id_detector

    if ($(`#clientes option:selected`).length === 0) {
        if ($('.alert-warning').length === 0) {
            $('.grupos').prepend('<p style="margin-left: 1%; width: 98%" class="alert-warning">Nenhum grupo selecionado</p>')
        }

        return
    } else {
        $('.alert-warning').remove()
    }

    if (editando){
        id_detector = $('#id_detector').val()
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {
            'id_grupos': $('#clientes').val(),
            'data_inicio': $('#id_data_inicio').val(),
            'data_final': $('#id_data_final').val(),
            'editando': editando,
            'id_detector': id_detector,
        },
        success: function (response) {
            let eventos = []
            let classes_select_selecionados = $('.select2-selection__choice')

            if (response['atividades_eventos']['atividades'].length > 0) {
                for (let i = 0; i < response['atividades_eventos']['atividades'].length; i++) {
                    eventos.push(pegar_dados_atividades(response['atividades_eventos']['atividades'][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++) {
                        if (classes_select_selecionados[j].title == response['atividades_eventos']['atividades'][i]['grupo']['nome']) {
                            classes_select_selecionados[j].style.backgroundColor = response['atividades_eventos']['atividades'][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['atividades_eventos']['atividades'][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }

                }
            }

            if (response['atividades_eventos']['locacoes'].length > 0) {
                for (let i = 0; i < response['atividades_eventos']['locacoes'].length; i++) {
                    eventos.push(pegar_dados_locacoes(response['atividades_eventos']['locacoes'][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++) {
                        if (classes_select_selecionados[j].title == response['atividades_eventos']['locacoes'][i]['grupo']['nome']) {
                            classes_select_selecionados[j].style.backgroundColor = response['atividades_eventos']['locacoes'][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['atividades_eventos']['locacoes'][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }
                }
            }

            detector_de_bombas(eventos)

            if (editando){
                mostrar_por_atividade(response['atividades_eventos'], response['escalas'], editando=true, response['atividades_eventos']['professores'])
            } else {
                console.log(response['atividades_eventos'])
                mostrar_por_atividade(response['atividades_eventos'], response['escalas'])
            }

        }
    })

}

function pegar_dados_atividades(dados_atividade) {
    return {
        title: dados_atividade['atividade']['nome'],
        start: dados_atividade['inicio_atividade'],
        end: dados_atividade['fim_atividade'],
        color: dados_atividade['color']
    }
}


function pegar_dados_locacoes(dados_locacao) {
    return {
        title: dados_locacao['local']['nome'],
        start: dados_locacao['check_in'],
        end: dados_locacao['check_out'],
        color: dados_locacao['color']
    }
}

function detector_de_bombas(eventos) {
    const calendarUI = document.getElementById('detector_de_bombas');
    const data_1 = moment($('#id_data_inicio').val())
    const data_2 = moment($('#id_data_final').val())
    let intervalo = data_2.diff(data_1);
    let dias_evento = moment.duration(intervalo).asDays() + 1;

    if (!isNaN(parseInt(window.location.href.split('/')[4]))){
        const hoje = new Date(Date.now())
        const id_detector = parseInt(window.location.href.split('/')[4])

        if (hoje.getHours() >= 22 || hoje.getHours() <= 2){
            if(hoje.getHours() >= 0 && hoje.getHours() <= 2){
                hoje.setDate(hoje.getDate() - 1)
            }

            $('#id_detector_modal').val(id_detector)
            $('#id_data_observacao').val(hoje.toLocaleDateString())
            $('#modal-adicionar-obs .modal-title').text(`Observações do dia: ${hoje.toLocaleDateString()}`)

            $.ajax({
                type: 'POST',
                url: '',
                headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                data: {'data': hoje.toLocaleDateString(), 'id_detector': id_detector},
                success: function (response) {
                    console.log(response)
                    if (response === 'False') {
                        $('.grupos').append(`<button type="button" class="btn btn-primary btn-observacoes" data-toggle="modal" data-target="#modal-adicionar-obs">Observações do dia ${hoje.getDate().toLocaleString()}<button`)
                    }
                }
            })
        }

    }

    const detector = new FullCalendar.Calendar(calendarUI, {
        headerToolbar: {
            left: '',
            center: 'title',
            right: '',
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

function mostrar_por_atividade(dados_eventos, escalados, editando=false, professores=null) {
    const datas = []
    let formulario_detector = $('#formulario-escala-professores-atividades')
    let grupos_teste = Array()
    let n_atividades = Array()
    moment.locale('pt-br')
    formulario_detector.empty()
    let grupos = juntar_grupos(dados_eventos)

    if (editando){
        const id_detector = $('#id_detector').val()
        $('#formulario-escala-professores-atividades').append(`<input type="hidden" name="id_detector" value="${id_detector}">`)
    }

    formulario_detector.append(`
        <input type="hidden" name="inicio" id="id_inicio" value="${$('#id_data_inicio').val()}">
        <input type="hidden" name="final" id="id_final" value="${$('#id_data_final').val()}">
    `)

    for (let i = 0; i < dados_eventos['atividades'].length; i++) {
        if (!datas.includes(moment(dados_eventos['atividades'][i]['inicio_atividade']).format('L'))) {
            datas.push(moment(dados_eventos['atividades'][i]['inicio_atividade']).format('L'))

            formulario_detector.append(
                `
                <hr>
                <div id="${moment(dados_eventos['atividades'][i]['inicio_atividade']).format('YYYY-MM-D')}" class="atividades-locacoes-grupo row">
                    <div class="titulo-botao" style="display: flex">
                        <h5 class="titulo-secao">${moment(dados_eventos['atividades'][i]['inicio_atividade']).format('LL')}</h5>
                        <button type="button" class="btn-mostrar-atividades-locacoes" onclick="mostrar_esconder_tividades(this)"><i class='bx bx-plus'></i></button>
                    </div>                    
                    <div class="atividades none"></div>
                    <div class="locacoes none"></div>
                </div>`
            )
        }
    }

    for (let i = 0; i < dados_eventos['locacoes'].length; i++) {
        if (!datas.includes(moment(dados_eventos['locacoes'][i]['check_in']).format('L'))) {
            datas.push((moment(dados_eventos['locacoes'][i]['check_in']).format('L')))

            formulario_detector.append(
                `
                <hr>
                <div id="${moment(dados_eventos['locacoes'][i]['check_in']).format('YYYY-MM-DD')}" class="atividades-locacoes-grupo row">
                    <div class="titulo-botao" style="display: flex">
                        <h5 class="titulo-secao">${moment(dados_eventos['locacoes'][i]['check_in']).format('LL')}</h5>
                        <button type="button" class="btn-mostrar-atividades-locacoes" onclick="mostrar_esconder_tividades(this)"><i class='bx bx-plus'></i></button>
                    </div>                    
                    <div class="atividades none"></div>
                    <div class="locacoes none"></div>
                </div>`
            )
        }
    }

//--------------------------------------------- Adição de todos os inputs ------------------------------------------------------
    for (let i = 0; i < dados_eventos['atividades'].length; i++) {
        if (n_atividades.length === 0 || !n_atividades[dados_eventos['atividades'][i]['grupo']['id']]) {
            n_atividades[dados_eventos['atividades'][i]['grupo']['id']] = 1
        } else {
            n_atividades[dados_eventos['atividades'][i]['grupo']['id']]++
        }

        if (grupos_teste === []) {
            grupos_teste.push(dados_eventos['atividades'][i]['grupo']['id'])
        } else if (!grupos_teste.includes(dados_eventos['atividades'][i]['grupo']['id'])) {
            grupos_teste.push(dados_eventos['atividades'][i]['grupo']['id'])

        }

        let nome_id_select = `professores_atividade_${n_atividades[dados_eventos['atividades'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['atividades'][i]['grupo']['id']) + 1}`
        let nome_input_data = `data_e_hora_atividade_${n_atividades[dados_eventos['atividades'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['atividades'][i]['grupo']['id']) + 1}`
        let nome_input_atividade = `atividade_${n_atividades[dados_eventos['atividades'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['atividades'][i]['grupo']['id']) + 1}`

        $(`#${moment(dados_eventos['atividades'][i]['inicio_atividade']).format('YYYY-MM-DD')} .atividades`).append(
            `
                <label>${dados_eventos['atividades'][i]['atividade']['nome']} - ${moment(dados_eventos['atividades'][i]['inicio_atividade']).format('[às] HH:mm')} com ${dados_eventos['atividades'][i]['atividade']['qtd']} participantes (${dados_eventos['atividades'][i]['grupo']['nome']})</label>
                <input type="hidden" name="${nome_input_atividade}" value="${dados_eventos['atividades'][i]['atividade']['id']}">
                <input type="hidden" name="${nome_input_data}" id="${nome_input_data}" class="data_e_hora" value="${dados_eventos['atividades'][i]['inicio_atividade']}">
                <select name="${nome_id_select}" id="${nome_id_select}" onchange="validacao(this)" multiple></select>
            `
        )

        for (let j = 0; j < escalados.length; j++) {
            if (escalados[j]['data'] === dados_eventos['atividades'][i]['inicio_atividade'].split(' ')[0]) {

                for (let k = 0; k < escalados[j]['escalados'].length; k++) {
                    if (professores !== null) {
                        if (Array.isArray(professores[nome_id_select])) {
                            if (professores[nome_id_select].includes(escalados[j]['escalados'][k]['id'])) {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}" selected>${escalados[j]['escalados'][k]['nome']}</option>`)
                            } else {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}">${escalados[j]['escalados'][k]['nome']}</option>`)
                            }
                        } else {
                            if (professores[nome_id_select] === escalados[j]['escalados'][k]['id']) {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}" selected>${escalados[j]['escalados'][k]['nome']}</option>`)
                            } else {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}">${escalados[j]['escalados'][k]['nome']}</option>`)
                            }
                        }
                    } else {
                        $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}">${escalados[j]['escalados'][k]['nome']}</option>`)
                    }
                }
            }
        }

        $(`#${nome_id_select}`).select2()
    }

    for (let i = 0; i < dados_eventos['locacoes'].length; i++) {
        if (n_atividades.length === 0 || !n_atividades[dados_eventos['locacoes'][i]['grupo']['id']]) {
            n_atividades[dados_eventos['locacoes'][i]['grupo']['id']] = 1
        } else {
            n_atividades[dados_eventos['locacoes'][i]['grupo']['id']]++
        }

        if (grupos_teste === []) {
            grupos_teste.push(dados_eventos['locacoes'][i]['grupo']['id'])
        } else if (!grupos_teste.includes(dados_eventos['locacoes'][i]['grupo']['id'])) {
            grupos_teste.push(dados_eventos['locacoes'][i]['grupo']['id'])
        }

        let nome_id_select = `professores_locacao_${n_atividades[dados_eventos['locacoes'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['locacoes'][i]['grupo']['id']) + 1}`
        let nome_input_check_in = `check_in_locacao_${n_atividades[dados_eventos['locacoes'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['locacoes'][i]['grupo']['id']) + 1}`
        let nome_input_check_out = `check_out_locacao_${n_atividades[dados_eventos['locacoes'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['locacoes'][i]['grupo']['id']) + 1}`
        let nome_input_local = `locacao_${n_atividades[dados_eventos['locacoes'][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos['locacoes'][i]['grupo']['id']) + 1}`

        $(`#${moment(dados_eventos['locacoes'][i]['check_in']).format('YYYY-MM-DD')} .locacoes`).append(
            `
                <label>Locacão ${dados_eventos['locacoes'][i]['local']['nome']} - Das ${moment(dados_eventos['locacoes'][i]['check_in']).format('HH:mm')} às ${moment(dados_eventos['locacoes'][i]['check_out']).format('HH:mm')} (${dados_eventos['locacoes'][i]['grupo']['nome']})</label>           
                <input type="hidden" name="${nome_input_local}" value="${dados_eventos['locacoes'][i]['local']['id']}">
                <input type="hidden" name="${nome_input_check_in}" value="${dados_eventos['locacoes'][i]['check_in']}">
                <input type="hidden" name="${nome_input_check_out}" value="${dados_eventos['locacoes'][i]['check_out']}">
                <select name="${nome_id_select}" id="${nome_id_select}" onchange="validacao()" multiple></select>
            `
        )

        for (let j = 0; j < escalados.length; j++) {
            if (escalados[j]['data'] === dados_eventos['locacoes'][i]['check_in'].split(' ')[0]) {
                for (let k = 0; k < escalados[j]['escalados'].length; k++) {
                    if (professores !== null) {
                        if (Array.isArray(professores[nome_id_select])) {
                            if (professores[nome_id_select].includes(escalados[j]['escalados'][k]['id'])) {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}" selected>${escalados[j]['escalados'][k]['nome']}</option>`)
                            } else {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}">${escalados[j]['escalados'][k]['nome']}</option>`)
                            }
                        } else {
                            if (professores[nome_id_select] === escalados[j]['escalados'][k]['id']) {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}" selected>${escalados[j]['escalados'][k]['nome']}</option>`)
                            } else {
                                $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}">${escalados[j]['escalados'][k]['nome']}</option>`)
                            }
                        }
                    } else {
                        $(`#${nome_id_select}`).append(`<option value="${escalados[j]['escalados'][k]['id']}">${escalados[j]['escalados'][k]['nome']}</option>`)
                    }
                }
            }
        }

        $(`#${nome_id_select}`).select2()
    }

    formulario_detector.append('<hr><button type="submit" id="btn_salvar" class="btn btn-primary">Salvar detector</button>')
    $('.escala-por-atividades').removeClass('none')
}

function mostrar_esconder_tividades(div) {
    const id_div_avo = div.parentNode.parentNode.id

    $(`#${id_div_avo} .atividades, #${id_div_avo} .locacoes`).toggleClass('none')
}

function juntar_grupos(dados_eventos) {
    let grupos = []
    let j = 1

    for (let i = 0; i < dados_eventos['atividades'].length; i++) {
        if (!grupos.includes(dados_eventos['atividades'][i]['grupo']['id'])) {
            grupos.push(dados_eventos['atividades'][i]['grupo']['id'])
            $('#formulario-escala-professores-atividades').append(`<input type="hidden" name="grupo_${j}" id="id_grupo_${j}" value="${dados_eventos['atividades'][i]['grupo']['id']}">`)
            j++
        }
    }

    for (let i = 0; i < dados_eventos['locacoes'].length; i++) {
        if (!grupos.includes(dados_eventos['locacoes'][i]['grupo']['id'])) {
            grupos.push(dados_eventos['locacoes'][i]['grupo']['id'])
            $('#formulario-escala-professores-atividades').append(`<input type="hidden" name="grupo_${j}" id="id_grupo_${j}" value="${dados_eventos['locacoes'][i]['grupo']['id']}">`)
            j++
        }
    }

    return grupos
}

function novo_detector() {
    $('#pesquisa_evento').removeClass('none')
    $('#detectores_salvos').addClass('none')
    $('#detector_de_bombas').empty()
}

function mostrar_detector(selecao) {
    const id_detector = selecao.id

    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_detector': id_detector},
        success: function (response) {
            mostrar_detector_de_bombas(response['events'], response['datas'][0], response['datas'][1])
            $('#detector_de_bombas').append('<hr><div class="legenda"></div>')

            for (let i in response['grupos']) {
                $('.legenda').append(`
                    <div id="${i}" style="display: flex; margin-bottom: -10px">
                        <div class="barra-de-cor" style="background: ${response['grupos'][i]}"></div>    
                        <p>${i}</p>    
                    </div>
                `)
            }
        }
    })
}

function mostrar_detector_de_bombas(eventos, data_1, dias_evento) {
    const calendarUI = document.getElementById('detector_de_bombas');

    const detector = new FullCalendar.Calendar(calendarUI, {
        headerToolbar: {
            left: '',
            center: 'title',
            right: '',
        },

        eventDidMount: function (info) {
            $(info.el).tooltip({
                title: `${info.event.extendedProps.description}`,
                placement: 'top',
                trigger: 'hover',
                container: 'body'
            });
        },

        initialDate: data_1,
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

function excluir_detector(selecao){
    $('#id_detector_excluir').val(selecao.id.split('_')[2])
    $('#modal-excluir-detector').modal('show')
}

function edtar_detector(selecao){
    const id_detector = parseInt(selecao.id.split('_')[2])
    window.location.href = `/detector-de-bombas/${id_detector}`
}

function validacao(selecao){
    const data_e_hora_atividade = moment($(`#${selecao.id.replace('professores', 'data_e_hora')}`).val()).format('Y-MM-DD HH:mm')
    const inputs_data_e_hora = $('.data_e_hora')

    for (let i = 0; i < inputs_data_e_hora.length; i++){
        const data_teste = moment(inputs_data_e_hora[i].value).format('Y-MM-DD HH:mm')
        const data_teste_somado_uma_hora = moment(inputs_data_e_hora[i].value).add(1, 'hours').format('Y-MM-DD HH:mm')

        if (selecao.id.replace('professores', 'data_e_hora') !== inputs_data_e_hora[i].id){
            if (data_e_hora_atividade >= data_teste && data_e_hora_atividade < data_teste_somado_uma_hora){
                const professores_selecionados =  $(`#${inputs_data_e_hora[i].id.replace('data_e_hora', 'professores')}`).val()
                let professor_selecionado = $(`#${selecao.id}`).val()

                for (let j = 0; j < professores_selecionados.length; j++){
                    if (professor_selecionado.includes(professores_selecionados[j])){
                        professor_selecionado.splice(professor_selecionado.indexOf(professor_selecionado[j]), 1)
                        $(`#${selecao.id}`).val(professor_selecionado).trigger('change')
                    }
                }
            }
        }

    }

}

$('document').ready(function() {
    jQuery('#form_observacoes_dia').submit(function () {
        let dados = jQuery(this).serialize();
        let url = $(this).attr('action');
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function(response) {
                $('#modal-adicionar-obs').modal('hide')
                $('.btn-observacoes').remove()
                console.log(response)
            }
        })
        return false
    })
})