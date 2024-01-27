$(document).ready(() => {
    moment.locale('pt-br')

    $('#tabela_adesao').DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: 4, // Supondo que a primeira coluna contenha datas
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY'); // Formate a data como desejado
                }
                return data;
            }
        }],
        order: [
            [3, 'asc']
        ]
    })

    $('#status #tabela_status_ficha').DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: 4,
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY')
                }

                return data;
            }
        }],
        order: [4, 'asc']
    })

    $('#status #tabela_status_pre_reserva, #tabela_status_agendado, #tabela_status_ordem, #tabela_avisos, #tabela_sem_escala').DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: 3,
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY')
                }
                return data;
            }
        }],
        order: [3, 'asc']
    })
})

function alterar_aba(aba, sectionId) {
    const conteudos_abas = $('.section-content').map((index, aba) => {
        return aba.id
    })
    $('.folder:not([ativo])').removeClass('ativo')
    $(aba).addClass('ativo')
    console.log(aba, sectionId)
    for (let conteudo of conteudos_abas) {
        if (conteudo === sectionId) {
            $(`#${conteudo}`).addClass('ativo')
        } else {
            $(`#${conteudo}`).removeClass('ativo')
        }
    }
}

let valor_atual, valores_op, valor_base, taxas_base, btn, desconto
let taxa_comercial_base = null
let comisao_base = null
let taxa_comercial = null
let valores_descontos
let comissao = null
let opcionais_aplicados = 0
let novas_taxas = 0
let comissao_aplicada = false
let taxa_aplicada = false
let outros = []
let desconto_aplicado = 0

function alterar_aba(aba, sectionId) {
    const conteudos_abas = [
        'pacotes',
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
    opcionais_aplicados = 0
    novas_taxas = 0
    comissao_aplicada = false
    taxa_aplicada = false
    outros = []
    desconto = 0
    desconto_aplicado = 0
}

function mostrar_modal_aprovacao(id_linha) {
    reiniciar_variaveis()
    $('#select_all_pedidos #select_all_op').prop('checked', false)
    const id_orcamento = parseInt($(id_linha).attr('id').split('_')[1])
    loading()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': id_orcamento},
        success: function (response) {
            console.log(response['msg'])
            if (response['msg']) {
                alert(response['msg'])
                window.location.reload()
            }

            const tabela_pedidos = $('#tabela_pedidos tbody').empty()
            const tabela_opcionais = $('#tabela_descontos_opcionais tbody').empty()
            let id_op = 1
            taxa_comercial_base = parseFloat(response['valores_padrao']['taxa_comercial'])
            comisao_base = parseFloat(response['valores_padrao']['comissao'])
            taxas_base = taxa_comercial_base + comisao_base
            valor_base = response['valor_base']
            let taxas = calcular_taxas()
            valores_descontos = response['pedidos']
            valores_op = response['opcionais']
            valor_atual = valor_base + taxas
            outros = response['outros']
            $('#comentario_pedido').text('OBS do colaborador: ' + response['observacoes'])
            $('#valores #valor_tratativa').text(convert_money(response['valor_com_desconto']))
            $('#valores #valor_atual').text(convert_money(valor_atual))
            $('#id_orcamento').val(response['id_orcamento'])

            for (let pedido of response['pedidos']) {
                let valor_formatado, valor_padrao

                if (pedido['campo'] == 'taxa_comercial' || pedido['campo'] == 'comissao') {
                    if (pedido['campo'] == 'comissao') {
                        comissao = pedido['valor_tratativa']
                    } else {
                        taxa_comercial = pedido['valor_tratativa']
                    }

                    valor_formatado = pedido['valor_tratativa'].toLocaleString() + '%'
                    valor_padrao = pedido['valor_padrao'].toLocaleString() + '%'
                }

                if (pedido['campo'] == 'desconto_geral') {
                    valor_formatado = convert_money(pedido['valor_tratativa'])
                    valor_padrao = convert_money(pedido['valor_padrao'])
                    desconto = pedido['valor_tratativa']
                }

                if (pedido['campo'] == 'data_pagamento') {
                    valor_formatado = pedido['valor_tratativa']
                    valor_padrao = pedido['valor_padrao']
                }

                if (pedido['campo'] == 'minimo_onibus') {
                    valor_formatado = parseInt(pedido['valor_tratativa'])
                    valor_padrao = parseInt(pedido['valor_padrao'])
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
                        <td>${id_op}</td>
                        <td>${op['nome']}</td>                    
                        <td><nobr>${convert_money(op['valor'])}</nobr></td>
                        <td>${op['descricao']}</td>
                        <td><input type="checkbox" onchange="calcular_aceites(this)" class="check" id="${op['id']}" name="opcional_${op['id']}"></td>                    
                    </tr>
                `)

                id_op++
            }
        }
    }).done((response) => {
        end_loading()
        $('#permissao_orcamentos').modal('show')
        if (!taxa_comercial) {
            taxa_comercial = response['valores_padrao']['taxa_comercial']
        }

        if (!comissao) {
            comissao = ['valores_padrao']['comissao']
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
    const lista_aceites = $('#tabela_pedidos .check, #tabela_descontos_opcionais .check')
    const linhaAceite = $(aceite).closest('tr')
    const idTabelaPai = linhaAceite.closest('table').attr('id')
    opcionais_aplicados = 0

    if (!$(aceite).prop('checked')) {
        $(`#${idTabelaPai} .select-all`).prop('checked', false)
    }

    for (let aceite of lista_aceites) {
        let nome = aceite.id

        if (nome === 'comissao') {
            comissao_aplicada = !!$(aceite).prop('checked');
        }

        if (nome === 'taxa_comercial') {
            taxa_aplicada = !!$(aceite).prop('checked');
        }

        if (valores_op) {
            for (let objeto of valores_op) {
                if (nome == objeto['id']) {
                    if ($(aceite).prop('checked')) {
                        opcionais_aplicados += objeto['valor']
                    }
                }
            }
        }
    }

    if ($('#desconto_geral').prop('checked')) {
        desconto_aplicado = desconto
    } else {
        desconto_aplicado = 0
    }

    novas_taxas = calcular_taxas()
    valor_atual = (valor_base + opcionais_aplicados - desconto_aplicado) + novas_taxas
    $('#valores #valor_atual').text(convert_money(valor_atual))
}

function calcular_taxas() {
    let valor_comissao, valor_taxa

    if (comissao_aplicada && taxa_aplicada) {
        valor_comissao = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (comissao / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)
        valor_taxa = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (taxa_comercial / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)

        return valor_comissao + valor_taxa
    } else if (comissao_aplicada && !taxa_aplicada) {
        valor_comissao = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (comissao / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)
        valor_taxa = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (taxa_comercial_base / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)

        return valor_comissao + valor_taxa
    } else if (taxa_aplicada && !comissao_aplicada) {
        valor_comissao = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (comisao_base / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)
        valor_taxa = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (taxa_comercial / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)

        return valor_comissao + valor_taxa
    } else {
        valor_comissao = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (comisao_base / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)
        valor_taxa = ((valor_base + opcionais_aplicados - desconto_aplicado) / (1 - (taxa_comercial_base / 100))) - (valor_base + opcionais_aplicados - desconto_aplicado)

        return valor_comissao + valor_taxa
    }
}

function alterar_status(btn) {
    const id_orcamento = $(btn).closest('tr').attr('id').split('_')[1]
    const novo_status = $(btn).attr('id')
    let motivo_recusa = ''
    loading()

    if (novo_status === 'perdido') {
        motivo_recusa = $('#modal_orcamento_perdido #motivo_recusa').val()
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': id_orcamento, 'novo_status': novo_status, 'motivo_recusa': motivo_recusa},
    }).done((response) => {
        if (response['status'] === 'error') {
            alert(`Houve um erro durante a alteração de status do orçamento (${response['msg']}), por favor tente novamente mais tarde`)
        } else {
            setTimeout(() => {
                window.location.reload()
            }, 500)
        }
    }).catch((error) => {
        alert(error)
        end_loading()
    })
}