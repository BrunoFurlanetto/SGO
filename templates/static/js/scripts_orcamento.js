let lista_valores = {}

$(document).ready(() => {
    $('#id_cliente').select2()
    $('#valor_opcional').maskMoney({prefix: 'R$ ', thousands: '.', decimal: ','})

    jQuery('#orcamento').submit(function () {
        const dados = jQuery(this).serialize()
        const url = $(this).attr('action')

        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
                console.log(response)
            }
        });

        return false
    });
})

function enviar_form() {
    const form = $('#orcamento')
    return new Promise(function (resolve, reject) {
        loading()
        const dados = form.serialize()
        const url = form.attr('action')
        let status

        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
                resolve(response)
            },
            error: function (xht, status, error) {
                reject(error)
            }
        })
    })
}

function atualizar_valor(etapa, valor_etapa) {
    let valor_total = 0.00
    lista_valores[etapa] = parseFloat(valor_etapa)
    console.log(lista_valores)
    for (let etapa in lista_valores) {
        valor_total += lista_valores[etapa]
    }

    return String(valor_total.toFixed(2)).replace('.', ',')
}

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
    if (id_responsavel !== '') {
        $('#container_periodo').removeClass('none')
    } else {
        $('#container_periodo').addClass('none')
    }
}

function verificar_preenchimento() {
    const periodo = $('#id_periodo_viagem').val()
    const dias = $('#id_n_dias').val()
    const hora_entrada = $('input[name="hora_check_in"]:checked').val()
    const hora_saida = $('input[name="hora_check_out"]:checked').val()
    const verificacao = [periodo, dias, hora_entrada, hora_saida]

    if (!verificacao.includes(undefined) && !verificacao.includes('') && !verificacao.includes('0')) {
        enviar_form().then(function (response) {
            const valores = response['data']

            if (response['status'] == 'success') {
                $('#container_periodo .parcial').text('R$ ' + valores['periodo'] + valores['valores']['meal']).addClass('visivel')
                $('.div-flutuante').text('R$ ' + valores['total']).addClass('mostrar')
                $('#container_monitoria_transporte').removeClass('none')
            } else {
                $('#container_monitoria_transporte').addClass('none')
                $('#container_periodo .parcial').text('').removeClass('visivel')
                $('.div-flutuante').text('').removeClass('mostrar')
            }
            end_loading()
        }).catch(function (error) {
            $('#container_periodo .parcial').text('').removeClass('visivel')
            $('.div-flutuante').text('').removeClass('mostrar')
            end_loading()
            alert(error)
        })
    } else {
        $('#container_periodo .parcial').text('').removeClass('visivel')
        $('.div-flutuante').removeClass('mostrar')
        $('#container_monitoria_transporte').addClass('none')
    }
}

function verificar_monitoria_transporte() {
    if ($('#id_tipo_monitoria').val() !== '' && $('#id_transporte').val() != '') {
        $('#id_opcionais').select2()
        enviar_form().then(function (response) {
            if (response['status']) {
                $('#container_monitoria_transporte .parcial').text('R$ ' + response['valor_etapa']).addClass('visivel')
                console.log(response['valor_etapa'])
                $('.div-flutuante').text('R$ ' + atualizar_valor('monitoria_transporte', response['valor_etapa'])).addClass('mostrar')
                $('#container_opcionais, #finalizacao').removeClass('none')
            } else {
                $('.div-flutuante').text('R$ ' + atualizar_valor('monitoria_transporte', response['valor_etapa'])).addClass('mostrar')
                $('#container_opcionais, #finalizacao').addClass('none')
            }
            end_loading()
        }).catch(function (error) {

            end_loading()
            alert(error)
        })
    } else {
        $('#container_opcionais, #finalizacao').addClass('none')
    }
}

function enviar_op(opcionais) {
    enviar_form().then(function (response) {
        if (response['status']) {
            $('.div-flutuante').text('R$ ' +  atualizar_valor('opcionais', response['valor_etapa']))
            $('#container_opcionais .parcial').text(response['valor_etapa']).addClass('visivel')
            end_loading()
        } else {
            $('#container_opcionais .parcial').text('').removeClass('visivel')
            $('.div-flutuante').text('R$ ' +  atualizar_valor('opcionais', response['valor_etapa']))
        }
    }).catch((xht, response, error) => {
        $('#container_opcionais .parcial').text('').removeClass('visivel')
        $('.div-flutuante').text('R$ ' +  atualizar_valor('opcionais', response['valor_etapa']))
        alert(error)
        end_loading()
    })
}

function adicionar_novo_op() {
    const nome_opcional = $('#nome_opcional').val()
    const valor_opcional = $('#valor_opcional').val()
    const descricao_opcional = $('#descricao_opcional').val()
    const verificacao = [nome_opcional, valor_opcional, descricao_opcional]

    if (!verificacao.includes('')) {
        $.ajax({
            type: 'POST',
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {
                'novo_opcional': nome_opcional,
                'valor': valor_opcional,
                'descricao': descricao_opcional,
            },
        }).done((response) => {
            if (response['adicionado']) {
                let newOption = new Option(
                    response['text'],
                    response['id'],
                    true,
                    true
                );
                $('#id_opcionais').append(newOption).trigger('change')
                $('#adicionar_opcional').modal('hide')
            }
        })
    }
}