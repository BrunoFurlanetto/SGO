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
let niveis_selecionados = []

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
    const monitores_totais = id_escalados.length
    const coordenadores_totais = $('#monitores_escalados').children().map((index, monitor) => {
        if (monitor.classList.contains('coordenador')) {
            return monitor
        }
    }).get().length

    if (monitores_totais > (n_monitores + n_coordenadores)) {
        $('#escalar').append('<div id="alerta_monitores" class="alerta_racionais"><p class="alert alert-danger">Número de monitores escalados acima do permitido para o evento!</p></div>')
    }

    // if (coordenadores_totais > n_coordenadores) {
    //     $('#escalar').append('<div id="alerta_coordenadores" class="alerta_racionais"><p class="alert alert-danger">Número de coordenadores escalados acima do permitido para o evento!</p></div>')
    // }
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
    await verificar_racionais()
    atualizar_valor()
}

function atualizar_valor() {
    $.ajax({
        url: '/escala/peraltas/atualizar_valor/',
        type: 'GET',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {
            'id_monitores': id_escalados,
            'id_monitores_embarque': id_monitores_embarque,
            'id_biologos': id_monitores_biologo,
            'id_enfermeiras': id_enfermeiras,
            'id_coordenadores': id_coordenadores_escalados,
            'id_tecnicos': id_tecnicos,
            'check_in': $('#check_in').val(),
            'check_out': $('#check_out').val(),
        },
        success: function (response) {
            $('#alerta_valor_monitoria span').text(response)
        }
    });
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
    let areas_monitor = []

    for (let monitor of tecnicos_escalados) {
        if (monitor.classList.contains('tecnica')) {
            try {
                areas_monitor = monitor.classList[Object.values(monitor.classList).indexOf('tecnica') + 1].replaceAll('_', ' ').split('-')
            } catch (e) {
            }

            areas_monitor.forEach(area => {
                if (!areas.includes(area)) {
                    areas.push(area)
                }
            })
        }
    }

    if (areas.length !== 0) {
        $('#mensagem_tecnica').remove()
        $('#escalar').append(`<div id="mensagem_tecnica"><p class="alert alert-info">Técnico(s) escalado(s)</p></div>`)
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

let coresGeradas = [];
// Função para calcular a distância euclidiana entre duas cores
function calcularDistancia(cor1, cor2) {
    const r1 = parseInt(cor1.slice(1, 3), 16);
    const g1 = parseInt(cor1.slice(3, 5), 16);
    const b1 = parseInt(cor1.slice(5, 7), 16);

    const r2 = parseInt(cor2.slice(1, 3), 16);
    const g2 = parseInt(cor2.slice(3, 5), 16);
    const b2 = parseInt(cor2.slice(5, 7), 16);

    return Math.sqrt(Math.pow(r1 - r2, 2) + Math.pow(g1 - g2, 2) + Math.pow(b1 - b2, 2));
}

function gerarCorAleatoria() {
    let cor;

    do {
        // Gerar componentes de cor de 0 a 255
        const r = Math.floor(Math.random() * 200) + 56; // Vermelho
        const g = Math.floor(Math.random() * 200) + 56; // Verde
        const b = Math.floor(Math.random() * 200) + 56; // Azul

        // Convertendo para formato hexadecimal
        cor = '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
    } while (coresGeradas.some(existingCor => calcularDistancia(existingCor, cor) < 40)); // Distância mínima

    coresGeradas.push(cor); // Adiciona a nova cor ao array
    return cor;
}

// Função para mapear cores a cada nível
function aplicarCoresPorNivel() {
    const coresPorNivel = {};

    // Selecionar todos os monitores e legendas
    const monitores = document.querySelectorAll('.card-monitor');
    const legendas = document.querySelectorAll('.card-monitor-legenda');

    // Mapear as cores aleatórias para os níveis das legendas
    legendas.forEach(function (legenda) {
        const nivel = legenda.getAttribute('data-nivel');
        const cor = gerarCorAleatoria();
        coresPorNivel[nivel] = cor;

        // Aplicar a cor à legenda
        legenda.style.backgroundColor = cor;
        legenda.style.color = definirCorTexto(cor); // Definindo a cor do texto com base na cor de fundo
    });

    // Aplicar as cores aos monitores com base no nível
    monitores.forEach(function (monitor) {
        if (!monitor.classList.contains('enfermeira')) {
            const nivel = monitor.getAttribute('data-nivel');
            const cor = coresPorNivel[nivel];  // Recuperar a cor associada ao nível

            // Aplicar a cor ao monitor
            monitor.style.backgroundColor = cor;
            monitor.style.color = definirCorTexto(cor); // Definindo a cor do texto com base na cor de fundo
        }
    });
}

// Função para definir a cor do texto com base na cor de fundo
function definirCorTexto(cor) {
    // Converter a cor hexadecimal para valores RGB
    const r = parseInt(cor.slice(1, 3), 16);
    const g = parseInt(cor.slice(3, 5), 16);
    const b = parseInt(cor.slice(5, 7), 16);

    // Calcular a luminância usando a fórmula de luminância relativa
    const luminancia = (0.299 * r + 0.587 * g + 0.114 * b);

    // Se a luminância for maior que um certo limiar, retorna preto, senão retorna branco
    return luminancia > 186 ? '#000' : '#fff'; // 186 é um valor de limiar que pode ser ajustado
}

// Executar a função quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', aplicarCoresPorNivel);

function filtrar_niveis(div, nivel) {
    let monitores_disponiveis = $('#monitores_acampamento').children()

    if (niveis_selecionados.includes(nivel)) {
        $(div).removeClass('clicado')
        niveis_selecionados.splice(niveis_selecionados.indexOf(nivel), 1)
    } else {
        $(div).addClass('clicado')
        niveis_selecionados.push(nivel)
    }

    for (let monitor of monitores_disponiveis) {
        if (niveis_selecionados.length == 0) {
            $(monitor).removeClass('none')
        } else {
            if (niveis_selecionados.includes($(monitor).data('nivel'))) {
                $(monitor).removeClass('none')
            } else {
                $(monitor).addClass('none')
            }
        }
    }
}

function salvar_monitores_escalados(setor, pre_escala, data, editando = false) {
    const monitores_escalados = $('#monitores_escalados').children()
    const monitores_escalados_embarque = $('#monitor_embarque').children()
    const enfermeiras_escaladas = $('#enfermagem').children()
    let url_save = ''
    let erro_sem_alteracao = false
    let erro_biologo = false
    let erro_monitor_embarque = false
    let erro_2_enfermeiras = false
    let erro_3_enfermeiras = false
    $('#mensagem_sem_monitor').remove()

    if (setor == 'acampamento') {
        url_save = '/escala/peraltas/acampamento/salvar/'
    } else {
        url_save = `/escala/peraltas/hotelaria/salvar/${data}/`
    }

    if (setor == 'acampamento') {
        if (produto === 'Só CEU') {
            if ((id_escalados.length + id_monitores_embarque.length + id_tecnicos) === 0) {
                if (editando) {
                    $('#corpo_site').prepend('<p class="alert alert-warning" id="mensagem_sem_monitor">Nenhuma alteração detectada</p>')
                } else {
                    $('#corpo_site').prepend('<p class="alert alert-warning" id="mensagem_sem_monitor">Nenhum monitor foi selecionado</p>')
                }
                erro_sem_alteracao = true
            }
        } else {
            if ((id_escalados.length + id_monitores_embarque.length) === 0) {
                if (editando) {
                    $('#corpo_site').prepend('<p class="alert alert-warning" id="mensagem_sem_monitor">Nenhuma alteração detectada</p>')
                } else {
                    $('#corpo_site').prepend('<p class="alert alert-warning" id="mensagem_sem_monitor">Nenhum monitor foi selecionado</p>')
                }
                erro_sem_alteracao = true
            }
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
    }

    if ($('#escalar .alerta_racionais').length > 0) {
        let count = 0;
        let interval = setInterval(function () {
            jQuery('#escalar .alerta_racionais').animate({opacity: 0.7}, 100, "linear", function () {
                jQuery(this).delay(50);
                jQuery(this).animate({opacity: 1}, 100, function () {
                });
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

    $('.container_loading').removeClass('none')
    $.ajax({
        url: url_save,
        type: 'POST',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {
            'id_escala': $('#escala_editada').val(),
            'id_monitores': id_escalados,
            'id_monitores_embarque': id_monitores_embarque,
            'id_biologos': id_monitores_biologo,
            'id_enfermeiras': id_enfermeiras,
            'id_coordenadores': id_coordenadores_escalados,
            'id_tecnicos': id_tecnicos,
            'evento': $('#cliente').val(), // Os nomes não batem porque alterei de ID do cliente para ID da Ficha de Evento, mas como não tinha tempo pra poder corrigir tudo preferi manter algumas partes como antes
            'check_in': $('#check_in').val(),
            'check_out': $('#check_out').val(),
            'observacoes': $('#observacoes').val(),
            'pre_escala': pre_escala,
        },
        success: function (response) {
            window.location.href = '/escala/peraltas/'
        }
    });
}
