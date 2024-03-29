$(document).ready(() => {
    $('#conteudo_nova_previa #id_cnpj').mask("99.999.999/9999-99")
    $('#serie_grupo, #produto_peraltas').select2()
})

function verificar_preenchimento() {
    let nome_cliente = $('#id_nome_colegio').val()
    let cnpj = $('#id_cnpj').val()
    let nome_responsavel = $('#id_nome_responsavel').val()
    let telefone = $('#id_telefone_responsavel').val()

    if (![nome_cliente, cnpj, nome_responsavel, telefone].includes('')) {
        $('.dados_previa').removeClass('inativo')
        $('#aviso_preencher_campos').addClass('none')
    } else {
        $('#aviso_preencher_campos').removeClass('none')
        $('.dados_previa').addClass('inativo')
        $('.dados_previa input, .previa select').val('')
        $('#serie_grupo, #produto_peraltas').trigger('change')
    }
}

function validarCNPJ(input) {
    $('#aviso_cnpj').addClass('none')
    let cnpj = input.value.replace(/[^\d]+/g, '')
    var numeros, digitos, soma, i, resultado, pos, tamanho, digitos_iguais
    digitos_iguais = 1

    if (cnpj.length < 14 && cnpj.length > 0) {
        $(input).val('')
        $('#aviso_cnpj').removeClass('none')
    }

    for (i = 0; i < cnpj.length - 1; i++) {
        if (cnpj.charAt(i) != cnpj.charAt(i + 1)) {
            digitos_iguais = 0

            break
        }
    }

    if (!digitos_iguais) {
        tamanho = cnpj.length - 2
        numeros = cnpj.substring(0, tamanho)
        digitos = cnpj.substring(tamanho)
        soma = 0
        pos = tamanho - 7

        for (i = tamanho; i >= 1; i--) {
            soma += numeros.charAt(tamanho - i) * pos--;
            if (pos < 2) pos = 9
        }

        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11

        if (resultado != digitos.charAt(0)) {
            $(input).val('')
            $('#aviso_cnpj').removeClass('none')
        }

        tamanho = tamanho + 1
        numeros = cnpj.substring(0, tamanho)
        soma = 0
        pos = tamanho - 7

        for (i = tamanho; i >= 1; i--) {
            soma += numeros.charAt(tamanho - i) * pos--
            if (pos < 2) pos = 9
        }

        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11

        return resultado == digitos.charAt(1)
    } else {
        $(input).val('')
        $('#aviso_cnpj').removeClass('none')
    }
}

function mascara_telefone(input) {
    $(input).mask('(00) 0 0000-00009');
    $(input).blur(function (event) {
        if ($(input).val().length == 16) { // Celular com 9 dígitos + 2 dígitos DDD e 4 da máscara
            $(input).mask('(00) 0 0000-0009');
        } else {
            $(input).mask('(00) 0000-0000');
        }
    })
}

function validar_pacotes() {
    $('#produto_peraltas').val(null).trigger('change')
    $.ajax({
        url: '/pre_orcamento/validar_pacotes/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "POST",
        data: {'dias': $('#n_dias').val()},
        success: function (response) {
            for (let produto of $('#produto_peraltas option')) {
                if (produto.value != '') {
                    if (response['id_pacotes_validos'].includes(parseInt($(produto).val()))) {
                        $(produto).prop('disabled', false)
                    } else {
                        $(produto).prop('disabled', true)
                    }
                }
            }
        }
    })
}
