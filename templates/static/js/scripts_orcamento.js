let resultado_ultima_consulta = {}
let op_extras = []
let mostrar_instrucao = true
let enviar = false
const secoes = ['diaria', 'tipo_monitoria', 'transporte', 'opcionais', 'atividades', 'atividades_ceu', 'outros']

$(document).ready(() => {
    $('#id_cliente').select2()
    let hoje = new Date()
    $('#data_pagamento').val(moment(hoje).add(15, 'd').format('YYYY-MM-DD'))

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

    $('#valor_opcional, #desconto_produto, #desconto_monitoria').maskMoney({
        prefix: 'R$ ',
        thousands: '.',
        decimal: ',',
        allowZero: true,
        affixesStay: false
    })
    $('#desconto_transporte, #desconto_geral').maskMoney({
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

    $("#id_opcionais, #op_extras, #id_atividades, #id_atividades_ceu").on("select2:select", async function (e) {
        const opcao = e.params.data;
        const opcionais = $('.opcionais').length
        const i = opcionais + 1
        let nome_id = $(this).attr('id')
        loading()

        try {
            if (nome_id !== 'op_extras') {
                await enviar_form()

                $.ajax({
                    type: 'GET',
                    url: '',
                    data: {'nome_id': nome_id, 'id': opcao['id']},
                    success: function (response) {
                        const valor_selecao = response['valor'].toLocaleString(
                            undefined,
                            {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }
                        ).replace('.', ',')

                        if (nome_id == 'id_atividades') {
                            $('#tabela_de_opcionais tbody').append(`
                                <tr id="op_${opcao['id']}" class="opcionais">
                                    <th><input type="text" id="atividade_peraltas_${i}" name="atividade_peraltas_${i}" value='${opcao['text']}' disabled></th>
                                    <input type="hidden" id="id_atividade_peraltas_${i}" name="atividade_peraltas_${i}" value="${opcao['id']}">                    
                                    <input type="hidden" id="valor_bd_atividade_peraltas_${i}" name="atividade_peraltas_${i}" value='${valor_selecao}' disabled>
                                    <th><input type="text" id="valor_atividade_peraltas_${i}" disabled name="atividade_peraltas_${i}" value='${valor_selecao}'></th>
                                    <th><input type="text" id="desconto_atividade_peraltas_${i}" name="atividade_peraltas_${i}" value="0,00" onchange="aplicar_desconto(this)"></th> 
                                </tr>
                            `)
                        } else if (nome_id == 'id_atividades_ceu') {
                            $('#tabela_de_opcionais tbody').append(`
                                <tr id="op_${opcao['id']}" class="opcionais">
                                    <th><input type="text" id="atividade_ceu_${i}" name="atividade_ceu_${i}" value='${opcao['text']}' disabled></th>
                                    <input type="hidden" id="id_atividade_ceu_${i}" name="atividade_ceu_${i}" value="${opcao['id']}">                    
                                    <input type="hidden" id="valor_bd_atividade_ceu_${i}" name="atividade_ceu_${i}" value='${valor_selecao}' disabled>
                                    <th><input type="text" id="valor_atividade_ceu_${i}" disabled name="atividade_ceu_${i}" value='${valor_selecao}'></th>
                                    <th><input type="text" id="desconto_atividade_ceu_${i}" name="atividade_ceu_${i}" value="0,00" onchange="aplicar_desconto(this)"></th> 
                                </tr>
                            `)
                        } else {
                            $('#tabela_de_opcionais tbody').append(`
                                <tr id="op_${opcao['id']}" class="opcionais">
                                    <th><input type="text" id="opcional_${i}" name="opcional_${i}" value="${opcao['text']}" disabled></th>
                                    <input type="hidden" id="id_opcional_${i}" name="opcional_${i}" value="${opcao['id']}">                    
                                    <input type="hidden" id="valor_bd_opcional_${i}" name="opcional_${i}" value='${valor_selecao}' disabled>
                                    <th><input type="text" id="valor_opcional_${i}" disabled name="opcional_${i}" value='${valor_selecao}'></th>
                                    <th><input type="text" id="desconto_opcional_${i}" name="opcional_${i}" value="0,00" onchange="aplicar_desconto(this)"></th> 
                                </tr>
                            `)
                        }

                    }
                }).done(async () => {
                    $(`#valor_opcional_${i}, #desconto_opcional_${i}`).maskMoney({
                        prefix: 'R$ ',
                        thousands: '.',
                        decimal: ',',
                        allowZero: true,
                        affixesStay: false
                    })

                    await atualizar_valores_op()
                })
            } else {
                await enviar_form()

                let opcional_extra = op_extras.filter((op, index) => {
                    console.log(op['id'], opcao['id'])
                    if (op['id'] === opcao['id']) {
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

            }
        } catch (error) {
            alert(error)
        } finally {
            end_loading()
        }
        end_loading()
    })

    $("#id_opcionais, #op_extras, #id_atividades, #id_atividades_ceu").on("select2:unselect", async function (e) {
        loading()

        try {
            await enviar_form()
            const opcao = e.params.data;
            $(`#op_${opcao['id']}`).remove()
        } catch (error) {
            alert(error)
        } finally {
            await atualizar_valores_op()
            end_loading()
        }
    })
})

function formatar_dinheiro(valor) {
    return valor.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})
}

function criar_linhas_tabela_valores() {
    const tabela_valores = $('#tabela_de_valores tbody').empty()
    tabela_valores.append(`<tr id="diaria"><td colspan="2">Diarias</td></tr>`)
    tabela_valores.append(`<tr id="tipo_monitoria"><td colspan="2">Monitoria</td></tr>`)
    tabela_valores.append(`<tr id="transporte"><td colspan="2">Transporte</td></tr>`)
    tabela_valores.append(`<tr id='opcionais'><td colspan="2">Atividades Peraltas<i class='bx bxs-chevron-down' onclick="$('#tabela_de_valores .opcionais_descritivo').toggleClass('none')"></i></td></tr>`)
    tabela_valores.append(`<tr id='atividades'><td colspan='2'>Opcionais<i class='bx bxs-chevron-down' onclick="$('#tabela_de_valores .atividades_descritivo').toggleClass('none')"></i></td></tr><tr id='atividades_descritivo'></tr>`)
    tabela_valores.append(`<tr id='atividades_ceu'><td colspan='2'>Atividades CEU<i class='bx bxs-chevron-down' onclick="$('#tabela_de_valores .atividades_ceu_descritivo').toggleClass('none')"></i></td></tr><tr id='ceu_descritivo'></tr>`)
    tabela_valores.append(`<tr id='outros'><td colspan='2'>Outros<i class='bx bxs-chevron-down' onclick="$('#tabela_de_valores .outros_descritivo').toggleClass('none')"></i></td></tr><tr id='outros_descritivo'></tr>`)
}

function separar_atividades(opcionais) {
    let opts = []

    for (let opt in opcionais) {
        if (opcionais[opt] !== opcionais[opcionais.length - 1]) {
            opts.push(opcionais[opt])
        }
    }

    return opts
}

function linhas_descritivo_opcionais(opcionais, id_linha) {
    let i = 1
    let classe_ultima_linha = ''

    for (let opt in opcionais) {
        let opcional = opcionais[opt]
        let linhaEspecifica = $(`#tabela_de_valores #${id_linha}`);
        let classe_ultimo_valor = ''

        if (i == 1) {
            classe_ultima_linha = 'ultima_linha'
        }

        let novaLinha = `<tr id='${id_linha}_${i}' class="${id_linha}_descritivo none atividade_ou_opcional">
            <td></td>
            <td>${opcional['nome']}</td>
            <td><nobr>R$ ${formatar_dinheiro(opcional['valor'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opcional['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opcional['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opcional['valor'] - opcional['valor_com_desconto'])}</nobr></td>
            <td class="valor_final_tabela ${classe_ultima_linha}"><nobr>R$ ${formatar_dinheiro(opcional['valor_final'])}</nobr></td>
        </tr>`
        linhaEspecifica.after(novaLinha)

        for (let valor_dia of opcional['valores']) {
            $(`#tabela_de_valores #${id_linha}_${i}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
        }

        i++
    }
}

function tabela_descrito(valores, dias, opcionais, totais) {
    $('#tabela_de_valores .datas').remove()
    $('.tag_datas').prop('colspan', dias.length)
    let classe_datas = ''

    for (let data of dias) {
        let dia = moment(data)

        if (data == dias[dias.length - 1]) {
            classe_datas = 'ultima_data'
        }

        $('#tabela_de_valores .cabecalho').append(`<th class="datas ${classe_datas}">${dia.format('DD/MM')}</th>`)
    }

    criar_linhas_tabela_valores(secoes)

    for (let secao of secoes) {
        $(`#tabela_de_valores #${secao}`).append(`
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['valor'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['valor'] - valores[secao]['valor_com_desconto'])}</nobr></td>
            <td class="valor_final_tabela"><nobr>R$ ${formatar_dinheiro(valores[secao]['valor_final'])}</nobr></td>
        `)

        for (let valor_dia of valores[secao]['valores']) {
            $(`#tabela_de_valores #${secao}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
        }

        if (opcionais.length > 1 && secao == 'opcionais') {
            linhas_descritivo_opcionais(separar_atividades(opcionais), 'opcionais')
        } else if (opcionais[opcionais.length - 1]['atividades'].length > 0 && secao == 'atividades') {
            linhas_descritivo_opcionais(opcionais[opcionais.length - 1]['atividades'], 'atividades')
        } else if (opcionais[opcionais.length - 1]['atividades_ceu'].length > 0 && secao == 'atividades_ceu') {
            linhas_descritivo_opcionais(opcionais[opcionais.length - 1]['atividades_ceu'], 'atividades_ceu')
        } else if (opcionais[opcionais.length - 1]['outros'].length > 0 && secao == 'outros') {
            linhas_descritivo_opcionais(opcionais[opcionais.length - 1]['outros'], 'outros')
        }
    }

    $('#tabela_de_valores tbody').append(`
        <tr id="totais">
            <td></td>
            <th>Total</th>
            <th><nobr>R$ ${formatar_dinheiro(totais['valor'])}</nobr></th>            
            <th><nobr>R$ ${formatar_dinheiro(totais['taxa_comercial'])}</nobr></th>            
            <th><nobr>R$ ${formatar_dinheiro(totais['comissao_de_vendas'])}</nobr></th>            
            <th><nobr>R$ ${formatar_dinheiro(totais['valor'] - totais['valor_com_desconto'])}</nobr></th>            
            <th class="valor_final_tabela"><nobr>R$ ${formatar_dinheiro(totais['valor_final'])}</nobr></th>            
        </tr>
    `)

    for (let valor of totais['descricao_valores']) {
        $('#tabela_de_valores #totais').append(`<th><nobr>R$ ${formatar_dinheiro(valor)}</nobr></th>`)
    }
}

async function enviar_form(form_opcionais = false, form_gerencia = false, salvar = false) {
    let dados_op, gerencia, outros;
    const form = $('#orcamento');
    const orcamento = form.serializeObject();
    const url = form.attr('action');

    if (op_extras.length > 0) {
        outros = op_extras.filter((op, index) => {
            if ($('#op_extras').val().includes(op['id'])) {
                return op;
            }
        });
    }

    if (form_opcionais || salvar) {
        dados_op = $('#forms_valores_op').serializeObject();
    }

    if (form_gerencia || salvar) {
        gerencia = $('#form_gerencia').serializeObject();
    }

    try {
        const response = await new Promise(function (resolve, reject) {
            $.ajax({
                url: url,
                headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                type: "POST",
                dataType: 'JSON',
                data: {orcamento, dados_op, gerencia, outros, 'salvar': salvar},
                success: function (response) {
                    if (!salvar) {
                        const valores = response['data']['valores']
                        const periodo = response['data']['periodo_viagem']['valor_com_desconto']
                        const diaria = valores['diaria']['valor_com_desconto']
                        const periodo_diaria = (periodo + diaria)
                        const periodo_diaria_formatado = formatar_dinheiro(periodo_diaria)

                        const valor_monitoria = valores['tipo_monitoria']['valor_com_desconto'];
                        const transporte = valores['transporte']['valor_com_desconto'];
                        const monitoria_transporte = (valor_monitoria + transporte);
                        const monitoria_transporte_formatado = formatar_dinheiro(monitoria_transporte)

                        const opcionais = valores['opcionais']['valor_com_desconto']
                        const atividades = valores['atividades']['valor_com_desconto']
                        const atividade_ceu = valores['atividades_ceu']['valor_com_desconto']
                        const outros = valores['outros']['valor_com_desconto']
                        const total = response['data']['total']['valor_final']
                        const opcionais_e_atividades_formatado = formatar_dinheiro(opcionais + outros + atividades + atividade_ceu)
                        const total_formatado = formatar_dinheiro(total)

                        // Alteração dos valores das seções
                        $('#container_periodo .parcial').text('R$ ' + periodo_diaria_formatado); // Periodo da viagem
                        $('#container_monitoria_transporte .parcial').text('R$ ' + monitoria_transporte_formatado); // Monitoria + transporte
                        $('#container_opcionais .parcial').text('R$ ' + opcionais_e_atividades_formatado); // Opcionais
                        $('#subtotal span').text('R$ ' + total_formatado); // Total

                        tabela_descrito(valores, response['data']['days'], response['data']['descricao_opcionais'], response['data']['total'])
                        resultado_ultima_consulta = response
                    }


                    resolve(response['status']);
                },
                error: function (xht, status, error) {
                    reject(xht['responseJSON']['msg']);
                }
            });
        });

        return response;
    } catch (error) {
        alert(error);
        throw error; // Lança o erro novamente para que a chamada de enviar_form() a capture
    }
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

function separar_produtos(periodo) {
    if (!enviar) {
        enviar = true;
        return
    }

    let check_in = $(periodo).val().split(' - ')[0]
    let check_out = $(periodo).val().split(' - ')[1]

    $.ajax({
        type: 'GET',
        url: '',
        data: {'check_in': check_in, 'check_out': check_out},
        success: function (response) {
            for (let produto of $('#id_produto option')) {
                if (response['ids'].includes(parseInt($(produto).val()))) {
                    $(produto).prop('disabled', false)
                } else {
                    $(produto).prop('disabled', true)
                }
            }
        }
    }).done(() => {
        $('#id_produto').prop('disabled', false)
    })
}

async function verificar_preenchimento() {
    const floatingBox = $('#floatingBox')
    $('.div-flutuante').removeClass('none')

    if ($('#data_viagem').val() != '' && ($('#id_produto').val() != null && $('#id_produto').val() != '')) {
        loading()

        try {
            await enviar_form()
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
        } catch (error) {
            $('#container_periodo .parcial').removeClass('visivel')
            $('.div-flutuante').removeClass('visivel').addClass('none')

            alert(error)
        } finally {
            end_loading()
        }
    } else {
        $('#container_periodo .parcial').removeClass('visivel')
        $('.div-flutuante').removeClass('visivel').addClass('none')
    }

}

async function verificar_monitoria_transporte() {
    if ($('#id_tipo_monitoria').val() !== '' && $('input[name="transporte"]:checked').val() != undefined) {
        setTimeout(() => {
            $('#id_opcionais, #op_extras, #id_atividades, #id_atividades_ceu').select2()
        }, 300)
        loading()

        try {
            await enviar_form()
            $('#container_monitoria_transporte .parcial').addClass('visivel')
            $('#container_opcionais, #finalizacao').removeClass('none')
        } catch (error) {
            $('#container_monitoria_transporte .parcial').removeClass('visivel')
            $('#container_opcionais, #finalizacao').addClass('none')

            alert(error)
        } finally {
            end_loading()
        }
    } else {
        $('#container_opcionais, #finalizacao').addClass('none')
    }
}

async function enviar_op(opcionais) {
    loading()

    try {
        await enviar_form()
        $('#container_opcionais .parcial').addClass('visivel')
    } catch (error) {
        $('#container_opcionais .parcial').text('').removeClass('visivel')
        alert(error)
    } finally {
        end_loading()
    }
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

async function atualizar_valores_op(carregar=false) {
    if (carregar) {
        loading()
    }

    try {
        await enviar_form($('#forms_valores_op'), null)
        $('#valores_outros_opcionais').modal('hide')
    } catch (error) {
        alert(error)
        $('#valores_outros_opcionais').modal('hide')
    } finally {
        if (carregar) {
            end_loading()
        }
    }
}

async function enviar_infos_gerencia() {
    loading()

    try {
        await enviar_form(null, $('#form_gerencia'))
        $('#modal_gerencia').modal('hide')
    } catch (error) {
        alert(error)
        $('#modal_gerencia').modal('hide')
    } finally {
        end_loading()
    }
}

async function salvar_orcamento() {
    loading()

    try {
        await enviar_form(false, false, true)
        window.location.href = '/'
    } catch (error) {
        alert(error)
    } finally {
        end_loading()
    }
}

