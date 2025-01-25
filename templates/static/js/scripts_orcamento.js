let resultado_ultima_consulta = {}
let valores_taxas = {}
let valores_taxas_padrao = {}
let op_extras = []
let mostrar_instrucao = true
let enviar, promocional, editando_pacote = false
const relacao_id_categoria = {
    'id_outros_opcionais': 'outros',
    'id_opcionais_eco': 'eco',
    'id_opcionais_ceu': 'ceu',
    'op_extras': 'extra'
}
const secoes = [
    'diaria',
    'periodo_viagem',
    'tipo_monitoria',
    'transporte',
    'opcionais',
    'opcionais_extras'
]
let opcionais_promocionais = []

async function inicializacao(check_in = undefined, check_out = undefined) {
    $('#id_cliente').select2()
    $('#id_tipos_de_pacote_elegivel').select2({
        dropdownParent: $("#dados_do_pacote .modal-content"),
        width: '100%'
    })
    $('select[name="opcionais"]').select2({
        width: '100%',
        minimumResultsForSearch: -1
    })
    $('#id_produto').on('change', function () {
        if (!$('#id_promocional').prop('checked')) {
            if ($(this).val() !== null && $(this).val() !== '') {
                $('.botoes button').prop('disabled', false);
            } else {
                $('.botoes button').prop('disabled', true);
            }
        }
    });
    $('#apelido_orcamento, #apelido_orcamento_2').val($('#id_apelido').val())
    $('select[name="opcionais"]').on('change', async () => {
        await enviar_op();
    });

    let hoje = new Date()

    if ($('#modal_descritivo #data_vencimento').val() == '') {
        $('#modal_descritivo #data_vencimento').val(moment(hoje).add(15, 'd').format('YYYY-MM-DD'))
    }
    promocional = $('#tipo_de_orcamento').val() == 'promocional'
    $('#data_viagem').inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas, moment())
        .on('apply.daterangepicker', function (ev, picker) {
            if ($('#so_ceu').prop('checked')) {
                const startDate = picker.startDate;
                const endDate = picker.endDate;

                // Verifica se a data inicial é diferente da data final
                if (!startDate.isSame(endDate, 'day')) {
                    // Ajusta para que a data final seja igual à inicial
                    picker.setStartDate(startDate); // Não altera o horário
                    picker.setEndDate(startDate.clone().hour(endDate.hour()).minute(endDate.minute()));

                    // Atualiza o input com o novo valor
                    $(this).val(
                        startDate.format('DD/MM/YYYY HH:mm') + ' - ' +
                        startDate.format('DD/MM/YYYY HH:mm')
                    );
                }
            }
        });
    $('#lista_de_periodos .periodos input').inicializarDateRange('DD/MM/YYYY', false)

    if (check_in && check_out) {
        $('#data_viagem').val(`${check_in} - ${check_out}`).inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
            .on('apply.daterangepicker', function (ev, picker) {
                if ($('#so_ceu').prop('checked')) {
                    const startDate = picker.startDate;
                    const endDate = picker.endDate;

                    // Verifica se a data inicial é diferente da data final
                    if (!startDate.isSame(endDate, 'day')) {
                        // Ajusta para que a data final seja igual à inicial
                        picker.setStartDate(startDate); // Não altera o horário
                        picker.setEndDate(startDate.clone().hour(endDate.hour()).minute(endDate.minute()));

                        // Atualiza o input com o novo valor
                        $(this).val(
                            startDate.format('DD/MM/YYYY HH:mm') + ' - ' +
                            startDate.format('DD/MM/YYYY HH:mm')
                        );
                    }
                }
            });
    }

    $('#valor_opcional, #desconto_geral, .opcionais [id*="desconto"], .opcionais [id*="acrescimo"]').mascaraDinheiro()
    $('#desconto_produto_real, #desconto_monitoria_real, #desconto_transporte_real').mascaraDinheiro()
    $('#desconto_transporte_percent, #desconto_produto_percent, #desconto_monitoria_percent').mask('00,00%', {reverse: true})
    $('#comissao, #taxa_comercial, #id_limite_desconto_geral').mask('00,00%', {reverse: true})


    jQuery('#orcamento').submit(function () {
        const dados = jQuery(this).serialize()
        const url = $(this).attr('action')

        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
            }
        });

        return false
    })

    $('select[name="opcionais"]').on("select2:select", async function (e) {
        const opcao = e.params.data;
        const opcionais = $('.opcionais').length
        const i = opcionais + 1

        let nome_id = relacao_id_categoria[$(this).attr('id')]
        // loading()

        try {
            $.ajax({
                type: 'GET',
                url: '/orcamento/pesquisar_op/',
                data: {'nome_id': nome_id, 'id': opcao['id']},
            }).then(async (response) => {
                await listar_op(response, opcao, i)
            }).done(async () => {
                $('#tabela_de_opcionais input').maskMoney({
                    prefix: 'R$ ',
                    thousands: '.',
                    decimal: ',',
                    allowZero: true,
                    affixesStay: false,
                })
                await enviar_form()
            })
        } catch (error) {
            alert(error)
        } finally {
            alterar_cor_op()
        }
    })

    $('select[name="opcionais"]').on("select2:unselect", async function (e) {
        // loading()
        const opcao = e.params.data;

        try {
            $(`#opcionais_${relacao_id_categoria[$(this).attr('id')]}_${opcao['id']}`).remove()
        } catch (error) {
            alert(error)
            // end_loading()
        } finally {
            // await atualizar_valores_op()
            await listar_op(null, opcao, null, '0,00', '0,00', true)
            await enviar_form()
            alterar_cor_op()
            // end_loading()
        }
    })

    $('select[name="opcionais"]').on("select2:unselecting", async function (e) {
        if (opcionais_promocionais.includes(parseInt(e.params.args.data.id))) {
            e.preventDefault()
        }
    })

    if ($('#data_vencimento').val() != '') {
        $('#btn_salvar_orcamento').prop('disabled', false)
    }

    inicializar_funcoes_periodo_viagem()
    inicializar_funcoes_periodos_promocional()
}

function inicializar_funcoes_periodo_viagem() {
    $('#data_viagem').on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY HH:mm') + ' - ' + picker.endDate.format('DD/MM/YYYY HH:mm')).trigger('change');
    });

    $('#data_viagem').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });
}

function inicializar_funcoes_periodos_promocional() {
    $('#lista_de_periodos .div_periodos_aplicaveis .periodos .periodos_aplicaveis').on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY')).trigger('change');
    })

    $('#lista_de_periodos .div_periodos_aplicaveis .periodos .periodos_aplicaveis').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });
}

async function verificar_alteracoes(div) {
    // loading()
    await verificar_pisos_e_tetos()
    await enviar_form()

    let mostrar_mensagem = $(`#${div.id} input`).toArray().some((input) => {
        let valor

        if ($(input).data('mask') != undefined) {
            valor = parseFloat($(input).val()).toFixed(2).replace('.', ',') + '%'
        } else {
            valor = $(input).val()
        }

        if (valor != $(input).data('valor_alterado') && !$(input).attr('id').includes('alterado') && $(input).attr('id') != 'valor_final') {
            return true
        }
    })
    // end_loading()
}

$('#modal_descritivo').on('hidden.bs.modal', function (e) {
    if (!$('#modal_descritivo #alteracoes_aviso').hasClass('none')) {
        $('#campos_alteraveis input').map((index, input) => {
            if (!$(input).attr('id').includes('alterado') && $(input).attr('id') != 'valor_final')
                $(input).val($(input).data('valor_alterado'))
        })

        let obs = $(`#campos_alteraveis input`).toArray().some((input) => {
            let valor

            if ($(input).data('mask') != undefined) {
                valor = parseFloat($(input).val()).toFixed(2).replace('.', ',') + '%'
            } else {
                valor = $(input).val()
            }

            if (!$(input).attr('id').includes('alterado') && $(input).attr('id') != 'valor_final' && $(input).data('valor_inicial') != $(input).data('valor_alterado')) {
                return true
            }
        })

        if (!obs) {
            $('#modal_descritivo #observacoes_gerencia').val('')
            $('#modal_descritivo #div_observacoes_gerencia').addClass('none')
        }

        $('#modal_descritivo #alteracoes_aviso').addClass('none')
    }
});

$.fn.mascaraDinheiro = function () {
    return $(this).maskMoney({
        prefix: 'R$ ',
        thousands: '.',
        decimal: ',',
        allowZero: true,
        affixesStay: false,
        allowNegative: false,
    })
}

$.fn.inicializarDateRange = function (format, time_picker, isInvalidDate, min_date) {
    if (!isInvalidDate) isInvalidDate = null
    if (!min_date) min_date = false

    return this.daterangepicker({
        "timePicker": time_picker,
        "timePicker24Hour": true,
        "timePickerIncrement": 30,
        "minDate": $('#id_promocional').prop('checked') ? false : min_date,
        "locale": {
            "format": format,
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
        "autoUpdateInput": false,
        "showCustomRangeLabel": false,
        "alwaysShowCalendars": true,
        "drops": "up",
        "isInvalidDate": isInvalidDate,
    })
}

function verificar_datas(date) {
    if ($('#id_promocional').prop('checked') || $('#id_orcamento_promocional').val() != '') {
        let periodos = $('#lista_de_periodos input').map(function () {
            let inicio = moment($(this).val().split(' - ')[0], 'DD/MM/YYYY')
            let final = moment($(this).val().split(' - ')[1], 'DD/MM/YYYY')

            return {'inicio': inicio, 'final': final.add(1, 'days')}
        }).get();

        return !periodos.some(function (periodo) {
            return date.isSameOrAfter(periodo.inicio) && date.isSameOrBefore(periodo.final);
        });
    }
}

async function listar_op(dados_op, opcao, i, desconto = '0,00', acrescimo = '0,00', removido = false) {
    if (removido) {
        $(`#tabela_de_opcionais tbody #opcionais_${opcao['id']}`).remove()

        return
    }

    const valor_selecao = formatar_dinheiro(dados_op['valor'])

    $('#tabela_de_opcionais tbody').append(`
        <tr id="opcionais_${opcao['id']}" class="opcionais">
            <th><input type="text" id="nome_opcionais_${i}" name="opcionais_${i}" value='${opcao['text']}' disabled></th>
            <input type="hidden" id="id_opcionais_${i}" name="opcionais_${i}" value="${opcao['id']}">                    
            <input type="hidden" id="valor_bd_opcionais_${i}" name="opcionais_${i}" value='${valor_selecao}' disabled>
            <th><input type="text" id="valor_opcionais_${i}" disabled name="opcionais_${i}" value='${valor_selecao}'></th>
            <th><input type="text" id="desconto_opcionais_${i}" data-limite_desconto="${valor_selecao}" name="opcionais_${i}" value="${desconto}" onchange="aplicar_desconto(this)"></th> 
            <th><input type="text" id="acrescimo_opcionais_${i}" name="opcionais_${i}" value="${acrescimo}" onchange="aplicar_desconto(this)"></th> 
        </tr>
    `)
}

async function listar_op_extras(opcao, i) {
    let opcional_extra = op_extras.filter((op, index) => {
        if (op['id'] === opcao['id']) {
            return op
        }
    })[0]

    $('#tabela_de_opcionais tbody').append(`
        <tr id="opcionais_extra_${opcional_extra['id']}" class="opcionais">
            <th><input type="text" id="nome_opcionais_extra_${i}" name="opcionais_extra_${i}" value="${opcional_extra['nome']}" disabled></th>
            <input type="hidden" id="id_opcionais_extra_${i}" name="opcionais_extra_${i}" value="${opcional_extra['id']}">
            <input type="hidden" id="valor_bd_opcionais_extra_${i}" name="opcionais_extra_${i}" value='${String(opcional_extra['valor']).replace('.', ',')}' disabled>                                 
            <th><input type="text" id="valor_opcionais_extra_${i}" disabled name="opcionais_extra_${i}" value="${String(opcional_extra['valor']).replace('.', ',')}"></th>
            <th><input type="text" id="desconto_opcionais_extra_${i}" name="opcionais_extra_${i}" value="0,00" disabled></th> 
            <th><input type="text" id="acrescimo_opcionais_extra_${i}" name="opcionais_extra_${i}" value="0,00" disabled></th>
        </tr>
    `)
}

function criar_linhas_tabela_valores(categorias) {
    const tabela_valores = $('#tabela_de_valores tbody').empty()
    tabela_valores.append(`<tr id="diaria"><td colspan="2">Diarias</td></tr>`)
    tabela_valores.append(`<tr id="periodo_viagem"><td colspan="2">Taxa fixa</td></tr>`)
    tabela_valores.append(`<tr id="tipo_monitoria"><td colspan="2">Monitoria</td></tr>`)
    tabela_valores.append(`<tr id="transporte"><td colspan="2">Transporte</td></tr>`)
    tabela_valores.append(`<tr id="opcionais"><td colspan="2">Opcionais</td></tr>`)
    tabela_valores.append(`<tr id="arredondamento"><td colspan="2">Arredondamento</td></tr>`)
}

function separar_atividades(opcionais) {
    let opts = []

    for (let opt of opcionais) {
        opts.push(opt)
    }

    return opts
}

function sumByCategory(items) {
    return items.reduce((acc, item) => {
        const {
            categoria,
            valor,
            valores,
            comissao_de_vendas,
            desconto,
            taxa_comercial,
            valor_com_desconto,
            valor_final,
            acrescimo
        } = item
        let categoria_lower = categoria.toLowerCase().replace(/[^a-z0-9]/g, '')

        if (!acc[categoria_lower]) {
            acc[categoria_lower] = {
                valor: 0,
                comissao_de_vendas: 0,
                desconto: 0,
                taxa_comercial: 0,
                valor_com_desconto: 0,
                valor_final: 0,
                acrescimo: 0,
                valores: []
            }
        }

        // Soma os campos individuais
        acc[categoria_lower].valor += valor
        acc[categoria_lower].comissao_de_vendas += comissao_de_vendas
        acc[categoria_lower].desconto += desconto
        acc[categoria_lower].taxa_comercial += taxa_comercial
        acc[categoria_lower].valor_com_desconto += valor_com_desconto
        acc[categoria_lower].acrescimo += acrescimo
        acc[categoria_lower].valor_final += valor_final

        // Soma os valores em cada posição do campo "valores"
        valores.forEach((v, i) => {
            if (!acc[categoria_lower].valores[i]) {
                acc[categoria_lower].valores[i] = 0
            }
            acc[categoria_lower].valores[i] += v
        })

        return acc;
    }, {})
}

function linhas_descritivo_opcionais(opcionais) {
    let i = 1
    var classe_ultima_linha = ''
    let id_linhas = {}

    opcionais.map((opt) => {
        // Remove todos os caracteres especiais, mantendo apenas letras e números
        let categoria = opt['categoria'].toLowerCase().replace(/[^a-z0-9]/g, '');

        // Verifica se a categoria já existe em id_linhas
        if (!id_linhas.hasOwnProperty(categoria)) {
            id_linhas[opt['categoria']] = categoria;
        }
    })

    for (let opt of opcionais) {
        let linhaEspecifica = $(`#tabela_de_valores #opcionais`);
        var classe_ultimo_valor = ''

        if (i == 1) {
            classe_ultima_linha = 'ultima_linha'
        }

        let novaLinha = `<tr id='opcionais_${i}' class='atividade_ou_opcional'>
            <td></td>
            <td>${opt['nome']}</td>
            <td><nobr>R$ ${formatar_dinheiro(opt['valor'])}</nobr></td>
            <td><nobr>${(opt['valor'] - opt['valor_com_desconto']) > 0
            ? '- R$' + formatar_dinheiro(opt['valor'] - opt['valor_com_desconto'])
            : 'R$ ' + formatar_dinheiro(opt['valor'] - opt['valor_com_desconto'])}
            </nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opt['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opt['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opt['acrescimo'])}</nobr></td>
            <td class="valor_final_tabela ${classe_ultima_linha}"><nobr>R$ ${formatar_dinheiro(opt['valor_final'])}</nobr></td>
        </tr>`
        linhaEspecifica.after(novaLinha)

        for (let valor_dia of opt['valores']) {
            $(`#tabela_de_valores #opcionais_${i}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
        }

        i++
    }
}

function tabela_descrito(valores, dias, taxa, opcionais, totais, racionais) {
    $('#tabela_de_valores .datas').remove()
    $('.tag_datas').prop('colspan', dias.length)
    let classe_datas = ''
    let categorias = {}

    for (let data of dias) {
        let dia

        if (data == dias[dias.length - 1]) {
            classe_datas = 'ultima_data'

        }

        if (data == dias[0]) {
            dia = moment(data + ' ' + $('#data_viagem').val().split(' - ')[0].split(' ')[1])
            $('#tabela_de_valores .cabecalho').append(`<th class="datas ${classe_datas}">${dia.format('DD/MM HH:mm')} (${racionais['check_in']})</th>`)
        } else if (data == dias[dias.length - 1]) {
            dia = moment(data + ' ' + $('#data_viagem').val().split(' - ')[1].split(' ')[1])
            $('#tabela_de_valores .cabecalho').append(`<th class="datas ${classe_datas}">${dia.format('DD/MM HH:mm')} (${racionais['check_out']})</th>`)
        } else {
            dia = moment(data)
            $('#tabela_de_valores .cabecalho').append(`<th class="datas ${classe_datas}">${dia.format('DD/MM')}</th>`)
        }
    }

    criar_linhas_tabela_valores(categorias)

    for (let secao of secoes) {
        $(`#tabela_de_valores #${secao}`).append(`
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['valor'])}</nobr></td>
            <td><nobr> ${(valores[secao]['valor'] - valores[secao]['valor_com_desconto']) > 0
            ? '- R$' + formatar_dinheiro(valores[secao]['valor'] - valores[secao]['valor_com_desconto'])
            : 'R$ ' + formatar_dinheiro(valores[secao]['valor'] - valores[secao]['valor_com_desconto'])}                 
            </nobr></td>            
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['acrescimo'])}</nobr></td>                             
            <td class="valor_final_tabela"><nobr>${formatar_dinheiro(valores[secao]['valor_final'])}</nobr></td>
        `)

        for (let valor_dia of valores[secao]['valores']) {
            $(`#tabela_de_valores #${secao}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
        }
    }

    linhas_descritivo_opcionais(opcionais)

    $('#tabela_de_valores tbody').append(`
        <tr id="totais">
            <td></td>
            <th>Total</th>
            <th><nobr>R$ ${formatar_dinheiro(totais['valor'])}</nobr></th>
            <th><nobr>
                ${(totais['valor'] - totais['valor_com_desconto']) > 0
        ? '- R$' + formatar_dinheiro(totais['valor'] - totais['valor_com_desconto'])
        : 'R$ ' + formatar_dinheiro(totais['valor'] - totais['valor_com_desconto'])}            
            </nobr></th>            
            <th><nobr>R$ ${formatar_dinheiro(totais['taxa_comercial'])}</nobr></th>            
            <th><nobr>R$ ${formatar_dinheiro(totais['comissao_de_vendas'])}</nobr></th>            
            <th><nobr>R$ ${formatar_dinheiro(totais['acrescimo'])}</nobr></th>            
            <th class="valor_final_tabela"><nobr>R$ ${formatar_dinheiro(totais['valor_final'])}</nobr></th>            
        </tr>
    `)

    for (let valor of totais['descricao_valores']) {
        $('#tabela_de_valores #totais').append(`<th><nobr>R$ ${formatar_dinheiro(valor)}</nobr></th>`)
    }

    $(`#tabela_de_valores #arredondamento`).append(`
        <td><nobr>R$ 0</nobr></td>
        <td><nobr>R$ 0</nobr></td>
        <td><nobr>R$ 0</nobr></td>
        <td><nobr>R$ 0</nobr></td>                 
        <td><nobr>R$ 0</nobr></td>                 
        <td class="valor_final_tabela"><nobr>${formatar_dinheiro(valores['total']['arredondamento'])}</nobr></td>
    `)

    for (let i = 0; i < dias.length; i++) {
        $(`#tabela_de_valores #arredondamento`).append('<td><nobr>R$ 0</nobr></td>')
    }
}

async function verificar_pisos_e_tetos() {
    $('#avisos_pisos_tetos').addClass('none')

    // $.ajax({
    //     url: url,
    //     headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
    //     type: "POST",
    //     dataType: 'JSON',
    //     data: {'id_tipo_pacote': $('#id_tipo_pacote')},
    //     success: function (response) {
    //
    //     }
    // })

    return await new Promise(async (resolve, reject) => {
        $('#campos_alteraveis input').map((index, campo) => {
            let valor, piso, teto

            if ($(campo).val() == '') {
                $(campo).val(0)
            }

            if ($(campo).attr('name') != 'desconto_geral') {
                if ($(campo).val().includes('%')) {
                    valor = $(campo).val().replace('%', '')
                    piso = $(campo).data('piso').replace('%', '')
                    teto = $(campo).data('teto').replace('%', '')
                } else if (!$(campo).val().includes('$')) {
                    valor = $(campo).val()
                    piso = $(campo).data('piso')
                    teto = $(campo).data('teto')
                }

                if (parseFloat(valor) < parseFloat(piso)) {
                    $(campo).val($(campo).data('piso'))
                    $('#avisos_pisos_tetos').text(`O valor mínimo para o campo "${$(campo).data('nome_taxa')}" é de ${piso}`).removeClass('none')
                }

                if (parseFloat(valor) > parseFloat(teto)) {
                    $(campo).val($(campo).data('teto'))
                    $('#avisos_pisos_tetos').text(`O valor máximo para o campo "${$(campo).data('nome_taxa')}" é de ${teto}`).removeClass('none')
                }
            }
        })

        await teto_desconto()

        resolve()
    })
}

async function soma_descontos_pacote() {
    const desconto_percent = (parseFloat($('#desconto_produto_percent').val().replace(',', '.').replace('%', ''))) / 100
    const desconto_real = parseFloat($('#desconto_produto_real').val().replace(',', '.'))
    const valor_diaria = resultado_ultima_consulta['data']['valores']['diaria']['valor']

    return desconto_real + (valor_diaria * desconto_percent)
}

async function teto_desconto() {
    return await new Promise(async (resolve, reject) => {
        $('#aviso_comentario_gerencia').addClass('none')
        let teto_percent

        if ($('#id_tipo_de_pacote').val() != '') {
            teto_percent = parseFloat($('#desconto_geral').data('teto')) / 100
        } else {
            teto_percent = Object.keys(resultado_ultima_consulta['limites_taxas']).filter(chave => chave.includes("desconto")).map(chave => resultado_ultima_consulta['limites_taxas'][chave])[0]
            teto_percent = teto_percent / 100
        }

        let descontos_pacote = await soma_descontos_pacote()
        const comissao_percent = parseFloat($('#comissao').val().replace(',', '.').replace('%', ''))
        const taxa_percent = parseFloat($('#taxa_comercial').val().replace(',', '.').replace('%', ''))
        const valor = resultado_ultima_consulta['data']['valores']['diaria']['valor']
        let valor_final = (valor - descontos_pacote) / (1 - ((parseFloat(comissao_percent) + parseFloat(taxa_percent)) / 100))
        const desconto = parseFloat($('#desconto_geral').val().replace(',', '.'))
        let desconto_permitido = (teto_percent * valor_final).toFixed(2);

        if (desconto > desconto_permitido) {
            $('#desconto_geral').val(formatar_dinheiro(desconto_permitido))
            $('#avisos_pisos_tetos').text(`O valor máximo para o campo "Desconto" é de R$ ${formatar_dinheiro(desconto_permitido)}`).removeClass('none')
        }

        if (parseInt($('#desconto_geral').val()) != 0) {
            $('#div_observacoes_gerencia').removeClass('none')
            $('.botoes button').prop('disabled', true)
            $('#aviso_comentario_gerencia').removeClass('none')
        } else {
            $('#div_observacoes_gerencia').addClass('none')
        }

        resolve()
    })
}

function verificar_cometario_gerencia(textarea) {
    const comentario = $(textarea).val()

    if (comentario.length > 10) {
        $('.botoes button').prop('disabled', false)
        $('#aviso_comentario_gerencia').addClass('none')
    } else {
        $('.botoes button').prop('disabled', true)
        $('#aviso_comentario_gerencia').removeClass('none')
    }
}

async function enviar_form(salvar = false, gerente_aprovando = false, id_orcamento = undefined) {
    if ($('#so_ceu').prop('checked') && $('#id_tipo_de_pacote').val() == '') {
        alert('Selecione o pacote só CEU que deseja')
        $('.botoes button').prop('disabled', true)
    } else {
        $('.botoes button').prop('disabled', false)
    }

    let url = '/orcamento/calculos/'

    if (salvar) {
        $('#id_cliente, #id_responsavel').prop('disabled', false)
        if (gerente_aprovando) {
            url = '/orcamento/orcamento_aprovado/' + id_orcamento + '/'
        } else {
            url = '/orcamento/salvar/'
        }
        if ($('#id_tratativa').val() != undefined && $('#id_tratativa').val() != '') {
            url = url + $('#id_tratativa').val() + '/'
        }
    }

    let dados_op, gerencia, opcionais_extra;
    const form = $('#orcamento');
    const orcamento = form.serializeObject();

    if (op_extras.length > 0) {
        opcionais_extra = op_extras
    }

    dados_op = $('#forms_valores_op').serializeObject();
    gerencia = $('#form_gerencia').serializeObject();

    try {
        const response = await new Promise(function (resolve, reject) {
            $.ajax({
                url: url,
                headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                type: "POST",
                dataType: 'JSON',
                data: {orcamento, dados_op, gerencia, opcionais_extra, 'salvar': salvar},
                success: function (response) {
                    if (!salvar) {
                        let valores = response['data']['valores']
                        const periodo = response['data']['periodo_viagem']['valor_final']
                        const diaria = valores['diaria']['valor_final']
                        const periodo_diaria = (periodo + diaria)
                        const periodo_diaria_formatado = formatar_dinheiro(periodo_diaria)

                        const valor_monitoria = valores['tipo_monitoria']['valor_final'];
                        const transporte = valores['transporte']['valor_final'];
                        const monitoria_transporte = (valor_monitoria + transporte);
                        const monitoria_transporte_formatado = formatar_dinheiro(monitoria_transporte)

                        const opcionais = valores['opcionais']['valor_final']
                        // const atividades = valores['opcionais_ecoturismo']['valor_final']
                        // const atividade_ceu = valores['opcionais_ceu']['valor_final']
                        const outros = valores['opcionais_extras']['valor_final']
                        const total = response['data']['total']['valor_final']
                        const opcionais_e_atividades_formatado = formatar_dinheiro(opcionais + outros)
                        const total_formatado = formatar_dinheiro(total)

                        // Alteração dos valores das seções
                        $('#container_periodo .parcial').text('R$ ' + periodo_diaria_formatado) // Periodo da viagem
                        $('#container_monitoria_transporte .parcial').text('R$ ' + monitoria_transporte_formatado) // Monitoria + transporte
                        $('#container_opcionais .parcial').text('R$ ' + opcionais_e_atividades_formatado) // Opcionais
                        $('#subtotal span').text('R$ ' + total_formatado) // Total
                        $('#modal_descritivo #valor_final').val('R$ ' + total_formatado)

                        tabela_descrito(Object.assign(
                                {},
                                valores,
                                response['data']),
                            response['data']['days'],
                            periodo,
                            response['data']['descricao_opcionais'],
                            response['data']['total'],
                            response['racionais']
                        )
                        resultado_ultima_consulta = response
                    }
                    resolve(response['promocionais']);
                },
                error: function (xht, status, error) {
                    alert(xht['responseJSON']['msg'])
                    reject(xht['responseJSON']['msg'])
                }
            });
        });

        let obs = $(`#campos_alteraveis input`).toArray().some((input) => {
            let valor

            if ($(input).data('mask') != undefined) {
                valor = parseFloat($(input).val()).toFixed(2).replace('.', ',') + '%'
            } else {
                valor = $(input).val()
            }

            if (!$(input).attr('id').includes('alterado') && $(input).attr('id') != 'valor_final' && $(input).val() != $(input).data('valor_inicial')) {
                return true
            }
        })

        if (!obs) {
            $('#campos_alteraveis input').map((index, input) => {
                if (!$(input).attr('id').includes('alterado') && $(input).attr('id') != 'valor_final')
                    $(input).val($(input).data('valor_inicial'))
            })

            $('#modal_descritivo #observacoes_gerencia').val('')
            $('#modal_descritivo #div_observacoes_gerencia').addClass('none')
        }

        if ($('#id_orcamento_promocional').val() != '') {
            // $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', true)
            $('#form_dados_pacote fieldset').prop('disabled', true)
            $('#id_tipos_de_pacote_elegivel').select2({
                disabled: 'readonly',
                width: '100%'
            })
        } else {
            if ($('#so_ceu').prop('checked')) {
                $('#campos_fixos #container_opcionais .bloqueado').addClass('none')
            } else {
                $('.bloqueado').addClass('none')
            }
            $('#form_dados_pacote fieldset').prop('disabled', false)
            $('#id_tipos_de_pacote_elegivel').select2({width: '100%'})
        }

        return response;
    } catch (error) {
        alert(error)

        throw error
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

async function gerar_responsaveis(cliente) {
    const id_cliente = cliente.value
    const responsaveis = $('#id_responsavel').children()
    $('#id_responsavel').val('')
    await liberar_periodo()

    if (id_cliente === '') {
        $('#id_responsavel').prop('disabled', true)
        $('#periodo_viagem, #subtotal').addClass('none')

        return
    }

    $.ajax({
        type: 'GET',
        url: '/orcamento/verificar_responsaveis/',
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

async function liberar_periodo(id_responsavel = null) {
    if (!id_responsavel) {
        if (promocional && $('#id_responsavel').val() !== '') {
            if ($('#orcamentos_promocionais').val() !== '') {
                $('#tabela_de_opcionais tbody').empty()
                await preencher_promocional($('#orcamentos_promocionais').val())
                $('#container_periodo, #subtotal').removeClass('none')
            } else {
                $('#container_periodo, #subtotal').addClass('none')
            }

            return
        }

        if ($('#id_promocional').prop('checked')) {
            $('#div_nome_promocional').removeClass('none')

            if ($.trim($('#id_nome_promocional').val()).length > 8) {
                $('#container_periodo').removeClass('none')
            } else {
                $('#container_periodo').addClass('none')
            }

        } else {
            $('#div_nome_promocional').addClass('none')
        }

        if ($('#id_responsavel').val() === '' && !$('#id_promocional').prop('checked')) {
            $('#container_periodo, #subtotal').addClass('none')
        }
    } else {
        if (id_responsavel !== '') {
            if (promocional) {
                if ($('#orcamentos_promocionais').val() !== '') {
                    $('#container_periodo, #subtotal').removeClass('none')
                } else {
                    $('#container_periodo, #subtotal').addClass('none')
                }
            } else {
                $('#container_periodo, #subtotal').removeClass('none')
            }
        } else {
            $('#container_periodo, #subtotal').addClass('none')
        }
    }
}

async function pegar_monitoria_valida() {
    let check_in = $('#data_viagem').val().split(' - ')[0]
    let select_monitoria = $('#id_tipo_monitoria')
    let monitoria_selecionada = parseInt(select_monitoria.val())

    $.ajax({
        type: 'GET',
        url: '/orcamento/pegar_monitoria_valida/',
        data: {'check_in': check_in},
        success: function (response) {
            select_monitoria.empty().append('<option></option>')
            for (let monitor of response['monitorias']) {
                select_monitoria.append(`<option ${$('#so_ceu') && monitor['sem'] ? 'selected' : ''} value="${monitor['id']}" ${monitor['id'] == monitoria_selecionada ? 'selected' : ''}>${monitor['nome']}</option>`)
            }
        },
        error: function (xhr, status, error) {
            alert(xhr.responseJSON.msg)
        }
    })
}

async function separar_produtos(periodo) {
    let check_in = $(periodo).val().split(' - ')[0]
    let check_out = $(periodo).val().split(' - ')[1]
    let data_check_in = moment(check_in, 'DD/MM/YYYY HH:mm')
    let data_check_out = moment(check_out, 'DD/MM/YYYY HH:mm')

    await new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/orcamento/validar_produtos/',
            data: {'check_in': check_in, 'check_out': check_out, 'so_ceu': $('#so_ceu').prop('checked')},
            success: function (response) {
                for (let produto of $('#id_produto option')) {
                    if (produto.value != '') {
                        if (response['ids_produtos'].includes(parseInt($(produto).val()))) {
                            $(produto).prop('disabled', false)
                        } else {
                            $(produto).prop('disabled', true)
                        }
                    }
                }

                if (!$('#so_ceu').prop('checked')) {
                    for (let tipo of $('#id_tipo_de_pacote option')) {
                        if (tipo.value != '') {
                            if (response['ids_tipo_de_pacote'].includes(parseInt($(tipo).val()))) {
                                $(tipo).prop('disabled', false)
                            } else {
                                $(tipo).prop('disabled', true)
                            }
                        }
                    }
                }
                resolve(response)
            }
        }).done(async () => {
            await pegar_monitoria_valida()
            $('#id_produto').prop('disabled', false)
            $('#subtotal').removeClass('none')
            if (!$('#so_ceu').prop('checked')) {
                $('#id_tipo_de_pacote').trigger('change')
            }
        }).catch((xht, status, error) => {
            alert(xht['responseJSON']['msg'])
            $('#id_produto').val('')
            $('#id_tipo_de_pacote').val('').trigger('change')
            $('#subtotal').addClass('none')

            reject(xht['responseJSON']['msg'])
        })
        verficar_validade_opcionais(check_in)
    })

    if (resultado_ultima_consulta['data'] != undefined) {
        let check_in = $('#data_viagem').val().split(' - ')[0]
        let check_out = $('#data_viagem').val().split(' - ')[1]
        let data_check_in = moment(check_in, 'DD/MM/YYYY HH:mm')
        let data_check_out = moment(check_out, 'DD/MM/YYYY HH:mm')

        if (moment(data_check_out).startOf('day').diff(moment(data_check_in).startOf('day'), 'days') + 1 != parseInt(resultado_ultima_consulta['data']['n_dias'])) {
            if (!$('#so_ceu').prop('checked')) {
                $('#id_produto').val('')
            }
            $('#id_tipo_de_pacote').val('')
            $('#container_periodo .parcial').removeClass('visivel')
            $('.div-flutuante').removeClass('visivel')
            await verificar_preenchimento()
        }
    }
}

async function alterar_valores_das_taxas(dados_taxas) {
    function formatarPorcentagem(valor, valorAtual) {
        return valor != null ? valor.toString().replace('.', ',') + '%' : valorAtual;
    }

    let taxa_negocial = $('#taxa_comercial')
    let comissao = $('#comissao')
    let desconto = $('#desconto_geral')

    taxa_negocial.val(formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.val())).data({
        'valor_default': formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.data('valor_default')),
        'valor_inicial': formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.data('valor_inicial')),
        'valor_alterado': formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.data('valor_alterado')),
        'teto': formatarPorcentagem(dados_taxas['taxa_negocial']['teto_taxa_negocial'], taxa_negocial.data('teto')),
        'piso': formatarPorcentagem(dados_taxas['taxa_negocial']['piso_taxa_negocial'], taxa_negocial.data('piso'))
    }).attr({
        'data-valor_default': formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.data('valor_default')),
        'data-valor_inicial': formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.data('valor_inicial')),
        'data-valor_alterado': formatarPorcentagem(dados_taxas['taxa_negocial']['padrao_taxa_negocial'], taxa_negocial.data('valor_alterado')),
        'data-teto': formatarPorcentagem(dados_taxas['taxa_negocial']['teto_taxa_negocial'], taxa_negocial.data('teto')),
        'data-piso': formatarPorcentagem(dados_taxas['taxa_negocial']['piso_taxa_negocial'], taxa_negocial.data('piso'))
    })

    comissao.val(formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.val())).data({
        'valor_default': formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.data('valor_default')),
        'valor_inicial': formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.data('valor_inicial')),
        'valor_alterado': formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.data('valor_alterado')),
        'teto': formatarPorcentagem(dados_taxas['comissao']['teto_comissao'], comissao.data('teto')),
        'piso': formatarPorcentagem(dados_taxas['comissao']['piso_comissao'], comissao.data('piso'))
    }).attr({
        'data-valor_default': formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.data('valor_default')),
        'data-valor_inicial': formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.data('valor_inicial')),
        'data-valor_alterado': formatarPorcentagem(dados_taxas['comissao']['padrao_comissao'], comissao.data('valor_alterado')),
        'data-teto': formatarPorcentagem(dados_taxas['comissao']['teto_comissao'], comissao.data('teto')),
        'data-piso': formatarPorcentagem(dados_taxas['comissao']['piso_comissao'], taxa_negocial.data('piso'))
    })

    desconto.data({
        'teto': dados_taxas['teto_desconto_geral']
    }).attr({
        'data-teto': dados_taxas['teto_desconto_geral']
    })
    valores_taxas = {}
}

async function verificar_pacotes_promocionais(editando = false) {
    // loading()

    const periodo = $('#data_viagem').val()
    const data_check_in = moment(periodo.split(' - ')[0], 'DD/MM/YYYY HH:mm')
    const data_check_out = moment(periodo.split(' - ')[1], 'DD/MM/YYYY HH:mm')
    const n_dias = moment(data_check_out).startOf('day').diff(moment(data_check_in).startOf('day'), 'days') + 1
    const id_tipo_de_pacote = $('#id_tipo_de_pacote').val()
    const promocional_selecionado = $('#id_orcamento_promocional').val()

    await new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/orcamento/verificar_pacotes_promocionais/',
            data: {
                'data_check_in': data_check_in.format('YYYY-MM-DD HH:mm'),
                'data_check_out': data_check_out.format('YYYY-MM-DD HH:mm'),
                'id_tipo_de_pacote': id_tipo_de_pacote,
                'n_dias': n_dias
            },
            success: async function (response) {
                if (!editando && $('#id_orcamento_promocional').val() != '') {
                    await alterar_valores_das_taxas(response['dados_taxas'])
                    valores_taxas = {}
                } else if ($('#id_promocional').prop('checked')) {
                    await alterar_valores_das_taxas(response['dados_taxas'])
                    valores_taxas = {}
                } else if (id_tipo_de_pacote == ''){
                    await alterar_valores_das_taxas(response['dados_taxas'])
                } else if ($('#id_orcamento_promocional').val() == '') {
                    valores_taxas = response['dados_taxas']
                }

                const promocionais = response['promocionais']
                const ids = promocionais.map(obj => obj.id)
                let select_promocionais = $('#id_orcamento_promocional')
                const id_promocional_selecionado = parseInt(select_promocionais.val())
                console.log(ids.includes(id_promocional_selecionado), ids, id_promocional_selecionado)
                if (response['dados_taxas']['so_ceu'] && $('#so_ceu').prop('checked')) {
                    await verificar_preenchimento()
                    await verificar_monitoria_transporte()
                }

                if (!$('#id_promocional').prop('checked')) {
                    if (promocionais.length == 0) {
                        select_promocionais.empty().append('<option></option>').trigger('change').prop('disabled', true)

                        return
                    } else if (ids.includes(parseInt(select_promocionais.val()))) {

                    } else {
                        if (editando_pacote) {
                            await resetar_forms()
                        }
                    }
                }

                select_promocionais.empty().append('<option></option>')

                for (let promocional of promocionais) {
                    $('#id_orcamento_promocional').append(
                        `<option value="${promocional['id']}" ${promocional['id'] == id_promocional_selecionado ? 'selected' : ''}>${promocional['nome']}</option>`
                    ).prop('disabled', false)
                }
            }
        }).done(async () => {
            resolve(true)
        }).catch((e) => {
            reject(e)
        })
    })
    // end_loading()
}

async function verificar_preenchimento() {
    const floatingBox = $('#floatingBox')
    $('.div-flutuante').removeClass('none')
    // await verificar_pacotes_promocionais()

    if ($('#id_orcamento_promocional').val() != '') {
        await verificar_horarios()
    }

    if (editando_pacote || ($('#data_viagem').val() != '' && ($('#id_produto').val() != null && $('#id_produto').val() != ''))) {
        editando_pacote = false

        try {
            if (!$('#data_viagem').data('programmatic')) {
                await enviar_form()
            } else {
                $('#data_viagem').data('programmatic', false)
            }

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
            $('#container_monitoria_transporte').addClass('none')

            alert(error)
        } finally {
            // if (!$('#so_ceu').prop('checked')) {
            $('#id_tipo_de_pacote').prop('disabled', false)
            // end_loading()
            // }
        }
    } else {
        $('#container_periodo .visivel, #subtotal span').text('R$ 0,00')
    }
}

async function verificar_monitoria_transporte() {
    if ($('#id_tipo_monitoria').val() !== '' && $('input[name="transporte"]:checked').val() != undefined) {
        // loading()

        try {
            await enviar_form()
            $('#container_monitoria_transporte .parcial').addClass('visivel')
            $('#container_opcionais, #finalizacao').removeClass('none')
        } catch (error) {
            $('#container_monitoria_transporte .parcial').removeClass('visivel')
            $('#container_opcionais, #finalizacao').addClass('none')

            alert(error)
        } finally {
            // end_loading()
        }
    } else {
        $('#container_opcionais, #finalizacao').addClass('none')
    }
}

async function enviar_op() {
    // loading()

    try {
        await enviar_form()
        $('#container_opcionais .parcial').addClass('visivel')
    } catch (error) {
        $('#container_opcionais .parcial').text('').removeClass('visivel')
        alert(error)
    } finally {
        // end_loading()
    }
}

function aplicar_desconto(desconto) {
    const posicao = $(desconto).prop('name').split('_')[1]
    const opcional = $(`#${$(desconto).prop('id').replace('desconto', 'valor').replace('acrescimo', 'valor')}`)
    const id_bd = $(desconto).prop('id').replace('desconto', 'valor_bd').replace('acrescimo', 'valor_bd')
    const valor_bd_opcional = parseFloat($(`#${id_bd}`).val().replace(',', '.'))
    const valor_opcional = parseFloat($(opcional).val().replace(',', '.'))
    const limite_desconto = parseFloat($(desconto).data()['limite_desconto'])
    let desconto_aplicado = parseFloat($(desconto).val().replace(',', '.'))
    let novo_valor

    if (!$(desconto).prop('id').includes('acrescimo')) {
        if (desconto_aplicado > limite_desconto) {
            desconto_aplicado = limite_desconto
            $(desconto).val(limite_desconto.toFixed(2).replace('.', ','))
        }
    }

    if ($(desconto).prop('id').includes('acrescimo')) {
        novo_valor = valor_bd_opcional + desconto_aplicado
    } else {
        novo_valor = valor_bd_opcional - desconto_aplicado
    }
    opcional.val(`${novo_valor.toFixed(2).replace('.', ',')}`)
}

async function adicionar_novo_op() {
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
    let id_op_extra = `OPCEXT${n_op.toString().padStart(2, '0')}`
    await novo_op_extra(id_op_extra, nome_opcional, valor_opcional, descricao_opcional)
    $('#adicionar_opcional').modal('hide')
    $('#container_opcionais .parcial').addClass('visivel')
}

async function novo_op_extra(id_op_extra, nome_opcional, valor_opcional, descricao_opcional, editando = false) {
    // loading()
    op_extras.push({
        'id': id_op_extra,
        'nome': nome_opcional,
        'valor': valor_opcional,
        'descricao': descricao_opcional,
    })
    const opcionais = $('.opcionais').length
    const i = opcionais + 1

    if (!editando) {
        await listar_op_extras({'id': id_op_extra}, i)
    }

    let dados_novo_opcional = `
        <div id="${id_op_extra}" class="opcional_extra">
            <input type="text" onfocusin="$('.botoes button').prop('disabled', true)" onfocusout="$('.botoes button').prop('disabled', false)" onchange="editar_opcional_extra(this.parentElement, this)" title="${nome_opcional}" id="nome_op_extra" name="nome_op_extra" value="${nome_opcional}">
            <input type="text" onfocusin="$('.botoes button').prop('disabled', true)" onfocusout="$('.botoes button').prop('disabled', false)" onchange="editar_opcional_extra(this.parentElement, this)" title="${descricao_opcional}" id="descricao_op_extra" name="descricao_op_extra" value="${descricao_opcional}">
            <input type="text" onfocusin="$('.botoes button').prop('disabled', true)" onfocusout="$('.botoes button').prop('disabled', false)" onchange="editar_opcional_extra(this.parentElement, this)" id="valor_op_extra" name="valor_op_extra" class="valor_opcional_extra" value="${valor_opcional}">
            <button onclick="remover_opcional_extra('${id_op_extra}')">&times;</button>
            <hr style="width: 100%">
        </div>
    `
    $('#lista_opcionais_extra').append(dados_novo_opcional)
    $('.valor_opcional_extra').mascaraDinheiro()
    $('#legenda_opcionais_extra').removeClass('none')
    await enviar_form()
    // end_loading()
}

async function remover_opcional_extra(id_op_extra) {
    op_extras = op_extras.filter(function (opcional) {
        return opcional.id !== id_op_extra;
    })
    $(`#lista_opcionais_extra #${id_op_extra}`).remove()
    $(`#opcionais_extra_${id_op_extra}`).remove()
    await enviar_form()
}

async function atualizar_valores_op(carregar = false) {
    if (carregar) {
        // loading()
    }

    try {
        await enviar_form()
        $('#valores_outros_opcionais').modal('hide')
    } catch (error) {
        alert(error)
        $('#valores_outros_opcionais').modal('hide')
    } finally {
        if (carregar) {
            // end_loading()
        }
    }
}

async function enviar_infos_gerencia() {
    // loading()

    try {
        await enviar_form()
        $('#modal_gerencia').modal('hide')
    } catch (error) {
        alert(error)
        $('#modal_gerencia').modal('hide')
    } finally {
        // end_loading()
    }
}

async function salvar_orcamento(salvar_previa = false) {
    // loading()

    try {
        $('#salvar_previa').val(String(salvar_previa))
        await enviar_form(true)
        window.location.href = '/'
    } catch (error) {
        alert(error)
    } finally {
        // end_loading()
    }
}

function montar_pacote(check_promocional = null) {
    if (check_promocional) {
        if ($(check_promocional).prop('checked')) {
            $('#dados_do_pacote').modal('show')
            $('#id_cliente, #id_responsavel').attr('disabled', $('#id_promocional').prop('checked'))
            $('#promocionais').addClass('none')
            $('#data_viagem').inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
        } else {
            $('#promocionais').removeClass('none')
            $('#id_cliente').attr('disabled', $('#id_promocional').prop('checked'))
            $('#data_viagem').inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas, moment())
        }
    }
}

async function aprovar_orcamento() {
    $('#id_comentario_desconto').val('')
    $('#id_aprovacao_diretoria').val('False')
    await salvar_orcamento()
}

function mostrar_limite_cortesia(cortesia) {
    if ($(cortesia).prop('checked')) {
        $('#div_limite_cortesia').removeClass('none')
    } else {
        $('#div_limite_cortesia').addClass('none')
        $('#id_limite_cortesia').val('')
    }
}

function remover_periodo(btn) {
    let div_periodo = $(btn).parent().parent().remove()
    let periodos_restantes = $('.div_periodos_aplicaveis')
    let periodos = $('.periodos_aplicaveis')
    let dias, checks_dias

    for (let i = 1; i <= periodos_restantes.length; i++) {
        $(periodos[i - 1]).attr('name', `periodo_${i}`).attr('id', `periodo_${i}`)
        dias = $(periodos_restantes[i - 1]).find('.dias')
        $(dias).find('input').attr('name', `dias_periodo_${i}`).attr('id', `dias_periodo_${i}`)

    }
}

function adicionar_periodo_novo(periodo = '', diasMarcados = [], check_ins = [], check_outs = []) {
    let periodo_n = $('#lista_de_periodos .periodos_aplicaveis').length + 1

    let novo_obj_periodo = `
        <div class="mt-3 div_periodos_aplicaveis">
            <div class="periodos">
                <input type="text" id="periodo_${periodo_n}" value="${periodo}" name="periodo_${periodo_n}" class="periodos_aplicaveis">
                <button type="button" class="btn_remover_periodo" onclick="remover_periodo(this)"><span>&times;</span></button>
            </div>
            <div class="dias mt-2">
                <div>
                    <input id="input_seg" type="checkbox" name="dias_periodo_${periodo_n}" value="0" ${diasMarcados.includes(0) ? 'checked' : ''}>
                    <label for="input_seg">Seg</label>
                </div>
                <div>
                    <input id="input_ter" type="checkbox" name="dias_periodo_${periodo_n}" value="1" ${diasMarcados.includes(1) ? 'checked' : ''}>
                    <label for="input_ter">Ter</label>
                </div>
                <div>
                    <input id="input_qua" type="checkbox" name="dias_periodo_${periodo_n}" value="2" ${diasMarcados.includes(2) ? 'checked' : ''}>
                    <label for="input_qua">Qua</label>
                </div>
                <div>
                    <input id="input_qui" type="checkbox" name="dias_periodo_${periodo_n}" value="3" ${diasMarcados.includes(3) ? 'checked' : ''}>
                    <label for="input_qui">Qui</label>
                </div>
                <div>
                    <input id="input_sex" type="checkbox" name="dias_periodo_${periodo_n}" value="4" ${diasMarcados.includes(4) ? 'checked' : ''}>
                    <label for="input_sex">Sex</label>
                </div>
                <div>
                    <input id="input_sab" type="checkbox" name="dias_periodo_${periodo_n}" value="5" ${diasMarcados.includes(5) ? 'checked' : ''}>
                    <label for="input_sab">Sab</label>
                </div>
                <div>
                    <input id="input_dom" type="checkbox" name="dias_periodo_${periodo_n}" value="6" ${diasMarcados.includes(6) ? 'checked' : ''}>
                    <label for="input_dom">Dom</label>
                </div>                
            </div>
            <div id="horas_permitidas" class="mt-2">
                <div id="check_in" >
                    <label>Periodo de check in</label>
                    <div>
                        <input type="time" name="check_in_permitido_${periodo_n}" value="${check_ins[0]}">
                        a
                        <input type="time" name="check_in_permitido_${periodo_n}" value="${check_ins[1]}">
                    </div>
                </div>
                <div id="check_out" class="mt-2">
                    <label>Periodo de check out</label>
                    <div>
                        <input type="time" name="check_out_permitido_${periodo_n}" value="${check_outs[0]}">
                        a
                        <input type="time" name="check_out_permitido_${periodo_n}" value="${check_outs[1]}">
                    </div>
                </div>
            </div>
            <hr style="width: 100%">
        </div>`
    $('#lista_de_periodos').append(novo_obj_periodo)
    $(`#periodo_${periodo_n}`).inicializarDateRange('DD/MM/YYYY', false)

    inicializar_funcoes_periodos_promocional()
}

function salvar_dados_do_pacote() {
    // loading()
    const dados_pacote = $('#form_dados_pacote').serializeObject()

    $.ajax({
        type: 'POST',
        url: '/orcamento/salvar_pacote/',
        data: dados_pacote,
        success: function (response) {
            $('#id_pacote, #id_pacote_promocional').val(response['id_pacote'])
            let periodo = $('#data_viagem').data('daterangepicker')
            periodo.setStartDate(response['data_inicial'])
            periodo.setEndDate(response['data_final'])
            $('#data_viagem').val(periodo.startDate.format('DD/MM/YYYY HH:mm') + ' - ' + periodo.endDate.format('DD/MM/YYYY HH:mm')).trigger('change');
            $('#id_tipo_de_pacote').val($('#id_tipos_de_pacote_elegivel').val())
            $('#id_tipo_de_pacote').prop('disabled', false).trigger('change')
            // inicializar_funcoes_periodo_viagem()
        },
        error: function (xhr, status, error) {
            alert(xhr.responseJSON.msg)
        }
    }).done(async () => {
        $('#dados_do_pacote').modal('hide')
        $('#container_monitoria_transporte, #container_periodo').removeClass('none')
        $('#subtotal').removeClass('none')
        await enviar_form()
        $('.div-flutuante, #container_periodo .parcial').addClass('visivel')
        $('#btn_dados_pacote').prop('disabled', false)
    })
    // end_loading()
}

async function preencher_op_extras(id_orcamento, editando = false) {
    $.ajax({
        type: 'GET',
        url: '/orcamento/preencher_op_extras/',
        data: {'id_orcamento_extras': id_orcamento},
        success: function (response) {
            if (response['opcionais_extra']) {
                for (let opt of response['opcionais_extra']) {
                    novo_op_extra(opt['id'], opt['nome'], opt['valor'], opt['descricao'], editando)
                }
            }
        }
    }).done(() => {
        $('#container_opcionais .parcial').addClass('visivel')
    })
}

function alterar_cor_op() {
    let opcionais = $('#opcionais select option')

    for (let op of opcionais) {
        let value = parseInt($(op).val())
        let title = $(op).text()

        setTimeout(() => {
            if (opcionais_promocionais.includes(value)) {
                $(`li[title="${title}"]`).addClass('op_bloqueado')
            } else {
                $(`li[title="${title}"]`).removeClass('op_bloqueado')
            }
        }, 100)
    }
}

async function preencher_promocional(id_promocional) {
    await new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/orcamento/preencher_orcamento_promocional/',
            data: {'id_promocional': id_promocional},
            success: async function (response) {
                $('#id_tipo_monitoria').val(response['monitoria'])
                $('#id_transporte input').map((index, transporte) => {
                    $(transporte).prop('checked', transporte.value === response['transporte'])
                })
                opcionais_promocionais = Object.values(response['opcionais']).flat()
                alterar_cor_op()

                for (let categoria of $('#opcionais select')) {
                    if (Object.keys(response['opcionais']).includes(categoria.id.split('_')[1])) {
                        for (let cat in response['opcionais']) {
                            if (cat == categoria.id.split('_')[1]) {
                                $(categoria).val(response['opcionais'][cat])
                            }
                        }
                    } else {
                        $(categoria).val('')
                    }
                    // $(`#opcionais_${categoria}`).val(response['opcionais'][categoria])
                }

                response['obj']['descricao_opcionais'].map((op, i) => {
                    if (op['categoria'] != 'extra') {
                        let dados_op = {'valor': op['valor']}
                        let opcional = {'id': op['id'], 'text': op['nome']}
                        let desconto = formatar_dinheiro(op['desconto'])
                        let acrescimo = formatar_dinheiro(op['acrescimo'])
                        listar_op(dados_op, opcional, i + 1, desconto, acrescimo)
                    }
                })

                if (response['opcionais_extra']) {
                    for (let opt of response['opcionais_extra']) {
                        await novo_op_extra(opt['id'], opt['nome'], opt['valor'], opt['descricao'])
                    }
                }

                for (let id_campo in response['gerencia']) {
                    if (id_campo == 'desconto_geral') {
                        $(`#form_gerencia #${id_campo}`).val(formatar_dinheiro(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).data('valor_inicial', formatar_dinheiro(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_inicial', formatar_dinheiro(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).data('valor_alterado', formatar_dinheiro(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_alterado', formatar_dinheiro(response['gerencia'][id_campo]))
                    }

                    if (id_campo == 'comissao' || id_campo == 'taxa_comercial') {
                        $(`#form_gerencia #${id_campo}`).val((response['gerencia'][id_campo].toFixed(2) + '%').replace('.', ','))
                        $(`#form_gerencia #${id_campo}`).data('valor_inicial', (response['gerencia'][id_campo].toFixed(2) + '%').replace('.', ','))
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_inicial', (response['gerencia'][id_campo].toFixed(2) + '%').replace('.', ','))
                        $(`#form_gerencia #${id_campo}`).data('valor_alterado', (response['gerencia'][id_campo].toFixed(2) + '%').replace('.', ','))
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_alterado', (response['gerencia'][id_campo].toFixed(2) + '%').replace('.', ','))
                    }

                    if (id_campo == 'minimo_onibus') {
                        $(`#form_gerencia #${id_campo}`).val(parseInt(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).data('valor_inicial', parseInt(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_inicial', parseInt(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).data('valor_alterado', parseInt(response['gerencia'][id_campo]))
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_alterado', parseInt(response['gerencia'][id_campo]))
                    }

                    if (id_campo == 'data_pagamento') {
                        $(`#form_gerencia #${id_campo}`).val(response['gerencia'][id_campo])
                        $(`#form_gerencia #${id_campo}`).data('valor_inicial', response['gerencia'][id_campo])
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_inicial', response['gerencia'][id_campo])
                        $(`#form_gerencia #${id_campo}`).data('valor_alterado', response['gerencia'][id_campo])
                        $(`#form_gerencia #${id_campo}`).attr('data-valor_alterado', response['gerencia'][id_campo])
                    }
                }

                $('#desconto_produto_percent').val(response['gerencia']['desconto_produto_percent'] + '%')
                $('#desconto_monitoria_percent').val(response['gerencia']['desconto_monitoria_percent'] + '%')
                $('#desconto_transporte_percent').val(response['gerencia']['desconto_transporte_percent'] + '%')
                $('#desconto_produto_real').val(response['gerencia']['desconto_produto_real'].toString().replace('.', ','))
                $('#desconto_monitoria_real').val(response['gerencia']['desconto_monitoria_real'].toString().replace('.', ','))
                $('#desconto_transporte_real').val(response['gerencia']['desconto_transporte_real'].toString().replace('.', ','))
                $('#data_vencimento').val(response['gerencia']['data_vencimento'])

                resolve(response)
            }
        }).done(() => {
            verificar_monitoria_transporte()
            $('select[name="opcionais"]').trigger('change')
            $('#tabela_de_opcionais input').maskMoney({
                prefix: 'R$ ',
                thousands: '.',
                decimal: ',',
                allowZero: true,
                affixesStay: false
            })
            $('.opcionais [id*="desconto"]').trigger('change')
            enviar_form()
        }).catch((xht, status, error) => {
            alert(xht['responseJSON']['msg'])
            reject(xht['responseJSON']['msg'])
        })
    })
}

async function resetar_forms() {
    // loading()

    await new Promise((resolve, reject) => {
        try {
            $('#info_promocional').prop('disabled', true)

            for (let input of $('#form_gerencia input')) {
                if ($(input).data('valor_default')) {
                    $(input).val($(input).data('valor_default'))
                }
            }

            if (!$('#so_ceu').prop('checked')) {
                $('.bloqueado').addClass('none')
            }
            $('#form_gerencia #div_financeiro input[id*=real]').val('0,00')
            $('#form_gerencia #div_financeiro [id*=percent]').val('0,00%')
            $('#modal_descritivo #data_vencimento').val(moment().add(15, 'd').format('YYYY-MM-DD'))
            $('#tabela_de_opcionais [id*=desconto]').val('0,00').trigger('change')
            let default_data_pagamento = $('#data_pagamento').data('valor_default')
            $('#data_pagamento').val(default_data_pagamento)

            resolve(true)
        } catch (e) {
            alert(e)
            reject(e)
        }
    })

    // end_loading()
}

async function mostrar_dados_pacote(pacote) {
    let id_pacote = pacote.value
    if (!$('#so_ceu').prop('checked')) {
        $('.bloqueado').addClass('none')
    }
    // $('#opcionais select').val('').trigger('change')

    if (id_pacote == '') {
        await alterar_valores_das_taxas(valores_taxas_padrao)
        opcionais_promocionais = []
        alterar_cor_op()

        if ($('#id_promocional').prop('checked')) {
            return
        }

        await resetar_forms()
        await enviar_form()
        $('#info_promocional').prop('disabled', true)

        return
    } else {
        $('#info_promocional').prop('disabled', false)
    }

    $.ajax({
        url: '/orcamento/pegar_dados_pacote/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "GET",
        data: {'id_pacote': id_pacote},
        success: async function (response) {
            const campos = response['dados_promocionais']['fields']
            const periodos = response['dados_promocionais']['fields']['periodos_aplicaveis']
            $('#lista_de_periodos').empty()

            for (let campo in campos) {
                if (typeof campos[campo] == 'boolean') {
                    $(`#id_${campo}`).prop('checked', Boolean(campos[campo])).trigger('change')
                } else {
                    $(`#id_${campo}`).val(campos[campo])
                }
            }

            for (let _p in periodos) {
                adicionar_periodo_novo(Object.values(periodos[_p])[0],
                    Object.values(periodos[_p])[1],
                    Object.values(periodos[_p])[2].split(' - '),
                    Object.values(periodos[_p])[3].split(' - ')
                )
            }

            $('#tabela_de_opcionais tbody, #lista_opcionais_extra').empty()
            op_extras = []
            await preencher_promocional(id_pacote)

            if (response['dados_promocionais']['fields']['monitoria_fechado']) {
                $('#campos_fixos #monitoria .bloqueado').removeClass('none')
            } else {
                $('#campos_fixos #monitoria .bloqueado').addClass('none')
            }

            if (response['dados_promocionais']['fields']['transporte_fechado']) {
                $('#campos_fixos #transporte .bloqueado').removeClass('none')
            } else {
                $('#campos_fixos #transporte .bloqueado').addClass('none')
            }

            if (response['dados_promocionais']['fields']['opcionais_fechado']) {
                $('#campos_fixos #container_opcionais .bloqueado').removeClass('none')
            } else {
                $('#campos_fixos #container_opcionais .bloqueado').addClass('none')
            }

            $('#form_dados_pacote fieldset').prop('disabled', true)
            $('#id_tipos_de_pacote_elegivel').select2({
                disabled: 'readonly',
                width: '100%'
            }).trigger('change')

            if (Object.keys(valores_taxas).length > 0) {
                await alterar_valores_das_taxas(valores_taxas)
            }

            await verificar_horarios()
        }
    }).done(() => {
        $('#dados_do_pacote').modal('show')
    })
}

function verificar_horarios() {
    const hora_check_in = moment($('#data_viagem').val().split(' - ')[0].split(' ')[1], 'HH:mm')
    const data_check_in = moment($('#data_viagem').val().split(' - ')[0].split(' ')[0], 'DD/MM/YYYY')
    const data_check_out = moment($('#data_viagem').val().split(' - ')[1].split(' ')[0], 'DD/MM/YYYY')
    const hora_check_out = moment($('#data_viagem').val().split(' - ')[1].split(' ')[1], 'HH:mm')
    let periodos_permitidos = $('#lista_de_periodos .periodos_aplicaveis')

    periodos_permitidos.each(async function (index, element) {
        let check_in_periodo = moment($(element).val().split(' - ')[0], 'DD/MM/YYYY');
        let check_out_periodo = moment($(element).val().split(' - ')[1], 'DD/MM/YYYY');

        if (data_check_in >= check_in_periodo && data_check_in <= check_out_periodo) {
            let hora_check_in_1 = moment($(`input[name=check_in_permitido_${index + 1}]`)[0].value, 'HH:mm')
            let hora_check_in_2 = moment($(`input[name=check_in_permitido_${index + 1}]`)[1].value, 'HH:mm')
            let hora_check_out_1 = moment($(`input[name=check_out_permitido_${index + 1}]`)[0].value, 'HH:mm')
            let hora_check_out_2 = moment($(`input[name=check_out_permitido_${index + 1}]`)[1].value, 'HH:mm')

            if (!(hora_check_in >= hora_check_in_1 && hora_check_in <= hora_check_in_2)) {
                var resp1 = confirm('Horário de check in do grupo fora do permitido para o pacote. Alterar data de check in para se enquadrar?')

                if (resp1) {
                    let check_in = `${data_check_in.format('DD/MM/YYYY')} ${hora_check_in_1.format('HH:mm')}`
                    let check_out = `${data_check_out.format('DD/MM/YYYY')} ${hora_check_out.format('HH:mm')}`
                    $('#data_viagem').val(`${check_in} - ${check_out}`).inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
                } else {
                    $('#id_orcamento_promocional').val('').trigger('change')
                }
            }

            if (!(hora_check_out >= hora_check_out_1 && hora_check_out <= hora_check_out_2)) {
                var resp2 = confirm('Horário de check out do grupo fora do permitido para o pacote. Alterar data de check out para se enquadrar?')

                if (resp2) {
                    let check_in = `${data_check_in.format('DD/MM/YYYY')} ${hora_check_in_1.format('HH:mm')}`
                    let check_out = `${data_check_out.format('DD/MM/YYYY')} ${hora_check_out_2.format('HH:mm')}`
                    $('#data_viagem').val(`${check_in} - ${check_out}`).inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
                } else {
                    $('#id_orcamento_promocional').val('').trigger('change')
                }
            }

            if (resp1 || resp2) {
                // loading()
                await enviar_form()
                // end_loading()
            }
        }

        inicializar_funcoes_periodo_viagem()
    })
}

try {
    document.getElementById("btnPrint").onclick = function () {
        printTable()
    }
} catch (e) {
}


function printTable() {
    var logo = document.getElementById('logo_peraltas').cloneNode(true)
    var style = document.getElementById('style_impressao').cloneNode(true)

    // Clona o conteúdo do formulário com o ID "form_gerencia"
    var formContentClone = document.getElementById("form_gerencia").cloneNode(true);

    // Clona a tabela para garantir que somente ela seja impressa
    var tableClone = document.getElementById("tabela_de_valores").cloneNode(true);

    // Cria um novo documento temporário para a impressão
    var printWindow = window.open('', '_blank');

    // Adiciona o cabeçalho à página de impressão
    var header = document.createElement('header');
    header.style.padding = '10px';
    header.style.display = 'flex';
    header.style.alignItems = 'center';

    // Adiciona os elementos ao cabeçalho
    header.appendChild(logo)
    header.appendChild(style)
    formContentClone.style.pointerEvents = 'none'

    // Adiciona o conteúdo do formulário clonado acima da tabela
    printWindow.document.body.appendChild(header);
    printWindow.document.body.appendChild(formContentClone);
    printWindow.document.body.appendChild(tableClone);

    var checkReady = setInterval(function () {
        if (printWindow.document.readyState === "complete") {
            clearInterval(checkReady);
            printWindow.print();
            printWindow.document.close();
            printWindow.close();
        }
    }, 50);
}

// async function verificar_gerencia() {
//     loading()
//     $('#server_error, #login_error').addClass('none').text('')
//     $('#id_gerente').val('')
//
//     $.ajax({
//         url: '/orcamento/verificar_gerencia/',
//         headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
//         type: "POST",
//         data: {'id_usuario': $('#usuario').val(), 'senha': $('#senha').val()},
//         success: async function (response) {
//             $('#id_gerente').val($('#usuario').val())
//
//             if ($('#campos_alteraveis #desconto_geral').data('valor_alterado') == '0,00') {
//                 $('#campos_alteraveis #valor_final').data('valor_inicial', $('#campos_alteraveis #valor_final').val())
//                 $('#campos_alteraveis #valor_final').attr('data-valor_inicial', $('#campos_alteraveis #valor_final').val())
//             }
//
//             await enviar_form()
//             $('#campos_alteraveis input').map((index, input) => {
//                 $(input).data('valor_alterado', $(input).val())
//                 $(input).attr('data-valor_alterado', $(input).val())
//             })
//
//             let obs = $(`#campos_alteraveis input`).toArray().some((input) => {
//                 let valor
//                 console.log(input)
//
//                 if ($(input).data('mask') != undefined) {
//                     valor = parseFloat($(input).val()).toFixed(2).replace('.', ',') + '%'
//                 } else {
//                     valor = $(input).val()
//                 }
//
//                 if (!$(input).attr('id').includes('alterado') && $(input).attr('id') != 'valor_final' && $(input).data('valor_inicial') != $(input).data('valor_alterado')) {
//                     return true
//                 }
//             })
//
//             if (!obs) {
//                 $('#modal_descritivo #observacoes_gerencia').val('')
//                 $('#modal_descritivo #div_observacoes_gerencia').addClass('none')
//             }
//
//             $('#verificacao_gerencia').modal('hide')
//             $('#alteracoes_aviso').addClass('none')
//         },
//         error: function (xht, status, error) {
//             if (xht.status == 500) {
//                 $('#server_error').removeClass('none').text(xht['responseJSON']['msg'])
//             }
//
//             if (xht.status == 401) {
//                 $('#login_error').removeClass('none').text(xht['responseJSON']['msg'])
//             }
//         }
//     })
//     end_loading()
//     $('#verificacao_gerencia #senha').val('')
// }

function atribuir_apelaido(input_apelido) {
    $('#id_apelido').val(input_apelido.value)
    if (input_apelido.value.length > 5) {
        $('#btn_salvar_apelido').prop('disabled', false)
    } else {
        $('#btn_salvar_apelido').prop('disabled', true)
    }
}

async function editar_opcional_extra(pai, elemento) {
    // loading()
    const id_pai = $(pai).attr('id')
    $(elemento).attr('title', $(elemento).val())

    op_extras.forEach((op) => {
        if (op['id'] == id_pai) {
            op['nome'] = $(`#${id_pai} #nome_op_extra`).val()
            op['descricao'] = $(`#${id_pai} #descricao_op_extra`).val()
            op['valor'] = $(`#${id_pai} #valor_op_extra`).val().replace('R$ ', '')
            $(`#opcionais_extra_${id_pai} input`).eq(0).val(op['nome'])
            $(`#opcionais_extra_${id_pai} input`).eq(3).val(op['valor'])
        }
    })

    if ($(elemento).attr('id') == 'valor_op_extra') {
        await enviar_form()
    }
    // end_loading()
}

function verficar_validade_opcionais(check_in) {
    $.ajax({
        url: '/orcamento/verificar_validade_op/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "GET",
        data: {'check_in': check_in},
        success: async function (response) {
            $('select[name="opcionais"]').each(function () {
                let select = $(this);

                select.find('option').each(function () {
                    let op = $(this);
                    let opValue = parseInt(op.val())

                    if (!response['id_opcionais'].includes(opValue)) {
                        $(op).addClass('none').prop('disabled', true)

                        if (op.is(':selected')) {
                            select.val(select.val().filter(value => value != op.val())).trigger('change');
                            select.trigger({
                                type: 'select2:unselect',
                                params: {
                                    data: {id: op.val()}
                                }
                            });
                        }
                    } else {
                        $(op).removeClass('none').prop('disabled', false)
                    }
                })
            })
            $('select[name="opcionais"]').select2({
                width: '100%',
                minimumResultsForSearch: -1
            })
        }
    })
}

async function salvar_comentario_diretoria() {
    if ($('#apelido_orcamento_2').val().length > 5 && $('#comentario_gerencia').val().length > 10) {
        $('#id_comentario_desconto').val($('#comentario_gerencia').val())
        $('#id_apelido').val($('#apelido_orcamento_2').val())
        $('#id_aprovacao_diretoria').val('True')
        $('#modal_cometario_diretoria').modal('hide')
        await salvar_orcamento(true)
    } else {
        $('#avisos_apelidos').removeClass('none')
        if ($('#apelido_orcamento_2').val().length < 5) {
            $('#aviso_apelido').removeClass('none')
        } else {
            $('#aviso_apelido').addClass('none')
        }
        if ($('#comentario_gerencia').val().length < 5) {
            $('#aviso_comentario').removeClass('none')
        } else {
            $('#aviso_comentario').addClass('none')
        }
    }
}

async function trocar_modalidade_desconto(btn) {
    const div_atual = $(btn).closest('div')
    const div_irmao = div_atual.siblings('div')
    const input_atual = div_atual.find('input');
    input_atual.val('0,00');
    $(div_atual).addClass('none')
    $(div_irmao).removeClass('none')
    await enviar_form()
}

async function modalidade_so_ceu(editando = false) {
    // loading()

    if (!editando) {
        $('#opcionais select').each(function () {
            const $select = $(this);
            // Remove todas as seleções manualmente sem disparar 'change'
            $select.val(null);
            console.log($select.val())
            // Dispara manualmente o evento 'select2:clear'
            $select.trigger('select2:clear');
        })

        $('#tabela_de_opcionais tbody').empty()
    }
    // $('#container_monitoria_transporte, #container_opcionais, #finalizacao').addClass('none')

    if ($('#so_ceu').prop('checked')) {
        $('#aviso_orcamento_so_ceu').removeClass('none')
        const picker = $('#data_viagem').data('daterangepicker');

        // Verifica se o picker está inicializado
        if ($('#data_viagem').val() == '') {
            // Define o dia atual com horários específicos
            const startDate = moment().add(1, 'days').startOf('day').hour(6);  // Hoje às 06:00
            const endDate = moment().add(1, 'days').startOf('day').hour(22);   // Hoje às 22:00

            // Define as datas no DateRangePicker
            picker.setStartDate(startDate);
            picker.setEndDate(endDate);
            // Opcional: Atualiza o valor do input manualmente (se necessário)
            $('#data_viagem').val(
                startDate.format('DD/MM/YYYY HH:mm') + ' - ' + endDate.format('DD/MM/YYYY HH:mm')
            );
        }
        const check_in = $('#data_viagem').val().split(' - ')[0]

        $.ajax({
            url: '/orcamento/verificar_dados_so_ceu/',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "GET",
            data: {'check_in': check_in},
            success: function (response) {
                for (let tipo of $('#id_tipo_de_pacote option')) {
                    if (tipo.value != '') {
                        if (response['id_pacotes_so_ceu'].includes(parseInt($(tipo).val()))) {
                            $(tipo).prop('disabled', false)
                        } else {
                            $(tipo).prop('disabled', true)
                        }
                    }
                }

                if (picker) {
                    const startDate = picker.startDate; // Data inicial
                    const endDate = picker.endDate;     // Data final

                    // Verifica se a data inicial é diferente da data final
                    if (!startDate.isSame(endDate, 'day')) {
                        // Ajusta a data final para ser igual à inicial (mantendo o horário)
                        picker.setStartDate(startDate); // Define nova data inicial
                        picker.setEndDate(startDate.clone().hour(endDate.hour()).minute(endDate.minute())); // Ajusta a data final

                        // Atualiza o campo de entrada com o novo valor
                        $('#data_viagem').val(
                            startDate.format('DD/MM/YYYY HH:mm') + ' - ' +
                            startDate.format('DD/MM/YYYY HH:mm')
                        )
                    }
                }

                $('#id_produto').val(response['id_produto'])
                $('#id_tipo_monitoria').val(response['id_monitoria'])
                $('#id_transporte_1').prop('checked', true)
            }
        }).done(async () => {
            $('#opcionais select.so_ceu').prop('disabled', false)
            $('#opcionais select:not(.so_ceu)').prop('disabled', true)
            $('#opcionais button').prop('disabled', true)
            $('#id_orcamento_promocional').prop('disabled', true)
            $('#id_tipo_de_pacote').prop('disabled', false)
            $('#id_produto').prop('disabled', false).addClass('pe-none')
            $('#id_orcamento_promocional').val('')
            $('#campos_fixos #monitoria .bloqueado').removeClass('none')
            $('#campos_fixos #transporte .bloqueado').removeClass('none')
            await separar_produtos($('#data_viagem'))

            if (!editando) {
                $('#container_monitoria_transporte, #container_opcionais, #finalizacao').addClass('none')
            }
        })
    } else {
        $('#opcionais select.so_ceu').prop('disabled', true)
        $('#opcionais select:not(.so_ceu)').prop('disabled', false)
        $('#opcionais button').prop('disabled', false)
        $('#id_tipo_monitoria').val('')
        $('#id_transporte_1').prop('checked', false)
        $('#aviso_orcamento_so_ceu').addClass('none')
        $('#id_produto').val('').trigger('change').removeClass('pe-none')
        $('#id_tipo_de_pacote').val('').prop('disabled', true)
        $('#campos_fixos #monitoria .bloqueado').addClass('none')
        $('#campos_fixos #transporte .bloqueado').addClass('none')
        $('#container_monitoria_transporte, #container_opcionais, #finalizacao').addClass('none')
        // await verificar_pacotes_promocionais()
        await enviar_form()
        await separar_produtos($('#data_viagem'))
    }
    // end_loading()
}