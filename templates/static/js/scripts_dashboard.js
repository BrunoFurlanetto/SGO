$(document).ready(() => {
    moment.locale('pt-br')

    if ($('.monitoria').length == 0) {
        $('#tabela_adesao').iniciarlizarDataTable(4, 3)
        $('#status #tabela_status_ficha').iniciarlizarDataTable(4, 4)
        $('#status #tabela_status_pre_reserva, #tabela_status_agendado, #tabela_status_ordem, #tabela_avisos, #tabela_sem_escala').iniciarlizarDataTable(3, 3)
    } else {
        // Inicialização das tabelas do dashboard da monitoria
        $('#tabela_status_pre_reserva, #tabela_status_agendado').iniciarlizarDataTable([3, 4], 3)
        $('#tabela_status_ordem, #tabela_status_ficha').iniciarlizarDataTable([4, 5], 4)
    }
})

$.fn.iniciarlizarDataTable = function (columnData, columnOrder) {
    return $(this).DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [{
            type: 'date',
            targets: columnData,
            render: function (data, type, row) {
                if (type === 'display' || type === 'filter') {
                    return moment(data).format('D [de] MMMM [de] YYYY')
                }

                return data;
            },
        }],
        order: [columnOrder, 'asc']
    })
}

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