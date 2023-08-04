let valor_atual, valores_descontos, valores_op, valor_base, taxas_base
let taxa_comercial_base = null
let comisao_base = null
let taxa_comercial = null
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

function mostrar_modal_aprovacao(id_linha) {
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
            valores_descontos = response['pedidos']
            valores_op = response['opcionais']
            valor_atual = valor_base / (1 - (taxas_base / 100))
            $('#comentario_pedido').text('OBS do colaborador: ' + response['observacoes'])
            $('#valores #valor_tratativa').text(convert_money(response['valor_com_desconto']))
            $('#valores #valor_atual').text(convert_money(valor_atual))


            for (let pedido of response['pedidos']) {
                let valor_formatado, valor_padrao

                Object.entries(pedido).forEach(([chave, valor]) => {
                    if (chave != 'observacoes') {
                        if (chave.includes('Desconto')) {
                            valor_formatado = convert_money(valor[0])
                            valor_padrao = convert_money(valor[1])
                        } else if (chave !== 'Data de pagamento') {
                            valor_formatado = valor[0].toLocaleString() + '%'
                            valor_padrao = valor[1].toLocaleString() + '%'

                            if (valor[2] === 'comissao') {
                                comissao = valor[0]
                            }

                            if (valor[2] === 'taxa_comercial') {
                                taxa_comercial = valor[0]
                            }
                        } else {
                            valor_formatado = valor[0]
                            valor_padrao = valor[1]
                        }

                        tabela_pedidos.append(`
                            <tr>
                                <td>${chave}</td>
                                <td>${valor_padrao}</td>
                                <td>${valor_formatado}</td>
                                <td><input type="checkbox" class="check" onchange="calcular_aceites(this)" id="${valor[2]}" name="${valor[2]}"></td>
                            </tr>
                        `)
                    }
                })
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
    }).done(() => {
        end_loading()
        $('#permissao_orcamentos').modal('show')
        if (!taxa_comercial) {
            taxa_comercial = 5
        }
        if (!comissao) {
            comissao = 9
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

    for (let objeto of valores_descontos) {
        let chave = Object.keys(objeto)[0]

        if (objeto[chave][2] === nome) {
            if (nome.includes('desconto')) {
                if ($(aceite).prop('checked')) {
                    descontos_aplicados += objeto[chave][0]
                } else {
                    descontos_aplicados -= objeto[chave][0]
                }
            }

            if (nome === 'comissao') {
                comissao_aplicada = !!$(aceite).prop('checked');
            }

            if (nome === 'taxa_comercial') {
                taxa_aplicada = !!$(aceite).prop('checked');
            }
        }
    }

     for (let objeto of valores_op) {
        if (nome == objeto['nome'].toLowerCase().replaceAll(' ', '_')) {
            if ($(aceite).prop('checked')) {
                descontos_aplicados += objeto['desconto']
            } else {
                descontos_aplicados -= objeto['desconto']
            }
        }
    }
    novas_taxas = calcular_taxas()
    valor_atual = (valor_base - descontos_aplicados) / (1 - (novas_taxas / 100))
    $('#valores #valor_atual').text(convert_money(valor_atual))
}

function calcular_taxas() {
    if (comissao_aplicada && taxa_aplicada) {
        return comissao + taxa_comercial
    } else if (comissao_aplicada && !taxa_aplicada) {
        return comissao + taxa_comercial_base
    } else if (taxa_aplicada && !comissao_aplicada) {
        return taxa_aplicada + comisao_base
    } else {
        return taxas_base
    }
}
