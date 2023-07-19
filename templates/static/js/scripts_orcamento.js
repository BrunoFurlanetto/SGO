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

function enviar_form(form_opcionais = null) {
    let dados_op
    const form = $('#orcamento')
    const valores_opcionais = form_opcionais
    const orcamento = form.serializeObject()
    let dados = { orcamento }
    const url = form.attr('action')

    return new Promise(function (resolve, reject) {
        loading()

        if (valores_opcionais !== null) {
            dados_op =  valores_opcionais.serializeObject()
        }

        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            dataType: 'JSON',
            data: {orcamento, dados_op},
            success: function (response) {
                resolve(response)
            },
            error: function (xht, status, error) {
                reject(error)
            }
        })
    })
}

$.fn.serializeObject = function(){
    let obj = {}
    let array = this.serializeArray()

    $.each(array, function () {
        if (obj[this.name]) {
            if (!obj[this.name].push) {
                obj[this.name] = [obj[this.name]]
            }
            obj[this.name].push(this.value || '')
        } else {
            obj[this.name] = this.value || ''
        }
    })

    return obj
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
        $('#periodo_viagem, #subtotal').addClass('none')

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
        $('#container_periodo, #subtotal').removeClass('none')
    } else {
        $('#container_periodo, #subtotal').addClass('none')
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
            const valores = response['data']['valores']
            const valor_somado = (response['data']['periodo_viagem']['valor'] + valores['diaria']['valor_com_desconto']).toFixed(2)
            console.log(response)
            if (response['status'] == 'success') {
                $('#container_periodo .parcial').text('R$ ' + valor_somado.replace('.', ',')).addClass('visivel')
                $('.div-flutuante').text('R$ ' + response['data']['total']['valor'].toFixed(2).replace('.', ',')).addClass('visivel')
                $('#container_monitoria_transporte').removeClass('none')
            } else {
                $('#container_monitoria_transporte').addClass('none')
                $('#container_periodo .parcial').text('').removeClass('visivel')
                $('.div-flutuante').removeClass('visivel')
            }
        }).catch(function (error) {
            $('#container_periodo .parcial').text('').removeClass('visivel')
            $('.div-flutuante').text('').removeClass('mostrar')
            alert(error)
        })
    } else {
        $('#container_periodo .parcial').text('').removeClass('visivel')
        $('.div-flutuante').removeClass('visivel')
    }
    end_loading()
}

function verificar_monitoria_transporte() {
    if ($('#id_tipo_monitoria').val() !== '' && $('#id_transporte').val() != '') {
        $('#id_opcionais, #id_outros').select2()

        enviar_form().then(function (response) {
            const valores = response['data']['valores']
            const valor_somado = (valores['transporte']['valor'] + valores['tipo_monitoria']['valor']).toFixed(2)

            if (response['status'] === 'success') {
                $('#container_monitoria_transporte .parcial').text('R$ ' + valor_somado.replace('.', ',')).addClass('visivel')
                $('.div-flutuante').text('R$ ' + response['data']['total']['valor'].toFixed(2).replace('.', ',')).addClass('visivel')
                $('#container_opcionais, #finalizacao').removeClass('none')
            } else {
                $('#container_opcionais, #finalizacao').addClass('none')
            }
        }).catch(function (error) {
            alert(error)
        })
    } else {
        $('#container_opcionais, #finalizacao').addClass('none')
    }
    end_loading()
}

function enviar_op(opcionais) {
    enviar_form().then(function (response) {
        if (response['status'] === 'success') {
            const valores = response['data']['valores']
            console.log(response)
            $('.div-flutuante').text('R$ ' + response['data']['total']['valor'].toFixed(2).replace('.', ',')).addClass('mostrar')
            $('#container_opcionais .parcial').text('R$ ' + valores['opcionais']['valor_com_desconto'].toFixed(2).replace('.', ',')).addClass('visivel')
        } else {
            $('#container_opcionais .parcial').text('').removeClass('visivel')
        }
    }).catch((xht, response, error) => {
        $('#container_opcionais .parcial').text('').removeClass('visivel')
        alert(error)
    })

    atualizar_lista_valores()
    end_loading()
}

function atualizar_lista_valores() {
    const opcionais_fixo = $('#id_opcionais').val()
    const outros = $('#id_outros').val()
    const opcionais = [opcionais_fixo, outros].flat()
    $('#tabela_de_opcionais tbody').empty()

    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'lista_opcionais': opcionais, 'teste': 'teste'},
    }).then((response) => {
        let i = 1
        let readonly = ''

        for (let opcional of response['retorno']) {
            if (opcional['fixo']) {
                readonly = 'disabled'
            }

            $('#tabela_de_opcionais tbody').append(
                `<tr>
                    <th><input type="text" id="opcional_${i}" name="opcional_${i}" value="${opcional['nome']}" disabled></th>
                    <input type="hidden" id="id_opcional_${i}" name="opcional_${i}" value="${opcional['id']}">
                    <input type="hidden" id="valor_bd_opcional_${i}" name="opcional_${i}" value="${opcional['valor']}">
                    <th><input type="text" id="valor_opcional_${i}" ${readonly} name="opcional_${i}" value="${opcional['valor'].toFixed(2).replace('.', ',')}"></th>
                    <th><input type="text" id="desconto_opcional_${i}" name="opcional_${i}" value="0,00" onchange="aplicar_desconto(this)"></th>
                </tr>`
            )
            $(`#valor_opcional_${i}, #desconto_opcional_${i}`).maskMoney({
                prefix: 'R$ ',
                thousands: '.',
                decimal: ',',
                allowZero: true,
                affixesStay: false
            })
            i++
        }
    }).catch((xht, response, error) => {
        alert(error)
    })
}

function aplicar_desconto(desconto) {
    const posicao = $(desconto).prop('name').split('_')[1]
    const opcional = $(`#valor_opcional_${posicao}`)
    const valor_bd_opcional = parseFloat($(`#valor_bd_opcional_${posicao}`).val().replace(',', '.'))
    const valor_opcional = parseFloat($(opcional).val().replace(',', '.'))
    const desconto_aplicado = parseFloat($(desconto).val().replace(',', '.'))
    const novo_valor = valor_bd_opcional - desconto_aplicado
    opcional.val(`${novo_valor.toFixed(2).replace('.', ',')}`)
    console.log(opcional, valor_opcional)
}

function enviar_atualizacao() {
    const form = $('#valores_outros_opcionais')
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
                $('#id_outros').append(newOption).trigger('change')
                $('#adicionar_opcional').modal('hide')
            }
        })
    }
}