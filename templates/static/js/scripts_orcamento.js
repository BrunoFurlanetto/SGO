let resultado_ultima_consulta = {}
let op_extras = []
let mostrar_instrucao = true
let enviar, promocional = false
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

async function inicializacao(check_in = undefined, check_out = undefined) {
    $('#id_cliente').select2()
    $('#id_produtos_elegiveis').select2({
        dropdownParent: $("#dados_do_pacote .modal-content"),
        width: '100%'
    })
    $('#apelido_orcamento, #apelido_orcamento_2').val($('#id_apelido').val())
    $('select[name="opcionais"]').on('change', async () => {
        await enviar_op();
    });

    let hoje = new Date()
    $('#modal_descritivo #data_vencimento').val(moment(hoje).add(15, 'd').format('YYYY-MM-DD'))
    promocional = $('#tipo_de_orcamento').val() == 'promocional'
    $('#data_viagem').inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
    $('#lista_de_periodos input').inicializarDateRange('DD/MM/YYYY', false)

    if (check_in && check_out) {
        $('#data_viagem').val(`${check_in} - ${check_out}`).inicializarDateRange('DD/MM/YYYY HH:mm', true, verificar_datas)
    }

    $('#valor_opcional').mascaraDinheiro()
    $('#ajuste_diaria').mascaraDinheiro()
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

        console.log($(this).attr('id'))
        let nome_id = relacao_id_categoria[$(this).attr('id')]
        loading()

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
            end_loading()
        }
    })

    $('select[name="opcionais"]').on("select2:unselect", async function (e) {
        loading()
        const opcao = e.params.data;

        try {
            $(`#opcionais_${relacao_id_categoria[$(this).attr('id')]}_${opcao['id']}`).remove()
        } catch (error) {
            alert(error)
            end_loading()
        } finally {
            // await atualizar_valores_op()
            await listar_op(null, opcao, null, '0,00', true)
            await enviar_form()
            end_loading()
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
    $('#lista_de_periodos .periodos_aplicaveis').on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY')).trigger('change');
    })

    $('#lista_de_periodos .div_periodos_aplicaveis .periodos_aplicaveis').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });
}

function verificar_produto() {
    const produto = $('#id_produto option:selected').text().toLowerCase()

    if (produto.includes('ceu')) {
        $('#form_gerencia fieldset, #btn_alterar_taxas, #id_opcionais_eco, #id_opcionais_ceu').prop('disabled', true)
    } else {
        $('#form_gerencia fieldset, #btn_alterar_taxas, #id_opcionais_eco, #id_opcionais_ceu').prop('disabled', false)
    }
}

async function verificar_alteracoes(div) {
    // if ($('#id_promocional').prop('checked')) {


    // return
    // }

    await verificar_pisos_e_tetos()
    await enviar_form()

    // setInterval(() => {
    //     $('#btn_salvar_orcamento').prop('disabled', !$('#div_observacoes_gerencia').hasClass('none') && $('#observacoes_gerencia').val().length < 10)
    // }, 10)

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

    // if (mostrar_mensagem) {
    //     $('#alteracoes_aviso').removeClass('none')
    // } else {
    //     $('#alteracoes_aviso').addClass('none')
    // }
    //
    // if (mostrar_mensagem) {
    //     $('#div_observacoes_gerencia').removeClass('none')
    //     $('#observacoes_gerencia').prop('required', true)
    //     // $('#btn_salvar_orcamento').prop('disabled', true)
    //     $('.botoes').attr('title', 'Verificar observações para a gerência')
    // } else {
    //     $('#div_observacoes_gerencia').addClass('none')
    //     $('#observacoes_gerencia').val('').prop('required', false)
    //     $('#btn_salvar_orcamento').prop('disabled', false)
    //     $('.botoes').attr('title', '')
    // }
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
        allowNegative: true,
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

async function listar_op(dados_op, opcao, i, desconto = '0,00', removido = false) {
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
        </tr>
    `)
}

function criar_linhas_tabela_valores(categorias) {
    const tabela_valores = $('#tabela_de_valores tbody').empty()
    tabela_valores.append(`<tr id="diaria"><td colspan="2">Diarias</td></tr>`)
    tabela_valores.append(`<tr id="periodo_viagem"><td colspan="2">Taxa fixa</td></tr>`)
    tabela_valores.append(`<tr id="tipo_monitoria"><td colspan="2">Monitoria</td></tr>`)
    tabela_valores.append(`<tr id="transporte"><td colspan="2">Transporte</td></tr>`)

    for (let categoria in categorias) {
        tabela_valores.append(`<tr id='${categorias[categoria]}'><td colspan="2">${categoria}<i class='bx bxs-chevron-down' onclick="$('#tabela_de_valores .${categorias[categoria]}_descritivo').toggleClass('none')"></i></td></tr>`)
    }

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
            valor_final
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
                valores: []
            }
        }

        // Soma os campos individuais
        acc[categoria_lower].valor += valor
        acc[categoria_lower].comissao += comissao_de_vendas
        acc[categoria_lower].desconto += desconto
        acc[categoria_lower].taxa_comercial += taxa_comercial
        acc[categoria_lower].valor_com_desconto += valor_com_desconto
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
        let linhaEspecifica = $(`#tabela_de_valores #${id_linhas[opt['categoria']]}`);
        var classe_ultimo_valor = ''

        if (i == 1) {
            classe_ultima_linha = 'ultima_linha'
        }

        let novaLinha = `<tr id='${id_linhas[opt['categoria']]}_${i}' class="${id_linhas[opt['categoria']]}_descritivo none atividade_ou_opcional">
            <td></td>
            <td>${opt['nome']}</td>
            <td><nobr>R$ ${formatar_dinheiro(opt['valor'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opt['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opt['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(opt['valor'] - opt['valor_com_desconto'])}</nobr></td>
            <td class="valor_final_tabela ${classe_ultima_linha}"><nobr>R$ ${formatar_dinheiro(opt['valor_final'])}</nobr></td>
        </tr>`
        linhaEspecifica.after(novaLinha)

        for (let valor_dia of opt['valores']) {
            $(`#tabela_de_valores #${id_linhas[opt['categoria']]}_${i}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
        }

        i++
    }
}

function tabela_descrito(valores, dias, taxa, opcionais, totais, racionais) {
    $('#tabela_de_valores .datas').remove()
    $('.tag_datas').prop('colspan', dias.length)
    const soma_por_categoria_opcionais = sumByCategory(opcionais)
    let classe_datas = ''
    let categorias = {}

    opcionais.map((opt) => {
        // Remove todos os caracteres especiais, mantendo apenas letras e números
        let categoria = opt['categoria'].toLowerCase().replace(/[^a-z0-9]/g, '');

        // Verifica se a categoria já existe em id_linhas
        if (!categorias.hasOwnProperty(categoria)) {
            categorias[opt['categoria']] = categoria;
        }
    })

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
        if (!secao.includes('opcionais')) {
            $(`#tabela_de_valores #${secao}`).append(`
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['valor'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(valores[secao]['valor'] - valores[secao]['valor_com_desconto'])}</nobr></td>                 
            <td class="valor_final_tabela"><nobr>${formatar_dinheiro(valores[secao]['valor_final'])}</nobr></td>
        `)

            for (let valor_dia of valores[secao]['valores']) {
                $(`#tabela_de_valores #${secao}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
            }
        }
    }

    for (let categoria in soma_por_categoria_opcionais) {
        $(`#tabela_de_valores #${categoria}`).append(`
            <td><nobr>R$ ${formatar_dinheiro(soma_por_categoria_opcionais[categoria]['valor'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(soma_por_categoria_opcionais[categoria]['taxa_comercial'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(soma_por_categoria_opcionais[categoria]['comissao_de_vendas'])}</nobr></td>
            <td><nobr>R$ ${formatar_dinheiro(soma_por_categoria_opcionais[categoria]['valor'] - soma_por_categoria_opcionais[categoria]['valor_com_desconto'])}</nobr></td>                 
            <td class="valor_final_tabela"><nobr>${formatar_dinheiro(soma_por_categoria_opcionais[categoria]['valor_final'])}</nobr></td>
        `)

        for (let valor_dia of soma_por_categoria_opcionais[categoria]['valores']) {
            $(`#tabela_de_valores #${categoria}`).append(`<td><nobr>R$ ${formatar_dinheiro(valor_dia)}</nobr></td>`)
        }
    }

    linhas_descritivo_opcionais(opcionais)

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

    $(`#tabela_de_valores #arredondamento`).append(`
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
    return await new Promise(async (resolve, reject) => {
        $('#campos_alteraveis input').map((index, campo) => {
            let valor, piso, teto

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
            }

            if (parseFloat(valor) > parseFloat(teto)) {
                $(campo).val($(campo).data('teto'))
            }
        })

        await teto_desconto()

        resolve()
    })
}

async function teto_desconto() {
    return await new Promise((resolve, reject) => {
        let teto_percent

        if ($('#id_orcamento_promocional').val() != '') {
            teto_percent = parseFloat($('#dados_do_pacote #id_limite_desconto_geral').val()) / 100
        } else {
            teto_percent = parseFloat(resultado_ultima_consulta['limites_taxas']['teto_desconto']) / 100
        }

        const desconto = parseFloat($('#ajuste_diaria').val().replace(',', '.'))

        if (desconto > teto_percent * valor_padrao()) {
            $('#ajuste_diaria').val(formatar_dinheiro((teto_percent * valor_padrao()).toFixed(2)))
        }

        resolve()
    })
}

function valor_padrao() {
    let taxa_comercial_default = $('#modal_descritivo #taxa_comercial').data('valor_default').replace('%', '')
    let comissao_default = $('#modal_descritivo #comissao').data('valor_default').replace('%', '')
    let valor_sem_desconto = resultado_ultima_consulta['data']['total']['valor']
    let taxa_comercial = (valor_sem_desconto / (1 - (parseFloat(taxa_comercial_default) / 100))) - valor_sem_desconto
    let comissao = (valor_sem_desconto / (1 - (parseFloat(comissao_default) / 100))) - valor_sem_desconto

    return valor_sem_desconto + taxa_comercial + comissao
}

async function enviar_form(salvar = false, gerente_aprovando = false, id_orcamento = undefined) {
    let url = '/orcamento/calculos/'

    if ($('#id_orcamento_promocional').val() != '') {
        $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', false)
    }

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

async function separar_produtos(periodo) {
    let check_in = $(periodo).val().split(' - ')[0]
    let check_out = $(periodo).val().split(' - ')[1]
    let data_check_in = moment(check_in, 'DD/MM/YYYY HH:mm')
    let data_check_out = moment(check_out, 'DD/MM/YYYY HH:mm')

    await new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/orcamento/validar_produtos/',
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
        verficar_validade_opcionais(check_in)
    })

    try {
        if (data_check_out.diff(data_check_in, 'days') != parseInt(resultado_ultima_consulta['data']['n_dias'])) {
            setTimeout(() => {
                if ($('#id_produto').val() == null) {
                    $('#id_produto').val('')
                }
            }, 1)
        }
    } catch (e) {
    }
}

async function verificar_preenchimento() {
    const floatingBox = $('#floatingBox')
    $('.div-flutuante').removeClass('none')
    // await separar_produtos($('#data_viagem'))

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
            $('select[name="opcionais"]').select2()
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

async function enviar_op() {
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

async function novo_op_extra(id_op_extra, nome_opcional, valor_opcional, descricao_opcional, editando = false) {
    loading()
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
    end_loading()
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

async function salvar_orcamento(salvar_previa = false) {
    loading()

    try {
        $('#salvar_previa').val(String(salvar_previa))
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
            $('#promocionais').addClass('none')
        } else {
            $('#promocionais').removeClass('none')
            $('#id_cliente').attr('disabled', $('#id_promocional').prop('checked'))
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

    inicializar_funcoes_periodos_promocional()
}

function salvar_dados_do_pacote() {
    loading()
    const dados_pacote = $('#form_dados_pacote').serializeObject()

    $.ajax({
        type: 'POST',
        url: '/orcamento/salvar_pacote/',
        data: dados_pacote,
        success: function (response) {
            $('#id_pacote, #id_pacote_promocional').val(response['id_pacote'])
            const min_diarias = parseInt($('#id_minimo_de_diarias').val())
            const data_1 = moment($('#periodo_1').val().split(' - ')[0], 'DD/MM/YYYY')
            const data_2 = moment(data_1).add(min_diarias - 1, 'd')
            let periodo = $('#data_viagem').data('daterangepicker')
            periodo.setStartDate(data_1.format('DD/MM/YYYY') + ' ' + response['menor_horario']);
            periodo.setEndDate(data_2.format('DD/MM/YYYY') + ' ' + response['maior_horario']);
            $('#data_viagem').val(periodo.startDate.format('DD/MM/YYYY HH:mm') + ' - ' + periodo.endDate.format('DD/MM/YYYY HH:mm')).trigger('change');
            $('#id_produto').val($('#id_produtos_elegiveis').val()).prop('disabled', false).trigger('change')
            // inicializar_funcoes_periodo_viagem()
        }
    }).done(async () => {
        $('#dados_do_pacote').modal('hide')
        $('#container_monitoria_transporte, #container_periodo').removeClass('none')
        $('#subtotal').removeClass('none')
        await enviar_form()
        $('.div-flutuante, #container_periodo .parcial').addClass('visivel')
        $('#btn_dados_pacote').prop('disabled', false)
    })
    end_loading()
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

                for (let categoria in response['opcionais']) {
                    $(`#opcionais_${categoria}`).val(response['opcionais'][categoria])
                }

                response['obj']['descricao_opcionais'].map((op, i) => {
                    let dados_op = {'valor': op['valor']}
                    let opcional = {'id': op['id'], 'text': op['nome']}
                    let desconto = formatar_dinheiro(op['desconto'])
                    listar_op(dados_op, opcional, i + 1, desconto)
                })

                if (response['opcionais_extra']) {
                    for (let opt of response['opcionais_extra']) {
                        await novo_op_extra(opt['id'], opt['nome'], opt['valor'], opt['descricao'])
                    }
                }

                for (let id_campo in response['gerencia']) {
                    if (id_campo == 'ajuste_diaria') {
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
                $('#desconto_transporte_percent').val(response['gerencia']['desconto_transporte_percent'])
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
    await new Promise((resolve, reject) => {
        try {
            $('#info_promocional').prop('disabled', true)
            $('#form_gerencia')[0].reset()
            $('#modal_descritivo #data_vencimento').val(moment().add(15, 'd').format('YYYY-MM-DD'))
            $('#tabela_de_opcionais [id*=desconto]').val('0,00')
            let default_data_pagamento = $('#data_pagamento').data('valor_default')
            $('#data_pagamento').val(default_data_pagamento)

            resolve(true)
        } catch (e) {
            alert(e)
            reject(e)
        }
    })
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
        url: '/orcamento/pegar_dados_pacoe/',
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

            $('#tabela_de_opcionais tbody, #lista_opcionais_extra').empty()
            op_extras = []
            await preencher_promocional(id_pacote)
            $('#campos_fixos input, #campos_fixos select, #campos_fixos button').prop('disabled', true)
            $('#form_dados_pacote fieldset').prop('disabled', true)
            $('#id_produtos_elegiveis').select2({
                disabled: 'readonly',
                width: '100%'
            }).trigger('change')
        }
    }).done(() => {
        $('#dados_do_pacote').modal('show')
    })
}

try {
    document.getElementById("btnPrint").onclick = function () {
        printTable()
    }
} catch (e) {}


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
        type: "POST",
        data: {'id_usuario': $('#usuario').val(), 'senha': $('#senha').val()},
        success: async function (response) {
            $('#id_gerente').val($('#usuario').val())

            if ($('#campos_alteraveis #ajuste_diaria').data('valor_alterado') == '0,00') {
                $('#campos_alteraveis #valor_final').data('valor_inicial', $('#campos_alteraveis #valor_final').val())
                $('#campos_alteraveis #valor_final').attr('data-valor_inicial', $('#campos_alteraveis #valor_final').val())
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

function atribuir_apelaido(input_apelido) {
    $('#id_apelido').val(input_apelido.value)
    if (input_apelido.value.length > 5) {
        $('#btn_salvar_apelido').prop('disabled', false)
    } else {
        $('#btn_salvar_apelido').prop('disabled', true)
    }
}

async function editar_opcional_extra(pai, elemento) {
    loading()
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
    end_loading()
}

function verficar_validade_opcionais(check_in) {
    $('select[name="opcionais"]').val()

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
                    let opValue = parseInt(op.val());

                    if (!response['id_opcionais'].includes(opValue)) {
                        op.prop('disabled', true);

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
                        op.prop('disabled', false);
                    }
                })
            })
            $('select[name="opcionais"]').select2()
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
