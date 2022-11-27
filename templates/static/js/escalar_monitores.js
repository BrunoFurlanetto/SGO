let id_escalados = []
const niveis = ['coordenadores', 'monitores', 'auxiliares']
let areas = []

const arrastaveis = document.querySelectorAll('[draggable=true]')
const espacos = document.querySelectorAll('.espacos')

espacos.forEach((espaco) => {
    espaco.addEventListener('dragover', (e) => {
        const arrastando = document.querySelector('.arrastando')
        const nova_posicao = pegar_nova_posicao(espaco, e.clientY)
        e.preventDefault()
        e.dataTransfer.dropEffect = 'move'

        if (nova_posicao) {
            nova_posicao.insertAdjacentElement('afterend', arrastando)
        } else {
            espaco.prepend(arrastando)
        }
    })
})

document.addEventListener('dragstart', (e) => {
    e.target.classList.add('arrastando')
})

document.addEventListener('dragend', (e) => {
    e.target.classList.remove('arrastando');
})

function pegar_nova_posicao(local, posY) {
    const cards_monitor = local.querySelectorAll('.card-monitor:not(.arrastando)')
    let resultado

    for (let card_referencia of cards_monitor) {
        const box = card_referencia.getBoundingClientRect()
        const centro_do_box = box.y + box.height / 2

        if (posY >= centro_do_box) resultado = card_referencia
    }

    return resultado
}

function escalado(espaco) {
    const tipo_escalacao = espaco.id
    let monitores = espaco.querySelectorAll('.card-monitor')


    // ---------------------------------este pra retorno na disponibilidade correta ------------------------------------
    if (tipo_escalacao === 'monitores_hotelaria') {
        verificar_escalados(false)

        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()

            if (monitor.classList.contains('acampamento')) {
                $('#monitores_acampamento').append(monitor)
            }
        }
    }

    if (tipo_escalacao === 'monitores_acampamento') {
        verificar_escalados(false)

        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()

            if (monitor.classList.contains('hotelaria')) {
                $('#monitores_hotelaria').append(monitor)
            }
        }
    }
    // -----------------------------------------------------------------------------------------------------------------
    if (tipo_escalacao === 'monitores_escalados') {
        verificar_escalados(true)

        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
        }
    }

    if (tipo_escalacao === 'enfermagem'){
        verificar_escalados(false)

        for (let monitor of monitores){
            if (!monitor.classList.contains('enfermeira')) verificar_enfermeira(monitor)
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
        }
    }

    if (tipo_escalacao === 'monitor_embarque'){
        verificar_escalados(false)

        for (let monitor of monitores){
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
        }
    }
}

function verificar_escalados(escalando){
    const monitores_escalados = $('#monitores_escalados').children()
    let id_monitores = []

    for (let monitor of monitores_escalados){
        id_monitores.push(monitor.id)

        if (escalando){
            if (!id_escalados.includes(monitor.id)){
                id_escalados.push(monitor.id)
            }
        }
    }

    if (!escalando){
        for (let id of id_escalados){
            if (!id_monitores.includes(id)) id_escalados.splice(id_escalados.indexOf(id), 1)
        }
    }
    console.log(id_escalados)
}

function verificar_tecnica() {
    const monitores_escalados = $('#monitores_escalados').children()
    let areas = []

    for (let monitor of monitores_escalados) {
        if (monitor.classList.contains('tecnica')) {
            let areas_monitor = monitor.classList[Object.values(monitor.classList).indexOf('tecnica') + 1].replaceAll('_', ' ').split('-')

            areas_monitor.forEach(area => {
                if (!areas.includes(area)) {
                    areas.push(area)
                }
            })
        }
    }

    if (areas.length !== 0 ){
        $('#mensagem_tecnica').remove()
        $('#div_monitores_escalados').append(`<p class="alert-info" id="mensagem_tecnica">Técnico(s) de ${areas.join(', ')} escalado(s)</p>`)
    } else {
        $('#mensagem_tecnica').remove()
    }
}

function verificar_enfermeira(monitor){
    if (monitor.classList.contains('acampamento')) {
        $('#monitores_acampamento').append(monitor)
    } else {
        $('#monitores_hotelaria').append(monitor)
    }
}

function salvar_monitores_escalados() {

    if (monitores_escalados.length === 0) {
        $('.alert-warning').empty()
        $('#corpo_site').prepend('<p class="alert-warning">Nenhum monitor foi selecionado</p>')
    } else {
        $('.alert-warning').empty()
        $('#monitores_escalados').val(monitores_escalados)
        $('#enviar_formulario').click()
    }
}

function verificar_escalado(id_monitor, editando = false) {
    let ja_escalado = false
    let id_cliente

    if (editando) {
        id_cliente = $('#id_cliente').val()
    } else {
        id_cliente = $('#cliente').val()
    }

    $.ajax({
        type: 'POST',
        async: false,
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_monitor': id_monitor, 'cliente': id_cliente},
        success: function (response) {

            if (response['acampamento']) {
                if ($('#mensagem').length === 0) {
                    $('#escalar').append('<p class="alert-danger" style="width: 98%; margin-left: 1%" id="mensagem">Monitor(es) presente(s) em escala do acampamento na data em questão!</p>')
                }
                ja_escalado = true
            }

            if (response['hotelaria']) {
                if ($('#mensagem').length === 0) {
                    $('#escalar').append('<p class="alert-danger" style="width: 98%; margin-left: 1%" id="mensagem">Monitor(es) presente(s) em escala da hotelaria na data em questão!</p>')
                }
                ja_escalado = true
            }
        }
    })
    return ja_escalado
}

function pegar_escalados() {
    let monitores = $('#monitores_escalados').val().replace('[', '').replace(']', '').split(', ')

    for (let i = 0; i < monitores.length; i++) {
        if (monitores[i] !== '') {
            monitores_escalados.push(monitores[i])
        }
    }
}

function active_botao_salvar() {
    $('#botao_salvar_escala').prop('disabled', false)
}

$('document').ready(function () {
    jQuery('#form_evento').submit(function () {
        let dados = jQuery(this).serialize();
        //aqui voce pega o conteudo do atributo action do form
        let url = $(this).attr('action');
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
            }
        })
    });
});