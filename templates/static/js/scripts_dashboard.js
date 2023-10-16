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

function filtros() {
    loading()

    $('.filtros').each(function() {
        const valor = $(this).val().trim()
        const chave = $(this).attr('name')

        if (valor !== '') {
            filtros_aplicados[chave] = valor;
        }
    });

    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: filtros_aplicados,
        success: function (response) {
            $('#tabela_adesao tbody').empty()

            for (let ficha of response['fichas']) {
                let classe = ''
                if (ficha['adesao'] < 50) {
                    classe = 'baixa'
                } else if (ficha['adesao'] > 50 && ficha['adesao'] < 70) {
                    classe = 'media'
                } else {
                    classe = 'alta'
                }

                $('#tabela_adesao tbody').append(`
                    <tr class="${classe}">
                        <td>${ficha['cliente']}</td>
                        <td>${ficha['convidada']}</td>
                        <td>${ficha['confirmada']}</td>
                        <td>${ficha['adesao'].toString().replace('.', ',')}%</td>
                    </tr>
                `)
            }
        }
    }).done(() => end_loading())
}