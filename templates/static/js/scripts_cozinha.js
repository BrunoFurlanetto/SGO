$(document).ready(() => {
    $('#fichas_evento').select2({
        width: '100%'
    })
})

function atualizar_participantes() {
    const n_adultos = parseInt($('#participantes #adultos').val())
    const n_criancas = parseInt($('#participantes #criancas').val())
    const n_monitoria = parseInt($('#participantes #monitoria').val())
    $('.total_monitores').val(n_monitoria)
    $('.total').val(n_adultos + n_criancas + n_monitoria)
}

function zerar_refeicao_grupo(celula_pai) {
    const refeicao_data_evento = celula_pai.className
    $(`.${refeicao_data_evento} input`).prop('disabled', true)
    $(`.${refeicao_data_evento} button`).toggleClass('none')
    atualizar_totais(refeicao_data_evento)
}

function adicionar_refeicao_grupo(celula_pai) {
    const refeicao_data_evento = celula_pai.className
    $(`.${refeicao_data_evento} input`).prop('disabled', false)
    $(`.${refeicao_data_evento} button`).toggleClass('none')
    atualizar_totais(refeicao_data_evento)
}

function atualizar_totais(refeicao_data_evento) {
    const valores = $(`input.${refeicao_data_evento.split('-')[0]}`)
    let soma_adultos = 0, soma_criancas = 0, soma_monitoria = 0, soma_geral = 0;
    const refeicao = refeicao_data_evento.split('-')[0]
    const totais_refeicao = $(`.${refeicao}`)

    valores.each(function () {
        const classe = $(this).attr('class')
        const valor = parseInt($(this).val(), 10) || 0

        if (!$(this).prop('disabled')) {
            if (classe.includes('adultos')) soma_adultos += valor
            else if (classe.includes('criancas')) soma_criancas += valor
            else if (classe.includes('monitoria')) soma_monitoria += valor
            else if (classe.includes('geral')) soma_geral += valor
        }
    })

    totais_refeicao.each(function () {
        const classe_total = $(this).attr('class');
        const valor_total = parseInt($(this).text(), 10) || 0; // Obtém o texto do <td> e converte em número

        if (classe_total.includes('total_adultos')) {
            $(this).text(soma_adultos); // Atualiza o texto do <td>
        } else if (classe_total.includes('total_criancas')) {
            $(this).text(soma_criancas); // Atualiza o texto do <td>
        } else if (classe_total.includes('total_monitoria')) {
            $(this).text(soma_monitoria); // Atualiza o texto do <td>
        } else if (classe_total.includes('total_geral')) {
            $(this).text(soma_geral); // Atualiza o texto do <td>
        }
    })
}

function atualizar_monitoria(monitoria) {
    const refeicao_data_evento = monitoria.parentNode.className
    let soma_valores = 0
    $(`.${refeicao_data_evento} input[type='number']`).each(function () {
        if (!$(this).attr('class').includes('geral')) {
            let valor = parseInt($(this).val(), 10) || 0; // Converte para número, ou 0 se for inválido
            soma_valores += valor
        }
    })
    $(`.${refeicao_data_evento} .geral`).val(soma_valores)
    atualizar_totais(refeicao_data_evento)
}