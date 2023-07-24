function alterar_aba(aba, sectionId) {
    const conteudos_abas = [
        'orcamentos_aprovacao',
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

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': id_orcamento},
        success: function (response) {
            const tabela_pedidos = $('#tabela_pedidos tbody').empty()
            const tabela_opcionais = $('#tabela_descontos_opcionais tbody').empty()
            $('#comentario_pedido').text('OBS do colaborador: ' + response['observacoes'])

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
                        } else {
                            valor_formatado = valor[0]
                            valor_padrao = valor[1]
                        }

                        tabela_pedidos.append(`
                            <tr>
                                <td>${chave}</td>
                                <td>${valor_padrao}</td>
                                <td>${valor_formatado}</td>
                                <td><input type="checkbox" id="resposta_${chave}"></td>
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
                        <td><input type="checkbox"></td>                    
                    </tr>
                `)
            }
        }
    })

    $('#permissao_orcamentos').modal('show')
}

function convert_money (valor) {
    return 'R$ ' + valor.toLocaleString(
        undefined,
        {minimumFractionDigits: 2, maximumFractionDigits: 2}
    )
}
