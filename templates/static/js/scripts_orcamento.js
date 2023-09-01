let resultado_ultima_consulta = {}
let op_extras = []
let mostrar_instrucao = true

$(document).ready(() => {
    let hoje = new Date()
    $('#data_viagem').daterangepicker({
        "timePicker": true,
        "timePicker24Hour": true,
        "timePickerIncrement": 30,
        "locale": {
            "format": "DD/MM/YYYY HH:mm",
            "separator": " - ",
            "applyLabel": "Salvar",
            "cancelLabel": "Limpar",
            "daysOfWeek": [
                "Dom",
                "Seg",
                "Ter",
                "Qua",
                "Qui",
                "Sex",
                "Sab"
            ],
            "monthNames": [
                "Janeiro",
                "Fevereiro",
                "Março",
                "Abril",
                "Maio",
                "Junho",
                "Julho",
                "Agosto",
                "Setembro",
                "Outubro",
                "Novembro",
                "Dezembro"
            ]
        },
        "showCustomRangeLabel": false,
        "alwaysShowCalendars": true,
        "drops": "up"
    })
    $('#data_pagamento').val(moment(hoje).add(15, 'd').format('YYYY-MM-DD'))

    $('#id_cliente').select2()
    $('#valor_opcional, #desconto_produto, #desconto_monitoria').maskMoney({
        prefix: 'R$ ',
        thousands: '.',
        decimal: ',',
        allowZero: true,
        affixesStay: false
    })
    $('#desconto_trasnporte, #desconto_geral').maskMoney({
        prefix: 'R$ ',
        thousands: '.',
        decimal: ',',
        allowZero: true,
        affixesStay: false
    })
    $('#comissao, #taxa_comercial').mask('00,00%', {reverse: true})

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
    })

    $("#id_opcionais, #op_extras").on("select2:select", function (e) {
        const opcional = e.params.data;
        const opcionais = $('.opcionais').length
        const i = opcionais + 1

        if (this.id === 'id_opcionais') {
            enviar_form().then((status) => {
                $.ajax({
                    type: 'GET',
                    url: '',
                    data: {'id_opcional': opcional['id']},
                    success: function (response) {
                        const valor_op = response['valor'].toLocaleString(
                            undefined,
                            {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }
                        ).replace('.', ',')

                        $('#tabela_de_opcionais tbody').append(`
                            <tr id="op_${opcional['id']}" class="opcionais">
                                <th><input type="text" id="opcional_${i}" name="opcional_${i}" value="${opcional['text']}" disabled></th>
                                <input type="hidden" id="id_opcional_${i}" name="opcional_${i}" value="${opcional['id']}">                    
                                <input type="hidden" id="valor_bd_opcional_${i}" name="opcional_${i}" value="${valor_op}" disabled>
                                <th><input type="text" id="valor_opcional_${i}" disabled name="opcional_${i}" value="${valor_op}"></th>
                                <th><input type="text" id="desconto_opcional_${i}" name="opcional_${i}" value="0,00" onchange="aplicar_desconto(this)"></th> 
                            </tr>
                        `)
                    }
                }).done(() => {
                    $(`#valor_opcional_${i}, #desconto_opcional_${i}`).maskMoney({
                        prefix: 'R$ ',
                        thousands: '.',
                        decimal: ',',
                        allowZero: true,
                        affixesStay: false
                    })

                    end_loading()
                })
            }).catch((error) => {
                alert(error)
                end_loading()
            })
        } else {
            enviar_form().then(() => {
                let opcional_extra = op_extras.filter((op, index) => {
                    console.log(op['id'], opcional['id'])
                    if (op['id'] === opcional['id']) {
                        return op
                    }
                })[0]

                $('#tabela_de_opcionais tbody').append(`
                    <tr id="op_${opcional_extra['id']}" class="opcionais">
                        <th><input type="text" id="opcional_${i}" name="opcional_${i}" value="${opcional_extra['nome']}" disabled></th>                                 
                        <th><input type="text" id="valor_opcional_${i}" disabled name="opcional_${i}" value="${opcional_extra['valor']}"></th>
                        <th><input type="text" id="desconto_opcional_${i}" name="opcional_${i}" value="0,00" disabled></th> 
                    </tr>
                `)
            }).catch((error) => {
                alert(error)
            })

            end_loading()
        }
    });

    $("#id_opcionais, #op_extras").on("select2:unselect", function (e) {
        enviar_form().then((status) => {
            const opcional = e.params.data;
            $(`#op_${opcional['id']}`).remove()
            end_loading()
        }).catch((error) => {
            alert(error)
            end_loading()
        })
    })
})

function enviar_form(form_opcionais = false, form_gerencia = false, salvar = false) {
    let dados_op, gerencia, outros
    const form = $('#orcamento')
    const orcamento = form.serializeObject()
    const url = form.attr('action')
    loading()

    if (op_extras.length > 0) {
        outros = op_extras.filter((op, index) => {
            console.log(op)
            if ($('#op_extras').val().includes(op['id'])) {
                return op
            }
        })
    }

    if (form_opcionais || salvar) {
        dados_op = $('#forms_valores_op').serializeObject()
    }

    if (form_gerencia || salvar) {
        gerencia = $('#form_gerencia').serializeObject()
    }

    return new Promise(function (resolve, reject) {
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            dataType: 'JSON',
            data: {orcamento, dados_op, gerencia, outros, 'salvar': salvar},
            success: function (response) {

                if (!salvar) {
                    const valores = response['data']['valores'];
                    const periodo = response['data']['periodo_viagem']['valor_com_desconto'];
                    const diaria = valores['diaria']['valor_com_desconto'];
                    const periodo_diaria = (periodo + diaria);

                    // Adicionando ponto de separação de milhar em periodo_diaria
                    const periodo_diaria_formatado = periodo_diaria.toLocaleString(
                        undefined,
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }
                    )
                    const valor_monitoria = valores['tipo_monitoria']['valor_com_desconto'];
                    const transporte = valores['transporte']['valor_com_desconto'];
                    const monitoria_transporte = (valor_monitoria + transporte);

                    // Adicionando ponto de separação de milhar em monitoria_transporte
                    const monitoria_transporte_formatado = monitoria_transporte.toLocaleString(
                        undefined,
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }
                    )

                    const opcionais = valores['opcionais']['valor_com_desconto'];
                    const outros = valores['outros']['valor_com_desconto']
                    const total = response['data']['total']['valor_final'];

                    // Adicionando ponto de separação de milhar em opcionais e total
                    const opcionais_formatado = (opcionais + outros).toLocaleString(
                        undefined,
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }
                    )

                    const total_formatado = total.toLocaleString(
                        undefined,
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }
                    )

                    // Alteração dos valores das seções
                    $('#container_periodo .parcial').text('R$ ' + periodo_diaria_formatado); // Periodo da viagem
                    $('#container_monitoria_transporte .parcial').text('R$ ' + monitoria_transporte_formatado); // Monitoria + transporte
                    $('#container_opcionais .parcial').text('R$ ' + opcionais_formatado); // Opcionais

                    $('#subtotal span').text('R$ ' + total_formatado); // Total

                    resultado_ultima_consulta = response
                }

                resolve(response['status'])
            },
            error: function (xht, status, error) {
                reject(error)
            }
        })
    })
}

$.fn.serializeObject = function () {
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
    const floatingBox = $("#floatingBox")
    $('.div-flutuante').removeClass('none')

    if (!verificacao.includes(undefined) && !verificacao.includes('') && !verificacao.includes('0')) {
        enviar_form().then(function (status) {
            $('#container_periodo .parcial').addClass('visivel')
            $('.div-flutuante').addClass('visivel')
            $('#container_monitoria_transporte').removeClass('none')

            if (mostrar_instrucao) {
                setTimeout(() => {
                    floatingBox.removeClass('none')
                }, 900)
                setTimeout(() => {
                    floatingBox.addClass('none')
                }, 2000)
                mostrar_instrucao = false
            }
        }).catch(function (error) {
            $('#container_periodo .parcial').removeClass('visivel')
            $('.div-flutuante').removeClass('visivel').addClass('none')

            alert(error)
        })
    } else {
        $('#container_periodo .parcial').removeClass('visivel')
        $('.div-flutuante').removeClass('visivel').addClass('none')
    }
    end_loading()
}

function verificar_monitoria_transporte() {
    if ($('#id_tipo_monitoria').val() !== '' && $('#id_transporte').val() != '') {
        $('#id_opcionais, #op_extras').select2()

        enviar_form().then(function (status) {
            $('#container_monitoria_transporte .parcial').addClass('visivel')
            $('#container_opcionais, #finalizacao').removeClass('none')
        }).catch(function (error) {
            $('#container_monitoria_transporte .parcial').removeClass('visivel')
            $('#container_opcionais, #finalizacao').addClass('none')

            alert(error)
        })
    } else {
        $('#container_opcionais, #finalizacao').addClass('none')
    }
    end_loading()
}

function enviar_op(opcionais) {
    enviar_form().then(function (status) {
        $('#container_opcionais .parcial').addClass('visivel')
    }).catch((xht, response, error) => {
        $('#container_opcionais .parcial').text('').removeClass('visivel')
        alert(error)
    })
    end_loading()
}

function aplicar_desconto(desconto) {
    const posicao = $(desconto).prop('name').split('_')[1]
    const opcional = $(`#valor_opcional_${posicao}`)
    const valor_bd_opcional = parseFloat($(`#valor_bd_opcional_${posicao}`).val().replace(',', '.'))
    const valor_opcional = parseFloat($(opcional).val().replace(',', '.'))
    const desconto_aplicado = parseFloat($(desconto).val().replace(',', '.'))
    const novo_valor = valor_bd_opcional - desconto_aplicado
    opcional.val(`${novo_valor.toFixed(2).replace('.', ',')}`)
}

function adicionar_novo_op() {
    const nome_opcional = $('#nome_opcional').val()
    const valor_opcional = $('#valor_opcional').val()
    const descricao_opcional = $('#descricao_opcional').val()
    const teste = [nome_opcional, valor_opcional, descricao_opcional]
    $('#adicionar_opcional #aviso').addClass('none')

    if (teste.includes('')) {
        $('#adicionar_opcional #aviso').removeClass('none').text('Verifique se todos os campos estão preenchidos corretamente!')

        return
    }

    const n_op = op_extras.length + 1

    op_extras.push({
        'id': `OPCEXT${n_op.toString().padStart(2, '0')}`,
        'nome': nome_opcional,
        'valor': valor_opcional,
        'descricao': descricao_opcional,
    })

    let newOption = new Option(
        nome_opcional,
        `OPCEXT${n_op.toString().padStart(2, '0')}`,
        true,
        true
    );

    $('#op_extras').append(newOption).trigger('change')

    $('#op_extras').trigger({
        type: 'select2:select',
        params: {
            data: {
                id: `OPCEXT${n_op.toString().padStart(2, '0')}`,
                text: nome_opcional
            }
        }
    })

    $('#adicionar_opcional').modal('hide')
    console.log(op_extras)
}

function atualizar_valores_op() {
    enviar_form($('#forms_valores_op'), null).then((status) => {
        end_loading()
        $('#valores_outros_opcionais').modal('hide')
    }).catch((error) => {
        alert(error)
        $('#valores_outros_opcionais').modal('hide')
        end_loading()
    })
}

function enviar_infos_gerencia() {
    enviar_form(null, $('#form_gerencia')).then((status) => {
        end_loading()
        $('#modal_gerencia').modal('hide')
    }).catch((error) => {
        alert(error)
        end_loading()
        $('#modal_gerencia').modal('hide')
    })
}

function salvar_orcamento() {
    enviar_form(false, false, true).then((status) => {
        window.location.href = '/'
    }).catch((error) => {
        alert(error)
        end_loading()
    })
}

