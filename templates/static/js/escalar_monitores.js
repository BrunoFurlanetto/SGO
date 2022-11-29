const niveis = ['coordenadores', 'monitores', 'auxiliares']
const espacos = document.querySelectorAll('.espacos')
let id_enfermeiras_disponiveis = []
let id_monitores_acampamento = []
let id_monitores_hotelaria = []
let id_monitores_embarque = []
let id_enfermeiras = []
let id_escalados = []
let areas = []

espacos.forEach((espaco) => {
    espaco.addEventListener('dragover', (e) => {
        const arrastando = document.querySelector('.arrastando')

        if (arrastando !== null) {
            const nova_posicao = pegar_nova_posicao(espaco, e.clientY)
            e.preventDefault()
            e.dataTransfer.dropEffect = 'move'

            if (nova_posicao) {
                nova_posicao.insertAdjacentElement('afterend', arrastando)
            } else {
                espaco.prepend(arrastando)
            }
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
    const monitores = espaco.querySelectorAll('.card-monitor')
    const tipo_escalacao = espaco.id
    verificar_escalados()

    // ---------------------------------este pra retorno na disponibilidade correta ------------------------------------
    if (tipo_escalacao === 'monitores_hotelaria') {
        let lista_de_ids = []

        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()

            if (!lista_de_ids.includes(monitor.id)){
                lista_de_ids.push(monitor.id)
            } else {
                $('#monitores_acampamento').append(monitor)
            }

            if (monitor.classList.contains('acampamento') && !monitor.classList.contains('hotelaria')) {
                $('#monitores_acampamento').append(monitor)
            } else if (monitor.classList.contains('acampamento') && monitor.classList.contains('hotelaria')) {
                voltar_disponibilidade_dupla(monitor, 'monitores_acampamento')
            }
        }
    }

    if (tipo_escalacao === 'monitores_acampamento') {
        let lista_de_ids = []

        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()

            if (!lista_de_ids.includes(monitor.id)){
                lista_de_ids.push(monitor.id)
            } else {
                $('#monitores_hotelaria').append(monitor)
            }

            if (monitor.classList.contains('hotelaria') && !monitor.classList.contains('acampamento')) {
                $('#monitores_hotelaria').append(monitor)
            } else if (monitor.classList.contains('hotelaria') && monitor.classList.contains('acampamento')) {
                voltar_disponibilidade_dupla(monitor, 'monitores_hotelaria')
            }
        }
    }
    // -----------------------------------------------------------------------------------------------------------------
    if (tipo_escalacao === 'monitores_escalados') {
        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
            if (monitor.classList.contains('enfermeira')) $('#enfermeiras').append(monitor)
            verificar_ja_escalado(monitor.id)
            verificar_escala_dupla(monitor)
        }
    }

    if (tipo_escalacao === 'monitor_embarque') {
        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
            verificar_escala_dupla(monitor)
        }
    }

    if (tipo_escalacao === 'enfermagem') {
        for (let monitor of monitores) {
            if (!monitor.classList.contains('enfermeira')) verificar_enfermeira(monitor)
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
        }

    }
}

function voltar_disponibilidade_dupla(monitor, id_disponibilidade){
    const monitores_duplicados = $('#disponibilidade_duplicada').children()

    for (let monitor_duplicado of monitores_duplicados){
        if (monitor.id === monitor_duplicado.id){
            $(`#${id_disponibilidade}`).append(monitor_duplicado)
        }
    }
}

function verificar_escalados() {
    const id_espacos = [
        'monitores_escalados', 'monitor_embarque',
        'enfermagem', 'monitores_acampamento',
        'monitores_hotelaria', 'enfermeiras'
    ]
    const lista_de_ids = [
        id_escalados, id_monitores_embarque,
        id_enfermeiras, id_monitores_acampamento,
        id_monitores_hotelaria, id_enfermeiras_disponiveis
    ]

    for (let i in id_espacos){
        let monitores_escalados = $(`#${id_espacos[i]}`).children()
        let id_monitores = []

        for (let monitor of monitores_escalados) {
            id_monitores.push(monitor.id)

            if (!lista_de_ids[i].includes(monitor.id)) {
                lista_de_ids[i].push(monitor.id)
            }
        }

        for (let id of lista_de_ids[i]) {
            if (!id_monitores.includes(id)) lista_de_ids[i].splice(lista_de_ids[i].indexOf(id), 1)
        }
    }
}

function verificar_escala_dupla(monitor){
    const monitores_hotelaria = $('#monitores_hotelaria').children()
    const monitores_acampamento = $('#monitores_acampamento').children()

    for (let monitor_teste of monitores_hotelaria){
        if (monitor_teste.id === monitor.id) $('#disponibilidade_duplicada').append(monitor_teste)
    }

    for (let monitor_teste of monitores_acampamento){
        if (monitor_teste.id === monitor.id) $('#disponibilidade_duplicada').append(monitor_teste)
    }

}

function verificar_tecnica() {
    let monitores_escalados = $('#monitores_escalados').children()
    const monitores_embarque = $('#monitor_embarque').children()
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

    for (let monitor of monitores_embarque) {
        if (monitor.classList.contains('tecnica')) {
            let areas_monitor = monitor.classList[Object.values(monitor.classList).indexOf('tecnica') + 1].replaceAll('_', ' ').split('-')

            areas_monitor.forEach(area => {
                if (!areas.includes(area)) {
                    areas.push(area)
                }
            })
        }
    }

    if (areas.length !== 0) {
        $('#mensagem_tecnica').remove()
        $('#escalar').append(`<div id="mensagem_tecnica"><p class="alert-info">Técnico(s) de ${areas.join(', ')} escalado(s)</p></div>`)
    } else {
        $('#mensagem_tecnica').remove()
    }
}

function verificar_enfermeira(monitor) {
    if (monitor.classList.contains('acampamento') && !id_monitores_acampamento.includes(monitor.id)) {
        $('#monitores_acampamento').append(monitor)
        voltar_disponibilidade_dupla(monitor, 'monitores_hotelaria')
    } else {
        $('#monitores_hotelaria').append(monitor)
        voltar_disponibilidade_dupla(monitor, 'monitores_hotelaria')
    }
}

function verificar_ja_escalado(id_monitor) {
    let id_cliente = $('#cliente').val()
    $('#mensagem').remove()

    $.ajax({
        type: 'POST',
        async: false,
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_monitor': id_monitor, 'cliente': id_cliente},
        success: function (response) {

            if (response['acampamento']) {
                $('#escalar').append('<p class="alert-danger" style="width: 98%; margin-left: 1%" id="mensagem">Monitor(es) presente(s) em escala do acampamento na data em questão!</p>')
            }

            if (response['hotelaria']) {
                $('#escalar').append('<p class="alert-danger" style="width: 98%; margin-left: 1%" id="mensagem">Monitor(es) presente(s) em escala da hotelaria na data em questão!</p>')
            }
        }
    })
}

function salvar_monitores_escalados(btn, editando=false){
    $('#mensagem_sem_monitor').remove()

    if (id_escalados.length === 0) {
        window.scroll({top: 0, behavior: 'smooth'});

        if (editando){
            $('#corpo_site').prepend('<p class="alert-warning" id="mensagem_sem_monitor">Nenhuma alteração detectada</p>')
        } else {
            $('#corpo_site').prepend('<p class="alert-warning" id="mensagem_sem_monitor">Nenhum monitor foi selecionado</p>')
        }

        return
    }
    console.log('Aqui')

    $.ajax({
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        async: false,
        type: "POST",
        data: {'id_monitores': id_escalados,
               'id_monitores_embarque': id_monitores_embarque,
               'id_enfermeiras': id_enfermeiras,
               'cliente': $('#cliente').val(),
               'check_in': $('#check_in').val(),
               'check_out': $('#check_out').val(),
        },
        success: function (response){
            window.location.href = '/escala/peraltas/'
        }
    });
}



