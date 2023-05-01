const niveis = ['coordenadores', 'monitores', 'auxiliares']
const espacos = document.querySelectorAll('.espacos')
let id_enfermeiras_disponiveis = []
let id_monitores_acampamento = []
let id_monitores_hotelaria = []
let id_monitores_embarque = []
let id_monitores_biologo = []
let id_tecnicos = []
let id_coordenadores_escalados = []
let outras_escalas = []
let id_enfermeiras = []
let id_escalados = []
let areas = []

espacos.forEach((espaco) => {
    espaco.addEventListener('dragover', (e) => {
        const arrastando = document.querySelector('.arrastando')

        if (arrastando !== null) {
            const nova_posicao = pegar_nova_posicao(espaco, e.clientX)
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

function pegar_nova_posicao(local, posX) {
    const cards_monitor = local.querySelectorAll('.card-monitor:not(.arrastando)')
    let resultado

    for (let card_referencia of cards_monitor) {
        const box = card_referencia.getBoundingClientRect()
        const centro_horizontal_do_box = box.x + box.width / 2

        if (posX >= centro_horizontal_do_box) resultado = card_referencia
    }

    return resultado
}

// ---------------------------------------------------------------------------------------------------------------------
function remover_escalado_clique(monitor) {
    $(`#monitor_embarque #${monitor.id}`).removeClass('embarque')
    id_escalados.splice(id_escalados.indexOf(monitor.id), 1)
    monitor.remove()
}

function trocar_card_monitor_escalado(monitor) {
    $(`#monitores_escalados #${monitor.id}`).remove()
    $('#monitores_escalados').append(monitor)
}

async function verificar_racionais() {
    $('#escalar .alerta_racionais').remove()
    const monitores_totais = id_escalados.length + id_monitores_embarque.length + id_monitores_biologo.length

    if (monitores_totais > n_monitores) {
        $('#escalar').append('<div id="alerta_monitores" class="alerta_racionais"><p class="alert alert-danger">Número de monitores escalados acima do permitido para o evento!</p></div>')
    }
}

async function escalado(espaco) {
    const monitores = espaco.querySelectorAll('.card-monitor')
    const tipo_escalacao = espaco.id
    // ---------------------------------este pra retorno na disponibilidade correta ------------------------------------
    if (tipo_escalacao === 'monitores_acampamento') {
        let lista_de_ids = []

        for (let monitor of monitores) {
            $(`#${monitor.id}`).removeClass('escalado')

            if (monitor.classList.contains('embarque')) {
                $(monitor).removeClass('embarque')

                if (monitor.children.length > 0) {
                    $(`#monitor_embarque #${monitor.id}`).removeClass('embarque')
                    monitor.remove()
                } else {
                    trocar_card_monitor_escalado(monitor)
                }

                return
            }

            if (monitor.classList.contains('tecnica')) verificar_tecnica()

            if (!lista_de_ids.includes(monitor.id) && !monitor.classList.contains('embarque')) {
                lista_de_ids.push(monitor.id)
            } else {
                $('#monitores_hotelaria').append(monitor)
            }

            if (monitor.classList.contains('enfermeira')) $('#enfermeiras_disponiveis').append(monitor)
        }
    }
    // -----------------------------------------------------------------------------------------------------------------
    if (tipo_escalacao === 'monitores_escalados' || tipo_escalacao === 'monitor_embarque') {
        for (let monitor of monitores) {
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
            if (monitor.classList.contains('enfermeira')) $('#enfermeiras_disponiveis').append(monitor)
            if (tipo_escalacao === 'monitor_embarque') duplicar_escalado(monitor)
            if (tipo_escalacao === 'monitores_escalados') {
                if ($(`#monitores_escalados .embarque`).length > 1) {
                    for (let card_monitor of $(`#monitores_escalados .embarque`)) {
                        if (card_monitor.children.length > 0) {
                            card_monitor.remove()
                        } else {
                            $(card_monitor).removeClass('embarque')
                        }
                    }
                }
            }
        }
    }

    if (tipo_escalacao === 'enfermagem') {
        for (let monitor of monitores) {
            if (!monitor.classList.contains('enfermeira')) verificar_enfermeira(monitor)
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
        }
    }

    if (tipo_escalacao === 'biologos') {
        for (let monitor of monitores) {
            if (!monitor.classList.contains('biologo')) verificar_biologo(monitor)
            if (monitor.classList.contains('tecnica')) verificar_tecnica()
        }
    }

    if (tipo_escalacao === 'coordenadores_escalados') {
        for (let monitor of monitores) {
            if (!monitor.classList.contains('coordenador')) {
                $('#monitores_acampamento').append(monitor)
            }
        }
    }

    if (tipo_escalacao === 'tecnicos_escalados') {
        for (let monitor of monitores) {
            if (!monitor.classList.contains('tecnica')) {
                $('#monitores_acampamento').append(monitor)
            } else {
                verificar_tecnica()
            }
        }
    }

    verificar_escalados()
    verificar_racionais()
}

function duplicar_escalado(monitor) {
    if (!id_escalados.includes(monitor.id) && !id_monitores_embarque.includes(monitor.id)) {
        $(monitor).addClass('embarque').clone().appendTo($('#monitores_escalados'))
        $(`#monitores_escalados #${monitor.id}`).append('<button class="btn btn-close" style="font-size: 12px; margin-left: 5px" onclick="remover_escalado_clique(this.parentNode)"></button>')
    }
}

function verificar_escalados() {
    const id_espacos = [
        'monitores_escalados', 'monitor_embarque',
        'enfermagem', 'monitores_acampamento',
        'monitores_hotelaria', 'enfermeiras',
        'biologos', 'coordenadores_escalados',
        'tecnicos_escalados'
    ]
    const lista_de_ids = [
        id_escalados, id_monitores_embarque,
        id_enfermeiras, id_monitores_acampamento,
        id_monitores_hotelaria, id_enfermeiras_disponiveis,
        id_monitores_biologo, id_coordenadores_escalados,
        id_tecnicos
    ]
    // Importante para garantir a ordem da escala informada pelo usuário em caso de ser para a hotelaria
    if (window.location.href.split('/').includes('hotelaria')) id_escalados.length = 0

    for (let i in id_espacos) {
        let monitores_escalados = $(`#${id_espacos[i]}`).children()
        let id_monitores = []

        for (let monitor of monitores_escalados) {
            id_monitores.push(monitor.id)

            if (!lista_de_ids[i].includes(monitor.id)) {
                lista_de_ids[i].push(monitor.id)
            }

            if (i == 0 || i == 1 || i == 6) {
                verificar_ja_escalado(monitor.id)

                if (monitor.classList.contains('escalado')) {
                    $('#mensagem').remove()
                    $('#escalar').append('<div id="mensagem"><p class="alert alert-danger">Monitor(es) já presente(s) em escala na data em questão!</p></div>')
                }
            } else {
                if (outras_escalas.indexOf(monitor.id) !== -1) {
                    outras_escalas.splice(outras_escalas.indexOf(monitor.id), 1)
                }
            }

            if (outras_escalas.length === 0) {
                $('#mensagem').remove()
            }


        }

        for (let id of lista_de_ids[i]) {
            if (!id_monitores.includes(id)) lista_de_ids[i].splice(lista_de_ids[i].indexOf(id), 1)
        }
    }
}

function verificar_biologo(monitor) {
    $(monitor).removeClass('escalado')

    if (!monitor.classList.contains('embarque')) {
        $('#monitores_acampamento').append(monitor)
    } else {
        monitor.remove()
    }
}

function verificar_tecnica() {
    let tecnicos_escalados = $('#tecnicos_escalados').children()
    let areas = []

    for (let monitor of tecnicos_escalados) {
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
        $('#escalar').append(`<div id="mensagem_tecnica"><p class="alert alert-info">Técnico(s) de ${areas.join(', ')} escalado(s)</p></div>`)
    } else {
        $('#mensagem_tecnica').remove()
    }
}

function verificar_enfermeira(monitor) {
    $(monitor).removeClass('escalado')

    if (!monitor.classList.contains('embarque')) {
        $('#monitores_acampamento').append(monitor)
    } else {
        monitor.remove()
    }
}

function verificar_ja_escalado(id_monitor) {
    let id_cliente = $('#cliente').val()
    window.scroll({top: 5000, behavior: 'smooth'});

    $.ajax({
        type: 'POST',
        async: false,
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_monitor': id_monitor, 'cliente': id_cliente},
        success: function (response) {
            if (response['acampamento']) {
                $(`#escalar #${id_monitor}`).addClass('escalado')

                if (!outras_escalas.includes(id_monitor)) {
                    outras_escalas.push(id_monitor)
                }
            }

            if (response['hotelaria']) {
                $(`#escalar #${id_monitor}`).addClass('escalado')

                if (!outras_escalas.includes(id_monitor)) {
                    outras_escalas.push(id_monitor)
                }
            }
        }
    })
}

function salvar_monitores_escalados(pre_escala, editando = false) {
    const monitores_escalados = $('#monitores_escalados').children()
    const monitores_escalados_embarque = $('#monitor_embarque').children()
    const enfermeiras_escaladas = $('#enfermagem').children()
    $('#mensagem_sem_monitor').remove()
    let erro_sem_alteracao = false
    let erro_biologo = false
    let erro_monitor_embarque = false
    let erro_2_enfermeiras = false
    let erro_3_enfermeiras = false

    if ((id_escalados.length + id_monitores_embarque.length) === 0) {
        if (editando) {
            $('#corpo_site').prepend('<p class="alert alert-warning" id="mensagem_sem_monitor">Nenhuma alteração detectada</p>')
        } else {
            $('#corpo_site').prepend('<p class="alert alert-warning" id="mensagem_sem_monitor">Nenhum monitor foi selecionado</p>')
        }
        erro_sem_alteracao = true
    }

    if ($('#obrigatoriedades')) {
        if ($('#obrigatoriedades .biologo_1').length > 0) {
            if (id_monitores_biologo < 1) {
                window.scroll({top: 0, behavior: 'smooth'});
                $('.biologo_1').css({'color': 'red'})
                erro_biologo = true
            } else {
                $('.biologo_1').css({'color': 'black'})
                erro_biologo = false
            }
        }

        if ($('#obrigatoriedades .embarque_1').length > 0 && monitores_escalados_embarque.length === 0) {
            $('.embarque_1').css({'color': 'red'})
            erro_monitor_embarque = true
        } else {
            $('.embarque_1').css({'color': 'black'})
            erro_monitor_embarque = false
        }

        if ($('#obrigatoriedades .enfermeira_2').length > 0 && enfermeiras_escaladas.length < 2) {
            $('.enfermeira_2').css({'color': 'red'})
            erro_2_enfermeiras = true
        } else {
            $('.enfermeira_2').css({'color': 'black'})
            erro_2_enfermeiras = false
        }

        if ($('#obrigatoriedades .enfermeira_3').length > 0 && enfermeiras_escaladas.length < 3) {
            $('.enfermeira_3').css({'color': 'red'})
            erro_3_enfermeiras = true
        } else {
            $('.enfermeira_3').css({'color': 'black'})
            erro_3_enfermeiras = false
        }
    }

    if ($('#escalar .alerta_racionais').length > 0) {
        let count = 0;
        let interval = setInterval(function () {
            jQuery('#escalar .alerta_racionais').animate({opacity: 0.7}, 100, "linear", function () {
                jQuery(this).delay(50);
                jQuery(this).animate({opacity: 1}, 100, function () {});
                jQuery(this).delay(50);
            });

            count++;

            if (count === 10) {
                clearInterval(interval);
            }
        }, 50)

        return
    }

    if (erro_sem_alteracao || erro_biologo || erro_monitor_embarque || erro_2_enfermeiras || erro_3_enfermeiras) {
        window.scroll({top: 0, behavior: 'smooth'});

        return
    }

    $.ajax({
        url: '',
        type: 'POST',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        async: false,
        data: {
            'id_escala': $('#escala_editada').val(),
            'id_monitores': id_escalados,
            'id_monitores_embarque': id_monitores_embarque,
            'id_biologos': id_monitores_biologo,
            'id_enfermeiras': id_enfermeiras,
            'id_coordenadores': id_coordenadores_escalados,
            'id_tecnicos': id_tecnicos,
            'cliente': $('#cliente').val(),
            'check_in': $('#check_in').val(),
            'check_out': $('#check_out').val(),
            'pre_escala': pre_escala,
        },
        success: function (response) {
            window.location.href = '/escala/peraltas/'
        }
    });
}
