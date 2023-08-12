let valor_atual, valores_op, valor_base, taxas_base
let taxa_comercial_base = null
let comisao_base = null
let taxa_comercial = null
let valores_descontos
let comissao = null
let descontos_aplicados = 0
let novas_taxas = 0
let comissao_aplicada = false
let taxa_aplicada = false

function alterar_aba(aba, sectionId) {
    const conteudos_abas = [
        'orcamentos_aprovacao',
        'orcamentos_aprovados',
        'log'
    ]
    $('.folder:not([ativo])').removeClass('ativo')
    $(aba).addClass('ativo')

    for (let conteudo of conteudos_abas) {
        if (conteudo === sectionId) {
            $(`#${conteudo}`).addClass('ativo')
        } else {
            $(`#${conteudo}`).removeClass('ativo')
        }
    }
}

function reiniciar_variaveis() {
    valor_atual = null
    valores_op = null
    valor_base = null
    taxas_base = null
    taxa_comercial_base = null
    comisao_base = null
    taxa_comercial = null
    valores_descontos = 0
    comissao = null
    descontos_aplicados = 0
    novas_taxas = 0
    comissao_aplicada = false
    taxa_aplicada = false
}

function mostrar_modal_aprovacao(id_linha) {
    reiniciar_variaveis()
    $('#select_all_pedidos, #select_all_op').prop('checked', false)
    const id_orcamento = parseInt($(id_linha).attr('id').split('_')[1])
    loading()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': id_orcamento},
        success: function (response) {
            const tabela_pedidos = $('#tabela_pedidos tbody').empty()
            const tabela_opcionais = $('#tabela_descontos_opcionais tbody').empty()
            taxa_comercial_base = 5  // TODO: Alterar para pegar valores base do back
            comisao_base = 9  // TODO: Alterar para pegar valores base do back
            taxas_base = taxa_comercial_base + comisao_base  // TODO: Alterar para pegar valores base do back
            valor_base = response['valor_base']
            let taxas = calcular_taxas()
            valores_descontos = response['pedidos']
            valores_op = response['opcionais']
            valor_atual = valor_base + taxas
            $('#comentario_pedido').text('OBS do colaborador: ' + response['observacoes'])
            $('#valores #valor_tratativa').text(convert_money(response['valor_com_desconto']))
            $('#valores #valor_atual').text(convert_money(valor_atual))
            console.log(response)
            for (let pedido of response['pedidos']) {
                let valor_formatado, valor_padrao
                console.log(pedido)
                if (pedido['campo'].includes('desconto')) {
                    valor_formatado = convert_money(pedido['valor_tratativa'])
                    valor_padrao = convert_money(pedido['base'])
                } else if (pedido['campo'] !== 'data_pagamento') {
                    valor_formatado = pedido['valor_tratativa'].toLocaleString() + '%'
                    valor_padrao = pedido['base'].toLocaleString() + '%'

                    if (pedido['campo'] === 'comissao') {
                        comissao = pedido['valor_tratativa']
                    }

                    if (pedido['campo'] === 'taxa_comercial') {
                        taxa_comercial = pedido['valor_tratativa']
                    }
                } else {
                    valor_formatado = pedido['valor_tratativa']
                    valor_padrao = pedido['base']
                }

                tabela_pedidos.append(`
                    <tr>
                        <td>${pedido['verbose']}</td>
                        <td>${valor_padrao}</td>
                        <td>${valor_formatado}</td>
                        <td><input type="checkbox" class="check" onchange="calcular_aceites(this)" id="${pedido['campo']}" name="${pedido['campo']}"></td>
                    </tr>
                `)
            }

            for (let op of response['opcionais']) {
                tabela_opcionais.append(`
                    <tr>
                        <td>${op['nome']}</td>                    
                        <td>${convert_money(op['valor'])}</td>                    
                        <td>${convert_money(op['desconto'])}</td>                    
                        <td>${convert_money(op['valor_com_desconto'])}</td>                    
                        <td><input type="checkbox" onchange="calcular_aceites(this)" class="check" id="${op['id']}" name="${op['nome'].toLowerCase().replaceAll(' ', '_')}"></td>                    
                    </tr>
                `)
            }
        }
    }).done((response) => {
        end_loading()
        $('#permissao_orcamentos').modal('show')
        if (!taxa_comercial) {
            taxa_comercial = 5 // TODO: Pegar valores do banco de dados depois
        }
        if (!comissao) {
            comissao = 9 // TODO: Pegar valores do banco de dados depois
        }
    }).catch((error) => {
        alert(error)
        end_loading()
    })
}

function convert_money(valor) {
    return 'R$ ' + valor.toLocaleString(
        undefined,
        {minimumFractionDigits: 2, maximumFractionDigits: 2}
    )
}

function selecionar_todos(select_all) {
    const status_select_all = $(select_all).prop('checked')
    const tabela = $(select_all).closest('table')
    tabela.find('.check').prop('checked', status_select_all).trigger('change')
}

function calcular_aceites(aceite) {
    const nome = $(aceite).attr('name')

    if (nome.includes('desconto')) {
        for (let pedido of valores_descontos) {
            if (nome === pedido['campo']) {
                if ($(aceite).prop('checked')) {
                    descontos_aplicados += pedido['valor_tratativa']
                } else {
                    descontos_aplicados -= pedido['valor_tratativa']
                }
            }
        }
    }

    if (nome === 'comissao') {
        comissao_aplicada = !!$(aceite).prop('checked');
    }

    if (nome === 'taxa_comercial') {
        taxa_aplicada = !!$(aceite).prop('checked');
    }

    if (valores_op) {
        for (let objeto of valores_op) {
            if (nome == objeto['nome'].toLowerCase().replaceAll(' ', '_')) {
                if ($(aceite).prop('checked')) {
                    descontos_aplicados += objeto['desconto']
                } else {
                    descontos_aplicados -= objeto['desconto']
                }
            }
        }
    }
    novas_taxas = calcular_taxas()
    valor_atual = (valor_base - descontos_aplicados) + novas_taxas
    $('#valores #valor_atual').text(convert_money(valor_atual))
}

function calcular_taxas() {
    let valor_comissao, valor_taxa
    console.log(comissao_aplicada, taxa_aplicada)

    if (comissao_aplicada && taxa_aplicada) {
        valor_comissao = ((valor_base - descontos_aplicados) / (1 - (comissao / 100))) - (valor_base - descontos_aplicados)
        valor_taxa = ((valor_base - descontos_aplicados) / (1 - (taxa_comercial / 100))) - (valor_base - descontos_aplicados)

        return valor_comissao + valor_taxa
    } else if (comissao_aplicada && !taxa_aplicada) {
        valor_comissao = ((valor_base - descontos_aplicados) / (1 - (comissao / 100))) - (valor_base - descontos_aplicados)
        valor_taxa = ((valor_base - descontos_aplicados) / (1 - (taxa_comercial_base / 100))) - (valor_base - descontos_aplicados)

        return valor_comissao + valor_taxa
    } else if (taxa_aplicada && !comissao_aplicada) {
        valor_comissao = ((valor_base - descontos_aplicados) / (1 - (comisao_base / 100))) - (valor_base - descontos_aplicados)
        valor_taxa = ((valor_base - descontos_aplicados) / (1 - (taxa_comercial / 100))) - (valor_base - descontos_aplicados)

        return valor_comissao + valor_taxa
    } else {
        valor_comissao = ((valor_base - descontos_aplicados) / (1 - (comisao_base / 100))) - (valor_base - descontos_aplicados)
        valor_taxa = ((valor_base - descontos_aplicados) / (1 - (taxa_comercial_base / 100))) - (valor_base - descontos_aplicados)

        return valor_comissao + valor_taxa
    }
}
