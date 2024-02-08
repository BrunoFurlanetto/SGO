let resultado_ultima_consulta = {}
let op_extras = []
let mostrar_instrucao = true
let enviar, promocional = false
const secoes = ['diaria', 'tipo_monitoria', 'transporte', 'opcionais', 'atividades', 'atividades_ceu', 'outros']

async function inicializacao(check_in = undefined, check_out = undefined) {
    $('#id_cliente').select2()
    $('#id_produtos_elegiveis').select2({
        dropdownParent: $("#dados_do_pacote .modal-content"),
        width: '100%'
    })

    let hoje = new Date()
    $('#data_pagamento, #modal_descritivo #data_vencimento').val(moment(hoje).add(15, 'd').format('YYYY-MM-DD'))
    $('#data_pagamento').data('valor_default', moment().add(15, 'd').format('YYYY-MM-DD'))
    promocional = $('#tipo_de_orcamento').val() == 'promocional'

    $('#data_viagem').inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
    $('#periodo_1').inicializarDateRange('DD/MM/YYYY', false)

    if (check_in && check_out) {
        $('#data_viagem').val(`${check_in} - ${check_out}`).inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
    }

    $('#valor_opcional').mascaraDinheiro()
    $('#desconto_geral').mascaraDinheiro()
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

    $("#id_opcionais, #op_extras, #id_atividades, #id_atividades_ceu").on("select2:select", async function (e) {
        const opcao = e.params.data;
        const opcionais = $('.opcionais').length
        const i = opcionais + 1
        let nome_id = $(this).attr('id')
        loading()

        try {
            if (nome_id !== 'op_extras') {
                $.ajax({
                    type: 'GET',
                    url: '',
                    data: {'nome_id': nome_id, 'id': opcao['id']},
                }).then(async (response) => {
                    await listar_op(response, nome_id, opcao, i)
                }).done(async () => {
                    $('#tabela_de_opcionais input').maskMoney({
                        prefix: 'R$ ',
                        thousands: '.',
                        decimal: ',',
                        allowZero: true,
                        affixesStay: false
                    })
                    await enviar_form()
                })
            } else {
                await listar_op_extras(opcao, i)
                await enviar_form()
            }
        } catch (error) {
            alert(error)
        } finally {
            // await atualizar_valores_op()
            end_loading()
        }
    })

    $("#id_opcionais, #op_extras, #id_atividades, #id_atividades_ceu").on("select2:unselect", async function (e) {
        loading()

        try {
            const opcao = e.params.data;
            $(`#op_${opcao['id']}`).remove()
        } catch (error) {
            alert(error)
            end_loading()
        } finally {
            // await atualizar_valores_op()
            await enviar_form()
            end_loading()
        }
    })

    if ($('#data_vencimento').val() != '') {
        $('#btn_salvar_orcamento').prop('disabled', false)
    }
}

function verificar_produto() {
    const produto = $('#id_produto option:selected').text().toLowerCase()

    if (produto.includes('ceu')) {
        $('#form_gerencia fieldset, #btn_alterar_taxas, #id_atividades, #id_opcionais').prop('disabled', true)
    } else {
        $('#form_gerencia fieldset, #btn_alterar_taxas, #id_atividades, #id_opcionais').prop('disabled', false)
    }
}

async function verificar_alteracoes(div) {
    if ($('#id_promocional').prop('checked')) {
        await enviar_form()

        return
    }

    setInterval(() => {
        $('#btn_salvar_orcamento').prop('disabled', !$('#div_observacoes_gerencia').hasClass('none') && $('#observacoes_gerencia').val().length < 10)
    }, 10)

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

    if (mostrar_mensagem) {
        $('#alteracoes_aviso').removeClass('none')
    } else {
        $('#alteracoes_aviso').addClass('none')
    }

    if (mostrar_mensagem) {
        $('#div_observacoes_gerencia').removeClass('none')
        $('#observacoes_gerencia').prop('required', true)
        // $('#btn_salvar_orcamento').prop('disabled', true)
        $('.botoes').attr('title', 'Verificar observações para a gerência')
    } else {
        $('#div_observacoes_gerencia').addClass('none')
        $('#observacoes_gerencia').val('').prop('required', false)
        $('#btn_salvar_orcamento').prop('disabled', false)
        $('.botoes').attr('title', '')
    }
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
        affixesStay: false
    })
}

$.fn.inicializarDateRange = function (format, time_picker, isInvalidDate, show_initial_date, ranges) {
    if (!isInvalidDate) isInvalidDate = null
    if (!show_initial_date) show_initial_date = true
    if (!ranges) ranges = ''
    return this.daterangepicker({
        "timePicker": time_picker,
        "timePicker24Hour": true,
        "timePickerIncrement": 30,
        "minDate": moment(),
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

async function listar_op(dados_op, nome_id, opcao, i, desconto = '0,00') {
    const valor_selecao = formatar_dinheiro(dados_op['valor'])

    if (nome_id == 'id_atividades') {
        $('#tabela_de_opcionais tbody').append(`
            <tr id="atividade_${opcao['id']}" class="opcionais">
                <th><input type="text" id="atividade_peraltas_${i}" name="atividade_peraltas_${i}" value='${opcao['text']}' disabled></th>
                <input type="hidden" id="id_atividade_peraltas_${i}" name="atividade_peraltas_${i}" value="${opcao['id']}">                    
                <input type="hidden" id="valor_bd_atividade_peraltas_${i}" name="atividade_peraltas_${i}" value='${valor_selecao}' disabled>
                <th><input type="text" id="valor_atividade_peraltas_${i}" disabled name="atividade_peraltas_${i}" value='${valor_selecao}'></th>
                <th><input type="text" id="desconto_atividade_peraltas_${i}" data-limite_desconto="${valor_selecao}" name="atividade_peraltas_${i}" value="${desconto}" onchange="aplicar_desconto(this)"></th> 
            </tr>
        `)
    } else if (nome_id == 'id_atividades_ceu') {
        $('#tabela_de_opcionais tbody').append(`
            <tr id="atividade_ceu_${opcao['id']}" class="opcionais">
                <th><input type="text" id="atividade_ceu_${i}" name="atividade_ceu_${i}" value='${opcao['text']}' disabled></th>
                <input type="hidden" id="id_atividade_ceu_${i}" name="atividade_ceu_${i}" value="${opcao['id']}">                    
                <input type="hidden" id="valor_bd_atividade_ceu_${i}" name="atividade_ceu_${i}" value='${valor_selecao}' disabled>
                <th><input type="text" id="valor_atividade_ceu_${i}" disabled name="atividade_ceu_${i}" value='${valor_selecao}'></th>
                <th><input type="text" id="desconto_atividade_ceu_${i}" name="atividade_ceu_${i}" value="${desconto}" disabled></th> 
            </tr>
        `)
    } else {
        $('#tabela_de_opcionais tbody').append(`
            <tr id="op_${opcao['id']}" class="opcionais">
                <th><input type="text" id="opcional_${i}" name="opcional_${i}" value="${opcao['text']}" disabled></th>
                <input type="hidden" id="id_opcional_${i}" name="opcional_${i}" value="${opcao['id']}">                    
                <input type="hidden" id="valor_bd_opcional_${i}" name="opcional_${i}" value='${valor_selecao}' disabled>
                <th><input type="text" id="valor_opcional_${i}" disabled name="opcional_${i}" value='${valor_selecao}'></th>
                <th><input type="text" id="desconto_opcional_${i}" name="opcional_${i}" data-limite_desconto="${valor_selecao}" value="${desconto}" onchange="aplicar_desconto(this)"></th> 
            </tr>
        `)
    }
}

async function listar_op_extras(opcao, i) {
    let opcional_extra = op_extras.filter((op, index) => {
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

function tabela_descrito(valores, dias, taxa, opcionais, totais) {
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
            <td class="valor_final_tabela"><nobr>${formatar_dinheiro(secao == 'diaria' ? valores[secao]['valor_final'] + taxa : valores[secao]['valor_final'])}</nobr></td>
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

async function enviar_form(salvar = false) {
    if ($('#id_orcamento_promocional').val() != '') {
        $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', false)
    }

    if (salvar) {
        $('#id_cliente, #id_responsavel').prop('disabled', false)
    }

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

    dados_op = $('#forms_valores_op').serializeObject();
    gerencia = $('#form_gerencia').serializeObject();

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
                        const periodo = response['data']['periodo_viagem']['valor_final']
                        const diaria = valores['diaria']['valor_final']
                        const periodo_diaria = (periodo + diaria)
                        const periodo_diaria_formatado = formatar_dinheiro(periodo_diaria)

                        const valor_monitoria = valores['tipo_monitoria']['valor_final'];
                        const transporte = valores['transporte']['valor_final'];
                        const monitoria_transporte = (valor_monitoria + transporte);
                        const monitoria_transporte_formatado = formatar_dinheiro(monitoria_transporte)

                        const opcionais = valores['opcionais']['valor_final']
                        const atividades = valores['atividades']['valor_final']
                        const atividade_ceu = valores['atividades_ceu']['valor_final']
                        const outros = valores['outros']['valor_final']
                        const total = response['data']['total']['valor_final']
                        const opcionais_e_atividades_formatado = formatar_dinheiro(opcionais + outros + atividades + atividade_ceu)
                        const total_formatado = formatar_dinheiro(total)
                        console.log(total_formatado, total)
                        // Alteração dos valores das seções
                        $('#container_periodo .parcial').text('R$ ' + periodo_diaria_formatado); // Periodo da viagem
                        $('#container_monitoria_transporte .parcial').text('R$ ' + monitoria_transporte_formatado); // Monitoria + transporte
                        $('#container_opcionais .parcial').text('R$ ' + opcionais_e_atividades_formatado); // Opcionais
                        $('#subtotal span').text('R$ ' + total_formatado) // Total
                        $('#modal_descritivo #valor_final').val('R$ ' + total_formatado)

                        tabela_descrito(valores, response['data']['days'], periodo, response['data']['descricao_opcionais'], response['data']['total'])
                        resultado_ultima_consulta = response
                    }
                    resolve(response['promocionais']);
                },
                error: function (xht, status, error) {
                    reject(xht['responseJSON']['msg']);
                }
            });
        });

        if (!salvar) {
            if (response.length > 0) {
                let pacote_selecionado = $('#id_orcamento_promocional').val()
                $('#id_orcamento_promocional').empty().append('<option></option>')

                for (let promocional of response) {
                    $('#id_orcamento_promocional').append(
                        `<option value="${promocional['id']}">${promocional['nome']}</option>`
                    ).prop('disabled', false)
                }
                $('#id_orcamento_promocional').val(pacote_selecionado)
            } else {
                $('#id_orcamento_promocional').prop('disabled', true)
            }
        }

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
            $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', true)
            $('#form_dados_pacote fieldset').prop('disabled', true)
            $('#id_produtos_elegiveis').select2({
                disabled: 'readonly',
                width: '100%'
            })
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

async function separar_produtos(periodo) {
    let check_in = $(periodo).val().split(' - ')[0]
    let check_out = $(periodo).val().split(' - ')[1]

    await new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '',
            data: {'check_in': check_in, 'check_out': check_out},
            success: function (response) {
                for (let produto of $('#id_produto option')) {
                    if (produto.value != '') {
                        if (response['ids'].includes(parseInt($(produto).val()))) {
                            $(produto).prop('disabled', false)
                        } else {
                            $(produto).prop('disabled', true)
                        }
                    }
                }

                resolve(response)
            }
        }).done(() => {
            $('#id_produto').prop('disabled', false)
            $('#subtotal').removeClass('none')
        }).catch((xht, status, error) => {
            alert(xht['responseJSON']['msg'])
            $('#id_produto').val('')
            $('#subtotal').addClass('none')

            reject(xht['responseJSON']['msg'])
        })
    })

    setTimeout(() => {
        if ($('#id_produto').val() == null) {
            $('#id_produto').val('')
        }
    }, 1)
}

async function verificar_preenchimento(editando = false) {
    const floatingBox = $('#floatingBox')
    $('.div-flutuante').removeClass('none')
    await separar_produtos($('#data_viagem'))

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
            $('#container_monitoria_transporte').addClass('none')

            alert(error)
        } finally {
            const check_in = moment($('#data_viagem').val().split(' - ')[0], 'DD/MM/YYYY HH:mm')
            end_loading()
        }
    } else {
        $('#container_periodo .visivel, #subtotal span').text('R$ 0,00')
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
    const opcional = $(`#${$(desconto).prop('id').replace('desconto', 'valor')}`)
    const id_bd = $(desconto).prop('id').replace('desconto', 'valor_bd')
    const valor_bd_opcional = parseFloat($(`#${id_bd}`).val().replace(',', '.'))
    const valor_opcional = parseFloat($(opcional).val().replace(',', '.'))
    const limite_desconto = parseFloat($(desconto).data()['limite_desconto'])
    let desconto_aplicado = parseFloat($(desconto).val().replace(',', '.'))

    if (desconto_aplicado > limite_desconto) {
        desconto_aplicado = limite_desconto
        $(desconto).val(limite_desconto.toFixed(2).replace('.', ','))
    }

    const novo_valor = valor_bd_opcional - desconto_aplicado
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

async function novo_op_extra(id_op_extra, nome_opcional, valor_opcional, descricao_opcional) {
    op_extras.push({
        'id': id_op_extra,
        'nome': nome_opcional,
        'valor': valor_opcional,
        'descricao': descricao_opcional,
    })

    let newOption = new Option(
        nome_opcional,
        id_op_extra,
        true,
        true
    );

    $('#op_extras').append(newOption).trigger('change')

    $('#op_extras').trigger({
        type: 'select2:select',
        params: {
            data: {
                id: id_op_extra,
                text: nome_opcional
            }
        }
    })

    await enviar_form()

}

async function atualizar_valores_op(carregar = false) {
    if (carregar) {
        loading()
    }

    try {
        await enviar_form()
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
        await enviar_form()
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
        await enviar_form(true)
        window.location.href = '/'
    } catch (error) {
        alert(error)
    } finally {
        end_loading()
    }
}

function montar_pacote(check_promocional = null) {
    if (check_promocional) {
        if ($(check_promocional).prop('checked')) {
            $('#dados_do_pacote').modal('show')
            $('#id_cliente, #id_responsavel').attr('disabled', $('#id_promocional').prop('checked'))
        } else {
            $('#id_cliente').attr('disabled', $('#id_promocional').prop('checked'))
        }
    }
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
    let div_periodo = $(btn).parent().remove()
    let periodos_restantes = $('.div_periodos_aplicaveis').length
    let periodos = $('.periodos_aplicaveis')

    for (let i = 1; i <= periodos_restantes; i++) {
        $(periodos[i - 1]).attr('name', `periodo_${i}`).attr('id', `periodo_${i}`)
    }
}

function adicionar_periodo_novo(periodo = '') {
    let periodo_n = $('#lista_de_periodos .periodos_aplicaveis').length + 1

    let novo_obj_periodo = `
        <div class="mt-3 div_periodos_aplicaveis" style="display: flex; column-gap: 10px">
            <input type="text" id="periodo_${periodo_n}" value="${periodo}" name="periodo_${periodo_n}" class="periodos_aplicaveis">
            <button type="button" class="btn_remover_periodo" onclick="remover_periodo(this)"><span>&times;</span></button>
        </div>`
    $('#lista_de_periodos').append(novo_obj_periodo)
    $(`#periodo_${periodo_n}`).inicializarDateRange('DD/MM/YYYY', false)
}

function salvar_dados_do_pacote() {
    const dados_pacote = $('#form_dados_pacote').serializeObject()

    $.ajax({
        type: 'POST',
        url: '',
        data: dados_pacote,
        success: function (response) {
            $('#id_pacote, #id_pacote_promocional').val(response)
        }
    }).done(async () => {
        $('#dados_do_pacote').modal('hide')
        $('#container_monitoria_transporte, #container_periodo').removeClass('none')
        $('#subtotal').removeClass('none')
        await enviar_form()
        $('.div-flutuante').addClass('visivel')
    })
}

async function preencher_promocional(id_promocional) {
    await new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '',
            data: {'id_promocional': id_promocional},
            success: function (response) {
                $('#id_tipo_monitoria').val(response['monitoria'])
                $('#id_transporte input').map((index, transporte) => {
                    $(transporte).prop('checked', transporte.value === response['transporte'])
                })

                $('#id_atividades').val(response['atividades'])
                $('#id_atividades_ceu').val(response['atividades_ceu'])
                $('#id_opcionais').val(response['opcionais'])

                response['obj']['descricao_opcionais'].map((op, i) => {
                    if (op['valor'] !== undefined) {
                        let dados_op = {'valor': op['valor']}
                        let opcional = {'id': op['id'], 'text': op['nome']}
                        let desconto = formatar_dinheiro(op['desconto'])
                        listar_op(dados_op, 'id_opcionais', opcional, i + 1, desconto)
                    } else {
                        op['atividades'].map((ativ) => {
                            let dados_op = {'valor': ativ['valor']}
                            let opcional = {'id': ativ['id'], 'text': ativ['nome']}
                            let desconto = formatar_dinheiro(ativ['desconto'])
                            listar_op(dados_op, 'id_atividades', opcional, i + 1, desconto)
                        })

                        op['atividades_ceu'].map((ativ) => {
                            let dados_op = {'valor': ativ['valor']}
                            let opcional = {'id': ativ['id'], 'text': ativ['nome']}
                            let desconto = formatar_dinheiro(ativ['desconto'])
                            listar_op(dados_op, 'id_atividades_ceu', opcional, i + 1, desconto)
                        })
                    }
                })

                if (response['opcionais_extra']) {
                    for (let opt of response['opcionais_extra']) {
                        novo_op_extra(opt['id'], opt['nome'], opt['valor'], opt['descricao'])
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
                resolve(response)
            }
        }).done(() => {
            verificar_monitoria_transporte()
            $('#id_atividades, #id_atividades_ceu, #id_opcionais').trigger('change')
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
    await new Promise((resolve, reject) => {
        try {
            $('#info_promocional').prop('disabled', true)
            $('#form_gerencia')[0].reset()
            $('#data_pagamento, #modal_descritivo #data_vencimento').val(moment().add(15, 'd').format('YYYY-MM-DD'))
            $('#tabela_de_opcionais [id*=desconto]').val('0,00')

            resolve(true)
        } catch (e) {
            alert(e)
            reject(e)
        }
    })
}

function atualizar_periodo() {
    const periodo = $('#data_viagem').data('daterangepicker');
    let data_1 = moment($('#periodo_1').val().split(' - ')[0], 'DD/MM/YYYY')
    let n_dias = $('#id_minimo_de_diarias').val() != '' ? parseInt($('#id_minimo_de_diarias').val()) - 1 : 0
    periodo.setStartDate(data_1.format('DD/MM/YYYY 10:00'));
    periodo.setEndDate(data_1.add(n_dias, 'days').format('DD/MM/YYYY 20:00'));
}

async function mostrar_dados_pacote(pacote) {
    let id_pacote = pacote.value
    $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', false)

    if (id_pacote == '') {
        await resetar_forms()
        await enviar_form()
        $('#info_promocional').prop('disabled', true)

        return
    } else {
        $('#info_promocional').prop('disabled', false)
    }

    $.ajax({
        url: '',
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
                adicionar_periodo_novo(Object.values(periodos[_p])[0])
            }

            $('#tabela_de_opcionais tbody').empty()
            await preencher_promocional(id_pacote)
            $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', true)
            $('#form_dados_pacote fieldset').prop('disabled', true)
            $('#id_produtos_elegiveis').select2({
                disabled: 'readonly',
                width: '100%'
            })
            $('#id_produtos_elegiveis').trigger('change')
        }
    }).done(() => {
        $('#dados_do_pacote').modal('show')
    })
}

document.getElementById("btnPrint").onclick = function () {
    printTable()
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

async function verificar_gerencia() {
    loading()
    $('#server_error, #login_error').addClass('none').text('')
    $('#id_gerente').val('')

    $.ajax({
        url: '/orcamento/verificar_gerencia/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "GET",
        data: {'id_usuario': $('#usuario').val(), 'senha': $('#senha').val()},
        success: async function (response) {
            $('#id_gerente').val($('#usuario').val())

            if ($('#campos_alteraveis #desconto_geral').data('valor_alterado') == '0,00') {
                $('#campos_alteraveis #valor_final').data('valor_inicial', $('#campos_alteraveis #valor_final').val())
                $('#campos_alteraveis #valor_final').attr('data-valor_inicial', $('#campos_alteraveis #valor_final').val())
            }

            let limite_desconto = parseFloat($('#dados_do_pacote #id_limite_desconto_geral').val()) / 100
            let valor_final = parseFloat($('#campos_alteraveis #valor_final').data('valor_inicial').replace('.', '').replace('R$ ', '').replace(',', '.'))
            let valor_deconto = parseFloat($('#campos_alteraveis #desconto_geral').val().replace(',', '.'))

            if (valor_deconto > valor_final * limite_desconto) {
                $('#campos_alteraveis #desconto_geral').val((valor_final * limite_desconto).toFixed(2).replace('.', ','))
                alert(`Desconto pedido acima do limite possível de ${$('#dados_do_pacote #id_limite_desconto_geral').val()}%. Valor máximo deve ser de  R$ ${(valor_final * limite_desconto).toFixed(2).replace('.', ',')}`)
            }

            await enviar_form()
            $('#campos_alteraveis input').map((index, input) => {
                $(input).data('valor_alterado', $(input).val())
                $(input).attr('data-valor_alterado', $(input).val())
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

            $('#verificacao_gerencia').modal('hide')
            $('#alteracoes_aviso').addClass('none')
        },
        error: function (xht, status, error) {
            if (xht.status == 500) {
                $('#server_error').removeClass('none').text(xht['responseJSON']['msg'])
            }

            if (xht.status == 401) {
                $('#login_error').removeClass('none').text(xht['responseJSON']['msg'])
            }
        }
    })
    end_loading()
    $('#verificacao_gerencia #senha').val('')
}
