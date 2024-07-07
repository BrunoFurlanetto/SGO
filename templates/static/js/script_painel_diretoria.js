
function mostrar_infos(estagio, mes_ano) {
    loading()
    const tabela_infos_mes_estagios = $('#infos_mes_estagio table tbody').empty()

    $.ajax({
        url: '/painel-diretoria/infos_clientes_mes_estagios/',
        type: 'GET',
        data: {'estagio': estagio, 'mes_ano': mes_ano},
        success: function (response) {
            const infos = response['relatorio']
            const mes = mes_ano.split('/')[0]
            const ano = mes_ano.split('/')[1]
            $('#infos_mes_estagio .titulo_info_extra h4').text(`Eventos no estágio ${response['estagio']} para ${mes} de ${ano}`)

            for (let cliente of infos) {
                let nova_linha = `
                    <tr>
                        <td>${cliente['cliente']}</td>
                        <td>${cliente['reservado']}</td>
                        <td>${cliente['confirmado']}</td>
                    </tr>
                `
                tabela_infos_mes_estagios.append(nova_linha)
            }
        }
    }).done(() => {
        $('#infos_mes_estagio').removeClass('none')
        end_loading()
    }).catch((e) => {
        alert(e)
        end_loading()
    })
}