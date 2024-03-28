$(document).ready(() => {
    $('#conteudo_nova_previa #id_cnpj').mask("99.999.999/9999-99")
})

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

