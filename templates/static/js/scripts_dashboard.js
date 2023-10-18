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

    $('#status #tabela_status_pre_reserva, #tabela_status_agendado, #tabela_status_ordem, #tabela_avisos').DataTable({
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

function inicializar_datatables(dados, colunas, alvo) {
    $(alvo).DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        data: dados,
        columns: colunas,
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

/*
function filtros(filtro) {
    loading()
    const id_filtro = $(filtro).parent().attr('id')
    let filtros_aplicados = {'filtro': id_filtro}

    $(`#${id_filtro} .filtros`).each(function () {
        const valor = $(this).val().trim()
        const chave = $(this).attr('name')

        if (valor !== '') {
            console.log(chave, valor)
            filtros_aplicados[chave] = valor
        }
    });

    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: filtros_aplicados,
        success: function (response) {
            console.log(response)
            if (id_filtro.includes('adesao')) {
                tabelar_adesao(response['fichas'])
            } else if (id_filtro.includes('status')) {
                tabelar_status()
            }
        }
    }).done(() => end_loading())
}

function tabelar_adesao(fichas) {
    $('#tabela_adesao').DataTable().destroy();

    $('#tabela_adesao').DataTable({
        data: fichas,
        columns: [
            {data: 'cliente_nome'},
            {data: 'convidada'},
            {data: 'confirmada'},
            {data: 'adesao'},
        ]
    });
}

function tabelar_status() {

}*/
