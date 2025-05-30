let atividades = []
let grupos = []
let atividade_acampamento_i = 0

function selecionar_tudo() {
    if ($("#select_all").is(':checked')) {
        $("#clientes > option").prop("selected", "selected");
        $("#clientes").trigger("change");
    } else {
        $("#clientes > option").prop("selected", false);
        $("#clientes").trigger("change");
    }
}

function mostrar_atividade_local_novo(switchButton) {
    const id_switchButton = switchButton.id

    if (id_switchButton === 'id_adicionar_locacao') {
        if ($(`#${id_switchButton}`).prop('checked')) {
            $('#dados_locacao_novo').removeClass('none')
            $('#div_switch_add_atividade, #dados_locacao_novo .div-titulo-btn .btn').addClass('none')
            $('#id_adicionar_atividade').prop('checked', false)
        } else {
            $('#dados_locacao_novo').addClass('none')
            $('#div_switch_add_atividade, #dados_locacao_novo .div-titulo-btn .btn').removeClass('none')
        }
    } else {
        if ($(`#${id_switchButton}`).prop('checked')) {
            $('#dados_nova_atividade').removeClass('none')
            $('#dados_locacao_novo').css({'margin-top': '40px'})
            $('#div_switch_add_locacao, #dados_nova_atividade .div-titulo-btn .btn').addClass('none')
            $('#id_adicionar_locacao').prop('checked', false)
        } else {
            $('#dados_nova_atividade').addClass('none')
            $('#dados_locacao_novo').css({'margin-top': '0px'})
            $('#div_switch_add_locacao, #dados_nova_atividade .div-titulo-btn .btn').removeClass('none')
        }
    }
}

function excluir_atividade(btn) {
    const id_btn = btn.id

    if (id_btn === 'btn_excluir_atv') {
        $('#atividade_excluida').val('true')
        $('#inputs_atividade_nova').addClass('none')
    } else if (id_btn === 'btn_excluir_loc') {
        $('#locacao_excluida').val('true')
        $('#inputs_locacao_nova').addClass('none')
    }
}

function pegar_dados_eventos(editando = false) {
    loading()
    let id_detector
    $('#atividades-acampamento').empty()

    if ($(`#clientes option:selected`).length === 0) {
        if ($('.alert-warning').length === 0) {
            $('.grupos').prepend('<p style="margin-left: 1%; width: 98%" class="alert-warning">Nenhum grupo selecionado</p>')
        }
        return
    } else {
        $('.alert-warning').remove()
    }

    if (editando) {
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
            let colunas_agenda = document.getElementsByClassName('fc-timegrid-col')

            for (let area in response['atividades_eventos']) {
                for (let i = 0; i < response['atividades_eventos'][area].length; i++) {
                    console.log(response['atividades_eventos'][area])
                    if (area === 'atividades_ceu') eventos.push(pegar_dados_atividades(response['atividades_eventos'][area][i]))
                    if (area === 'locacoes') eventos.push(pegar_dados_locacoes(response['atividades_eventos'][area][i]))
                    if (area === 'atividades_extra') eventos.push(pegar_dados_atividades(response['atividades_eventos'][area][i]))

                    for (let j = 0; j < classes_select_selecionados.length; j++) {
                        if (classes_select_selecionados[j].title === response['atividades_eventos'][area][i]['grupo']['nome']) {
                            classes_select_selecionados[j].style.backgroundColor = response['atividades_eventos'][area][i]['color']
                            classes_select_selecionados[j].style.borderColor = response['atividades_eventos'][area][i]['color']
                            classes_select_selecionados[j].style.color = '#fff'
                        }
                    }
                }
            }

            detector_de_bombas(eventos, false, false)

            if (editando) {
                mostrar_por_atividade(response['atividades_eventos'], response['grupos'], response['escalas'], true)
            } else {
                mostrar_por_atividade(response['atividades_eventos'], response['grupos'], response['escalas'])
            }

            for (let i = 0; i < colunas_agenda.length; i++) {
                try {
                    if (response['escalas'][response['escalas'].length - 1]['datas_sem'].includes(colunas_agenda[i].attributes[2].value)) {
                        colunas_agenda[i].classList.add('sem-monitor')
                    }

                } catch (e) {
                }
            }

        }
    }).done(() => {
        end_loading()
    }).catch((error) => {
        alert(error)
        end_loading()
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

function pegar_atividades_acampamento(dados_atividades_acampamento) {
    const id_atividade = dados_atividades_acampamento['id']
    const nome_atividade = dados_atividades_acampamento['nome']
    const duracao = dados_atividades_acampamento['duracao']
    const color = dados_atividades_acampamento['color']
    const id_grupo = dados_atividades_acampamento['grupo']['id']
    const nome_grupo = dados_atividades_acampamento['grupo']['nome']
    const div_atividades = `<div id="${id_atividade}" data-grupo_id="${id_grupo}" data-grupo="${nome_grupo}" class="card-atividade" style="background: ${color}; color: #fff" data-event='{ "title": "${nome_atividade}", "duration": "${duracao}", "color": "${color}" }'>${nome_atividade}</div>`
    $('#atividades-acampamento').append(div_atividades)
}

function pegar_select_atividade_locacao(atividade, hora_atividade) {
    const labels = $(`#${moment(hora_atividade).format('yyyy-MM-DD')} label`)

    for (let i = 0; i < labels.length; i++) {
        if (labels[i].textContent.includes(atividade) && labels[i].textContent.includes(moment(hora_atividade).format('HH:mm'))) {
            const label = labels[i]
            let elemento = label
            const atividade_alterada = label.nextElementSibling.name
            $('#atividade_locacao_alterada').val(atividade_alterada)
            $('#qtd_atividade').val($(`#qtd_${atividade_alterada}`).val())

            while (true) {
                elemento = elemento.nextElementSibling

                if (elemento.tagName === 'SELECT') {
                    console.log(elemento);

                    let options = $(`#${elemento.id} option`).map(function () {
                        let selected = this.selected ? 'selected' : ''; // Mantém a seleção original
                        return `<option value="${this.value}" ${selected}>${this.text}</option>`;
                    }).get().join('');

                    $('#id_professores_atividade_nova').html(options).trigger('change.select2');


                    break;
                }
            }
        }
    }
}

function detector_de_bombas(eventos, dropable, editable) {
    const calendarUI = document.getElementById('detector_de_bombas')
    const data_1 = moment($('#id_data_inicio').val())
    const data_2 = moment($('#id_data_final').val())
    let intervalo = data_2.diff(data_1);
    let dias_evento = moment.duration(intervalo).asDays() + 1;
    let atividades = document.getElementById('atividades-acampamento')

    new FullCalendar.Draggable(atividades, {
        itemSelector: '.card-atividade',
    })

    const detector = new FullCalendar.Calendar(calendarUI, {
        editable: editable,
        droppable: dropable,

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

        drop: function (info) {
            atividade_acampamento_i++
            const grupo = grupos.indexOf(parseInt(info.draggedEl.attributes['data-grupo_id'].value)) + 1
            const nome_grupo = info.draggedEl.attributes['data-grupo'].value
            const dados_atividade = {'id': info.draggedEl.id, 'nome': info.draggedEl.innerText}
            criar_inputs_atividades_acampamento(info.date, dados_atividade, atividade_acampamento_i, grupo, nome_grupo)
            try {
            } catch (e) {
            }
        },

        eventResize: function (info) {
            console.log(info)
        },

        eventDrop: function (info) {
            console.log(info)
        },

        eventClick: function (info) {
            if (!isNaN(parseInt(window.location.href.split('/')[4]))) {
                const atividade_local = info.event.title
                const start = info.event.start
                const end = info.event.end
                const hoje = new Date(Date.now())

                if (((hoje - start) / (1000 * 60 * 60)) >= 24) {
                    return
                }

                $('#id_atividade_atual, #id_atividade_nova, #id_data_hora_atividade_atual, #id_data_hora_atividade_nova, #id_observacoes_alteracao').val('')
                $('#id_espaco_atual, #id_espaco_novo, #id_check_out_atual, #id_check_out_novo, #atividade_locacao_alterada').val('')
                $('#id_adicionar_atividade, #id_adicionar_locacao').prop('checked', false)
                $('#div_switch_add_atividade, #div_switch_add_locacao').removeClass('none')
                $('#alerta_dados_iguais').remove()
                $('#atividade_excluida, #locacao_excluida').val('false')
                $('#id_professores_atividade_nova').select2({dropdownParent: $("#modal_trocar_atividade .modal-content")})
                $('#form_alteracao_de_atividade #id_detector').val(window.location.href.split('/')[4])
                pegar_select_atividade_locacao(atividade_local, start)

                $.ajax({
                    type: 'POST',
                    url: '',
                    headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                    data: {'atividade_local': atividade_local},
                    success: function (response) {
                        if (response['id_atividade']) {
                            $('#dados_locacao_atual, #dados_locacao_novo').addClass('none')
                            $('#dados_atividade_atual, #dados_nova_atividade').removeClass('none')
                            $('#id_atividade_atual, #id_atividade_nova').val(response['id_atividade'])
                            $('#id_data_hora_atividade_atual, #id_data_hora_atividade_nova').val(moment(start).format('yyyy-MM-DDTHH:mm'))
                        } else {
                            $('#dados_locacao_atual, #dados_locacao_novo').removeClass('none')
                            $('#dados_atividade_atual, #dados_nova_atividade').addClass('none')
                            $('#id_espaco_atual, #id_espaco_novo').val(response['id_local'])
                            $('#id_check_in_atual, #id_check_in_novo').val(moment(start).format('yyyy-MM-DDTHH:mm'))
                            $('#id_check_out_atual, #id_check_out_novo').val(moment(end).format('yyyy-MM-DDTHH:mm'))
                        }
                    }
                })

                $('#modal_trocar_atividade').modal('show')
            }
        }

    })

    detector.render();
    detector.setOption('locale', 'pt-br')

    if (!isNaN(parseInt(window.location.href.split('/')[4]))) {
        const hoje = new Date(Date.now())
        const id_detector = parseInt(window.location.href.split('/')[4])
        let colunas_agenda = document.getElementsByClassName('fc-timegrid-col')
        let datas_colunas = []

        for (let i = 1; i < colunas_agenda.length; i++) {
            datas_colunas.push(colunas_agenda[i].attributes[2].value)
        }

        if ((datas_colunas.includes(moment(hoje).format('Y-m-d'))) && (hoje.getHours() >= 22 || hoje.getHours() <= 2)) {
            if (hoje.getHours() >= 0 && hoje.getHours() <= 2) {
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
                    if (response === 'False') {
                        $('.grupos').append(`<button type="button" class="btn btn-primary btn-observacoes" data-toggle="modal" data-target="#modal-adicionar-obs">Observações do dia ${hoje.getDate().toLocaleString()}<button`)
                    }
                }
            })
        }

    }
}

function mostrar_por_atividade(dados_eventos, grupos_detector, escalados, editando = false) {
    const datas = []
    let formulario_detector = $('#formulario-escala-professores-atividades')
    let grupos_teste = Array()
    let n_atividades = Array()
    let relacoes = Array()
    let professores_monitores = 'professores'
    moment.locale('pt-br')
    formulario_detector.empty()
    grupos = juntar_grupos(grupos_detector)

    if (editando) {
        const id_detector = $('#id_detector').val()
        $('#formulario-escala-professores-atividades').append(`<input type="hidden" name="id_detector" value="${id_detector}">`)
    }

    formulario_detector.append(`
        <input type="hidden" name="inicio" id="id_inicio" value="${$('#id_data_inicio').val()}">
        <input type="hidden" name="final" id="id_final" value="${$('#id_data_final').val()}">
    `)

//--------------------------------------------- Adição de todas divs -----------------------------------------------------------
    for (let area in dados_eventos) {
        for (let i = 0; i < dados_eventos[area].length; i++) {
            if (area !== 'locacoes') {
                if (!datas.includes(moment(dados_eventos[area][i]['inicio_atividade']).format('L'))) {
                    datas.push(moment(dados_eventos[area][i]['inicio_atividade']).format('L'))
                    criar_divs_atividades(formulario_detector, moment(dados_eventos[area][i]['inicio_atividade']))
                }
            } else {
                if (!datas.includes(moment(dados_eventos[area][i]['check_in']).format('L'))) {
                    datas.push(moment(dados_eventos[area][i]['check_in']).format('L'))
                    criar_divs_atividades(formulario_detector, moment(dados_eventos[area][i]['check_in']))
                }
            }
        }
    }

//--------------------------------------------- Adição de todos os inputs ------------------------------------------------------
    for (let area in dados_eventos) {
        n_atividades = Array()

        for (let i = 0; i < dados_eventos[area].length; i++) {
            if (n_atividades.length === 0 || !n_atividades[dados_eventos[area][i]['grupo']['id']]) {
                n_atividades[dados_eventos[area][i]['grupo']['id']] = 1
            } else {
                n_atividades[dados_eventos[area][i]['grupo']['id']]++
            }

            if (grupos_teste === []) {
                grupos_teste.push(dados_eventos[area][i]['grupo']['id'])
            } else if (!grupos_teste.includes(dados_eventos[area][i]['grupo']['id'])) {
                grupos_teste.push(dados_eventos[area][i]['grupo']['id'])
            }

            let id_select = `${professores_monitores}_${area}_${n_atividades[dados_eventos[area][i]['grupo']['id']]}_grupo_${grupos.indexOf(dados_eventos[area][i]['grupo']['id']) + 1}`

            if (area === 'locacoes') {
                criar_inputs_locacoes(professores_monitores, dados_eventos[area][i], i + 1, grupos, area)
                popular_professores(
                    formulario_detector,
                    dados_eventos[area][i]['professores'],
                    escalados,
                    id_select,
                    dados_eventos[area][i]['check_in'].split(' ')[0]
                )
            } else {
                criar_inputs_atividades(professores_monitores, n_atividades[dados_eventos[area][i]['grupo']['id']], grupos, dados_eventos[area][i], area)
                popular_professores(
                    formulario_detector,
                    dados_eventos[area][i]['professores'],
                    escalados,
                    id_select,
                    dados_eventos[area][i]['inicio_atividade'].split(' ')[0]
                )
            }
        }
    }

    formulario_detector.append(`<div class="botoes">
        <button type="button" id="btn_salvar" onclick="validar()" class="btn btn-primary">Salvar detector</button>
        <button type="submit" id="salvar" class="none">Salvar detector</button>
    </div>`)
    $('.escala-por-atividades').removeClass('none')
}

function popular_professores(formulario_detector, professores, escalados, id_select, data) {
    for (let escala of escalados) {
        if (escala['data'] == data) {
            for (let monitor_professor of escala['escalados']) {
                $(`#${id_select}`).append(`<option value="${monitor_professor['id']}">${monitor_professor['nome']}</option>`)
            }
        }
    }

    $('#formulario-escala-professores-atividades select').select2()
    $(`#${id_select}`).val(professores)
    $(`#${id_select}`).trigger('change.select2')
}

function criar_divs_atividades(formulario_detector, data_inicio) {
    formulario_detector.append(`
        <hr>
        <div id="${data_inicio.format('YYYY-MM-DD')}" class="atividades-locacoes-grupo row">
            <div class="titulo-botao" style="display: flex">
                <h5 class="titulo-secao">${data_inicio.format('LL')}</h5>
                <button type="button" class="btn-mostrar-atividades-locacoes" onclick="mostrar_esconder_tividades(this)"><i class='bx bx-plus'></i></button>
            </div>                    
            <div class="atividades_ceu none atividades_detector"></div>
            <div class="atividades_extra none atividades_detector"></div>
            <div class="atividades_acampamento none atividades_detector"></div>
            <div class="locacoes none atividades_detector"></div>
        </div>
    `)
}

function criar_inputs_atividades_acampamento(data_inicio, dados_atividade, atividade_n, grupo_n, nome_grupo) {
    const div_append = `${moment(data_inicio).format('YYYY-MM-DD')} .atividades_acampamento`
    const label_atividade = `${dados_atividade['nome']} - ${moment(data_inicio).format('[às] HH:mm')} (${nome_grupo})`
    const nome_id_select = `monitores_atividades_acampamento_${atividade_n}_grupo_${grupo_n}`
    const nome_input_data = `data_e_hora_atividades_acampamento_${atividade_n}_grupo_${grupo_n}`
    const nome_input_qtd = `qtd_atividades_acampamento_${atividade_n}_grupo_${grupo_n}`
    const nome_input_atividade = `atividades_acampamento_${atividade_n}_grupo_${grupo_n}`
    const value_atividade = dados_atividade['id']
    const value_data_e_hora = moment(data_inicio).format('YYYY-MM-DD HH:mm')

    $(`#${div_append}`).append(`
        <label>${label_atividade}</label>
        <input type="hidden" name="grupo_${grupo_n}_atividades_acampamento_${atividade_n}" id="${nome_input_atividade}" value="${value_atividade}">
        <input type="hidden" name="grupo_${grupo_n}_atividades_acampamento_${atividade_n}" id="${nome_input_data}" class="data_e_hora" value="${value_data_e_hora}">
        <div class="row">
            <div style="width: 85%">
                <select name="grupo_${grupo_n}_atividades_acampamento_${atividade_n}[monitores]" id="${nome_id_select}" onchange="validacao(this)" style="width: 100%" multiple></select>
            </div>
            <div style="width: 15%">
                <input type="number" min="0" name="grupo_${grupo_n}_atividades_acampamento_${atividade_n}" placeholder="QTD" id="${nome_input_qtd}" style="height: 33px" class="qtd" required>
            </div>
        </div>        
    `)

    popular_select_monitores($(`#${moment(data_inicio).format('YYYY-MM-DD')} select`), $(`#${nome_id_select}`))
}

function criar_inputs_atividades(professores_monitores, atividade_n, grupos, dados_eventos, area) {
    const div_append = `${moment(dados_eventos['inicio_atividade']).format('YYYY-MM-DD')} .${area}`
    const label_atividade = `${dados_eventos['atividade']['nome']} - ${moment(dados_eventos['inicio_atividade']).format('[às] HH:mm')} com ${dados_eventos['atividade']['qtd']} participantes (${dados_eventos['grupo']['nome']})`
    const nome_id_select = `${professores_monitores}_${area}_${atividade_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_data = `data_e_hora_${area}_${atividade_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_qtd = `qtd_${area}_${atividade_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_atividade = `${area}_${atividade_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const value_atividade = dados_eventos['atividade']['id']
    const value_data_e_hora = dados_eventos['inicio_atividade']
    const value_qtd = dados_eventos['atividade']['qtd']

    $(`#${div_append}`).append(`
        <label>${label_atividade}</label>
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${atividade_n}" value="${value_atividade}">
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${atividade_n}" id="${nome_input_data}" class="data_e_hora" value="${value_data_e_hora}">
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${atividade_n}" id="${nome_input_qtd}" class="qtd" value="${value_qtd}">
        <select name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${atividade_n}[${professores_monitores}]" id="${nome_id_select}" onchange="validacao(this)" multiple></select>
    `)

    atividades[nome_input_atividade] = [value_atividade, value_data_e_hora]
}

function criar_inputs_locacoes(professores_monitores, dados_eventos, locacao_n, grupos, area) {
    const div_append = `${moment(dados_eventos['check_in']).format('YYYY-MM-DD')} .${area}`
    const nome_id_select = `${professores_monitores}_locacoes_${locacao_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_local = `locacao_${locacao_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_check_in = `check_in_locacao_${locacao_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_check_out = `check_out_locacao_${locacao_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`
    const nome_input_qtd = `qtd_locacao_${locacao_n}_grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}`

    $(`#${div_append}`).append(`
        <label>Locacão ${dados_eventos['local']['nome']} - Das ${moment(dados_eventos['check_in']).format('HH:mm')} às ${moment(dados_eventos['check_out']).format('HH:mm')} (${dados_eventos['grupo']['nome']})</label>           
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${locacao_n}" id="${nome_input_local}" value="${dados_eventos['local']['id']}">
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${locacao_n}" id="${nome_input_check_in}" value="${dados_eventos['check_in']}">
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${locacao_n}" id="${nome_input_check_out}" value="${dados_eventos['check_out']}">
        <input type="hidden" name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${locacao_n}" id="${nome_input_qtd}" value="${dados_eventos['local']['qtd']}">
        <select name="grupo_${grupos.indexOf(dados_eventos['grupo']['id']) + 1}_${area}_${locacao_n}[${professores_monitores}]" id="${nome_id_select}" onchange="validacao(this)" multiple></select>
    `)

    atividades[nome_input_local] = [dados_eventos['local']['id'], dados_eventos['check_in']]
}

function popular_select_monitores(selects_existentes, select_append) {
    for (let select of selects_existentes) {
        if (select.children.length > 0) {
            $(select.children).clone().appendTo($(select_append))
            select_append.select2()

            return
        }
    }
}

function mostrar_esconder_tividades(div) {
    const id_div_avo = div.parentNode.parentNode.id

    $(`#${id_div_avo} .atividades_ceu, #${id_div_avo} .locacoes, #${id_div_avo} .atividades_extra, #${id_div_avo} .atividades_acampamento`).toggleClass('none')
}

function juntar_grupos(dados_grupos) {
    let grupos = []
    let j = 1

    for (let grupo of dados_grupos) {
        let n_grupo = Object.keys(grupo)[0]
        let id_grupo = Object.values(grupo)[0]
        grupos.push(id_grupo)
        $('#formulario-escala-professores-atividades').append(`<input type="hidden" name="grupos" id="id_grupo_${n_grupo.split('_')[1]}" value="${id_grupo}">`)
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
    loading()

    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_detector': id_detector},
        success: function (response) {
            console.log(response['events'])
            mostrar_detector_de_bombas(response['events'], response['datas'][0], response['datas'][1])
            const legenda = $('.legenda')

            if (legenda.length === 0) {
                $('#detector_de_bombas').append('<hr><div class="legenda"></div>')
            } else {
                legenda.empty()
            }

            for (let i in response['grupos']) {
                $('.legenda').append(`
                    <div id="${i}" style="display: flex; margin-bottom: -10px">
                        <div class="barra-de-cor" style="background: ${response['grupos'][i]}"></div>    
                        <p>${i}</p>    
                    </div>
                `)
            }
        }
    }).done(() => {
        end_loading()
    }).catch((error) => {
        alert(error)
        end_loading()
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

function excluir_detector(selecao) {
    $('#id_detector_excluir').val(selecao.id.split('_')[2])
    $('#modal-excluir-detector').modal('show')
}

function editar_detector(selecao) {
    const id_detector = parseInt(selecao.id.split('_')[2])
    window.location.href = `/detector-de-bombas/${id_detector}`
}

function validacao(selecao) {
    const data_e_hora_atividade = moment($(`#${selecao.id.replace('professores', 'data_e_hora')}`).val()).format('Y-MM-DD HH:mm')
    const inputs_data_e_hora = $('.data_e_hora')

    for (let i = 0; i < inputs_data_e_hora.length; i++) {
        const data_teste = moment(inputs_data_e_hora[i].value).format('Y-MM-DD HH:mm')
        const data_teste_somado_uma_hora = moment(inputs_data_e_hora[i].value).add(1, 'hours').format('Y-MM-DD HH:mm')

        if (selecao.id.replace('professores', 'data_e_hora') !== inputs_data_e_hora[i].id) {
            if (data_e_hora_atividade >= data_teste && data_e_hora_atividade < data_teste_somado_uma_hora) {
                const professores_selecionados = $(`#${inputs_data_e_hora[i].id.replace('data_e_hora', 'professores')}`).val()
                let professor_selecionado = $(`#${selecao.id}`).val()

                for (let j = 0; j < professores_selecionados.length; j++) {
                    if (professor_selecionado.includes(professores_selecionados[j])) {
                        professor_selecionado.splice(professor_selecionado.indexOf(professor_selecionado[j]), 1)
                        $(`#${selecao.id}`).val(professor_selecionado).trigger('change')
                    }
                }
            }
        }
    }
}

$('document').ready(function () {
    jQuery('#form_observacoes_dia').submit(function () {
        let dados = jQuery(this).serialize();
        let url = $(this).attr('action');
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
                $('#modal-adicionar-obs').modal('hide')
                $('.btn-observacoes').remove()
            }
        })
        return false
    })

})

function validar(e) {
    const inputs = $('#formulario-escala-professores-atividades select')
    let lista_dias_errado = []
    $('#mensagem_escala_faltando').remove()

    for (let input of inputs) {
        if (input.value === '' && !lista_dias_errado.includes(moment(input.parentNode.parentNode.id, 'YYYY-MM-DD').date())) {
            lista_dias_errado.push(moment(input.parentNode.parentNode.id, 'YYYY-MM-DD').date())
        }
    }

    if (lista_dias_errado.length > 0) {
        $('#formulario-escala-professores-atividades').prepend(`<div id="mensagem_escala_faltando" class="alert-warning">
            <p>Verificar as escalas dos dias ${lista_dias_errado.join(', ')}</p>
        </div>`)
    } else {
        $('#salvar').click()
    }
}

$('#btn_salvar_alteracao').on('click', function (e) {
    const form = $('#form_alteracao_de_atividade');

    // validação para o caso de ser atividades sendo alteradas e os dados forem iguais
    const atividade_atual = $('#id_atividade_atual').val()
    const inicio_atividade_atual = $('#id_data_hora_atividade_atual').val()
    const nova_atividade = $('#id_atividade_nova').val()
    const inicio_atividade_nova = $('#id_data_hora_atividade_nova').val()

    if (atividade_atual !== '' && $('#atividade_excluida').val() === 'false') {
        if (atividade_atual === nova_atividade && inicio_atividade_atual === inicio_atividade_nova) {
            $('#alerta_dados_iguais').remove()
            $('#dados_nova_atividade').prepend('<p id="alerta_dados_iguais" class="alert-warning">Dados da nova atividade igual da atual!</p>')
            e.preventDefault()
            return false
        }
    }

    // Validação para o caso de dados de locações repetidos
    const locacao_atual = $('#id_espaco_atual').val()
    const check_in_atual = $('#id_check_in_atual').val()
    const check_out_atual = $('#id_check_out_atual').val()
    const locacao_nova = $('#id_espaco_novo').val()
    const check_in_novo = $('#id_check_in_novo').val()
    const check_out_novo = $('#id_check_out_novo').val()

    if (locacao_atual !== '' && $('#locacao_excluida').val() === 'false') {
        if (locacao_atual === locacao_nova && check_in_atual === check_in_novo && check_out_atual === check_out_novo) {
            $('#alerta_dados_iguais').remove()
            $('#dados_locacao_novo').prepend('<p id="alerta_dados_iguais" class="alert-warning">Dados da nova locacação igual da atual!</p>')
            e.preventDefault()
            return false
        }
    }

    $('body').css({'cursor': 'wait'})
    $('.alert-warning').remove()
    $(form).submit()
});