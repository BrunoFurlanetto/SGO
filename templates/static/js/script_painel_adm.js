$(document).ready(() => {
    $('#resumo_por_mes').DataTable({
        ordering: false,
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
    })
})

function tabelar_mes(linha) {
    const mes_ano = $(linha).data('mes_ano')
    loading()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'mes_ano': mes_ano},
        success: function (response) {
            const tabela_detalhes = $('#tabela_detalhe_mes tbody').empty()
            $('#form_gerar_pdf #mes_ano').val(mes_ano)

            for (let professor of response['dados']) {
                tabela_detalhes.append(`
                    <tr>
                        <td>${professor['nome']}</td>
                        <td>${professor['atividades']}</td>
                        <td>${professor['horas']}</td>
                        <td><nobr>R$ ${formatar_dinheiro(professor['valor_atividades'])}</nobr></td>
                        <td><nobr>R$ ${formatar_dinheiro(professor['valor_horas'])}</nobr></td>
                        <td><nobr>R$ ${formatar_dinheiro(professor['valor_atividades'] + professor['valor_horas'])}</nobr></td>
                    </tr>
                `)
            }
        }
    }).done(() => {
        $('#detalhe_mes').modal('show')
        end_loading()
    }).catch((error) => {
        alert(error)
        end_loading()
    })
}