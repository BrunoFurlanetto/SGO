$(document).ready(() => {
    $('#id_cliente').select2()
})

function ativar_mascara() {
    setTimeout(() => {
        $('.select2-search__field').mask("99.999.999/9999-99")
    }, 10)
}

function gerar_responsaveis(cliente) {
    const id_cliente = cliente.value
    const responsaveis = $('#id_responsavel').children()

    if (id_cliente === '') {
        $('#id_responsavel').prop('disabled', true).val('')
        $('#periodo_viagem').addClass('none')

        return
    }

    $.ajax({
        type: 'GET',
        url: '',
        data: {'id_cliente': id_cliente},
        success: function (response) {
            for (let opcao of responsaveis) {
                if (response['responsaveis'].includes(parseInt(opcao.value))) {
                    opcao.classList.remove('none')
                } else {
                    opcao.classList.add('none')
                }
            }
        }
    }).done(() => {
        $('#id_responsavel').prop('disabled', false)
    })
}

function liberar_periodo(id_responsavel) {
    if (id_responsavel !== ''){
        $('#periodo_viagem').removeClass('none')
    } else {
        $('#periodo_viagem').addClass('none')
    }
}

function verificar_preenchimento(){
    const periodo = $('#id_periodo_viagem').val()
    const dias = $('#id_n_dias').val()
    const hora_entrada = $('input[name="hora_check_in"]:checked').val()
    const hora_saida = $('input[name="hora_check_out"]:checked').val()
    const verificacao = [periodo, dias, hora_entrada, hora_saida]

    if (!verificacao.includes(undefined) && !verificacao.includes('') && !verificacao.includes('0')) {
        envio_periodo(periodo, dias, hora_entrada, hora_saida)
    } else {
        $('#monitoria').addClass('none')
    }
}

function envio_periodo(periodo, dias, hora_entrada, hora_saida) {
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {
            'period': periodo,
            'days': dias,
            'comming': hora_entrada,
            'exit': hora_saida
        },
    }).done((response) => {
        if (response['status'] == 'success') {
            $('#monitoria').removeClass('none')
        } else {
            $('#monitoria').addClass('none')
        }
    })
}
