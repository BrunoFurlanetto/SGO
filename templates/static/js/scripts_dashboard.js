$(document).ready(() => {
    moment.locale('pt-br')

    $('#tabela_adesao').DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: 4, // Supondo que a primeira coluna contenha datas
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY'); // Formate a data como desejado
                }
                return data;
            }
        }],
        order: [
            [3, 'asc']
        ]
    })

    $('#status #tabela_status_ficha').DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: 4,
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY')
                }

                return data;
            }
        }],
        order: [4, 'asc']
    })

    $('#status #tabela_status_pre_reserva, #tabela_status_agendado, #tabela_status_ordem, #tabela_avisos, #tabela_sem_escala').DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: 3,
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY')
                }
                return data;
            }
        }],
        order: [3, 'asc']
    })
})

function alterar_aba(aba, sectionId) {
    const conteudos_abas = $('.section-content').map((index, aba) => {
        return aba.id
    })
    $('.folder:not([ativo])').removeClass('ativo')
    $(aba).addClass('ativo')
    console.log(aba, sectionId)
    for (let conteudo of conteudos_abas) {
        if (conteudo === sectionId) {
            $(`#${conteudo}`).addClass('ativo')
        } else {
            $(`#${conteudo}`).removeClass('ativo')
        }
    }
}