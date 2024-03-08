$(document).ready(() => {
    $('#id_comissao').mask('00,00%', {reverse: true})
    $('#id_cnpj').mask("99.999.999/9999-99")
    $('#id_valor_a_vista').DinheiroMascara()

    $('#form_ficha_financeira').submit(function() {
        let comissaoValue = $('#id_comissao').val()
        let valor_a_vista = $('#id_valor_a_vista').val()

        comissaoValue = comissaoValue.replace('%', '')
        valor_a_vista = valor_a_vista.replace('.', '').replace(',', '.')

        $('#id_comissao').val(parseInt(comissaoValue))
        $('#id_valor_a_vista').val(parseFloat(valor_a_vista))
    });
})

$.fn.DinheiroMascara = function () {
    return $(this).maskMoney({
        prefix: 'R$ ',
        thousands: '.',
        decimal: ',',
        allowZero: true,
        affixesStay: false,
        allowNegative: true,
    })
}

function verificar_vencimentos(input) {
    const id_input = $(input).attr('id')
    const inicio_vencimento = moment($('#id_inicio_vencimento').val())
    const final_vencimento = moment($('#id_final_vencimento').val())
    const parcelas = parseInt($('#id_parcelas').val())
    $('.planos_pagamento .alert').addClass('none')

    if (id_input != 'id_final_vencimento') {
        $('#id_final_vencimento').val(inicio_vencimento.add(parcelas - 1, 'month').format('YYYY-MM-DD'))
    } else {
        if (final_vencimento.month() - inicio_vencimento.month() != parcelas - 1) {
            $('.planos_pagamento .alert').removeClass('none')
        }
    }
}

function verificar_metodo_pagamento() {
    const metodo_pagamento = $('#id_forma_pagamento option:selected').text()

    if (metodo_pagamento.includes('vista')) {
        $('#id_parcelas').val(1).attr('readonly', true)
        $('#id_final_vencimento').val(moment($('#id_inicio_vencimento').val()).format('YYYY-MM-DD')).attr('readonly', true)
    } else {
        $('#id_parcelas, #id_final_vencimento').attr('readonly', false)

    }
}
