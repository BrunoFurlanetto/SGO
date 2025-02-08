/*let valor_atual, valores_op, valor_base, taxas_base, btn, desconto
let taxa_comercial_base = null
let comisao_base = null
let taxa_comercial = null
let valores_descontos
let comissao = null
let opcionais_aplicados = 0
let novas_taxas = 0
let comissao_aplicada = false
let taxa_aplicada = false
let outros = []
let desconto_aplicado = 0*/



$.fn.iniciarlizarDataTablePacotes = function (columnData, columnOrder, nonOrderableColumns) {
    // Inicializa o DataTable
    var tabela = $(this).DataTable({
        pageLength: 25,
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ páginas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [
            {
                type: 'date',
                targets: columnData,
                render: function (data, type, row) {
                    if (type === 'display' || type === 'filter') {
                        return moment(data).format('DD/MM/YYYY')
                    }
                    return data;
                },
            },
            {
                orderable: false,
                targets: nonOrderableColumns
            },
        ],
        order: [
            [columnOrder[0], 'asc'],
            [columnOrder[1], 'asc'],
        ]
    });

    // Filtro de data de vencimento
    function aplicarFiltroVencimento() {
        // Limpa os filtros antigos
        $.fn.dataTable.ext.search = [];

        // Obtém o valor selecionado no radio input
        var valorFiltro = $('input[name="vencidos"]:checked').val();

        // Se for 'sim', filtra pacotes vencidos
        if (valorFiltro === 'sim') {
            $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                return true
            });
        }
        // Se for 'não', filtra pacotes não vencidos
        else if (valorFiltro === 'nao') {
            $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                var dataVencimento = data[2]; // Índice da coluna de vencimento
                var dataHoje = moment(); // Data de hoje
                var dataTabela = moment(dataVencimento, 'DD/MM/YYYY');
                return dataTabela.isSameOrAfter(dataHoje); // Mostrar pacotes não vencidos
            });
        }

        // Atualiza a tabela com o filtro aplicado
        tabela.draw();
    }

    // Chama a função sempre que o valor do radio mudar
    $('input[name="vencidos"]').change(function () {
        aplicarFiltroVencimento();
    });

    // Aplica o filtro inicial, de acordo com o valor default
    aplicarFiltroVencimento();

    return tabela;
}

$(document).ready(() => {
    moment.locale('pt-br');

    // Inicialização da tabela de orçamentos (caso exista)
    $('#previas_orcamento .tabelas table').iniciarlizarDataTableOrcamento([0, 1, 4, 5], 0, [7, 8, 9, 10, 11]);

    // Inicialização da tabela de pacotes promocionais
    var tabelaPacotes = $('#tabela_pacotes_promocionais table').iniciarlizarDataTablePacotes(2, [0, 1, 2, 3], []);

    // Redesenha a tabela após a inicialização (pode ser necessário, caso queira garantir a aplicação do filtro)
    tabelaPacotes.draw();

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

$.fn.iniciarlizarDataTableOrcamento = function (columnData, columnOrder, nonOrderableColumns) {
    return $(this).DataTable({
        language: {
            info: 'Mostrando _PAGE_ página de _PAGES_ pagínas',
            infoEmpty: 'Sem dados',
            infoFiltered: '(filtrado de _MAX_ dados)',
            lengthMenu: 'Mostrar _MENU_ por página',
            zeroRecords: 'Nada encontrado',
        },
        columnDefs: [
            {
                type: 'date',
                targets: columnData,
                render: function (data, type, row) {
                    if (type === 'display' || type === 'filter') {
                        return moment(data).format('DD/MM/YYYY')
                    }

                    return data;
                },
            },
            {
                orderable: false,
                targets: nonOrderableColumns
            },
        ],
        order: [columnOrder, 'desc']
    })
}

function alterar_aba(aba, sectionId) {
    const conteudos_abas = $('.section-content').map((index, aba) => {
        return aba.id
    })
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

function alterar_status(btn, id_orcamento = '') {
    const novo_status = $(btn).attr('id')
    let orcamento_id = id_orcamento
    let motivo_recusa = ''
    loading()

    if (novo_status === 'perdido') {
        motivo_recusa = $('#modal_orcamento_perdido #motivo_recusa').val()
        orcamento_id = $('#modal_orcamento_perdido #id_orcamento_perdido').val()
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': orcamento_id, 'novo_status': novo_status, 'motivo_recusa': motivo_recusa},
    }).done((response) => {
        if (response['status'] === 'error') {
            alert(`Houve um erro durante a alteração de status do orçamento (${response['msg']}), por favor tente novamente mais tarde`)
        } else {
            setTimeout(() => {
                window.location.reload()
            }, 500)
        }
    }).catch((xht, status, error) => {
        alert(xht['responseJSON']['msg'])
        end_loading()
    })
}

function gerar_pdf_orcamento(id_tratativa) {
    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento_pdf': id_tratativa},
    })
}

function modal_de_tratativas(id_tratativa) {
    loading()
    $.ajax({
        type: 'GET',
        url: '/orcamento/pegar_orcamentos_tratativa/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_tratativa': id_tratativa},
        success: function (response) {
            const orcamentos = response['orcamentos']
            const tabela_tratativas = $('#tabela_tratativas tbody').empty()
            $('#modal_tratativas .modal-title span').text(orcamentos[0]['cliente'])
            $('#adicionar_tratativa').click(() => {
                window.location.href = `/orcamento/tratativa/${id_tratativa}/`
            })

            for (let orcamento of orcamentos) {
                tabela_tratativas.append(
                    `<tr id="orcamento_${orcamento['id_orcamento']}">
                        <td>${orcamento['status']}</td>
                        <td>${orcamento['apelido']}</td>
                        <td>${orcamento['vencimento']}</td>
                        <td>${orcamento['data_edicao']}</td>
                        <td>${orcamento['check_in']}</td>
                        <td>${orcamento['check_out']}</td>
                        <td>R$ ${orcamento['valor']}</td>
                        <td style="white-space: nowrap">
                            <button type="button" id="ganho" class="button_ganho" onclick="alterar_status(this, ${orcamento['id_orcamento']})">
                                <i class='bx bx-check'></i>
                            </button>
                            <button type="button" id="perdido" class="button_perdido" onclick="btn = this; $('#modal_orcamento_perdido #id_orcamento_perdido').val(${orcamento['id_orcamento']}); $('#modal_orcamento_perdido').modal('show')">
                                <i class='bx bx-x'></i>
                            </button>
                        </td>                                                                
                    </tr>`
                )

                if (['Vencido', 'Ganho', 'Perdido'].includes(orcamento['status'])) {
                    $(`#orcamento_${orcamento['id_orcamento']} button`).prop('disabled', true)
                }
            }
        }
    })
    $('#modal_tratativas').modal('show')
    end_loading()
}
