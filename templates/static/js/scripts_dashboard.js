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
                        return moment(data).format('DD/MM/YYYY');
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

    // Defina o filtro apenas para essa instância
    var tabelaElemento = tabela.table().node();

    function filtroCustomizado(settings, data, dataIndex) {
        // Se o filtro não for desta tabela, não aplica
        if (settings.nTable !== tabelaElemento) return true;

        var valorFiltro = $('input[name="vencidos"]:checked').val();

        if (valorFiltro === 'sim') {
            return true;
        } else if (valorFiltro === 'nao') {
            var dataVencimento = data[2]; // Índice da coluna de vencimento
            var dataHoje = moment();
            var dataTabela = moment(dataVencimento, 'DD/MM/YYYY');
            return dataTabela.isSameOrAfter(dataHoje);
        }

        return true;
    }

    // Adiciona filtro sem sobrescrever os demais
    $.fn.dataTable.ext.search.push(filtroCustomizado);

    function aplicarFiltroVencimento() {
        tabela.draw(); // Apenas redesenha a tabela atual
    }

    $('input[name="vencidos"]').change(function () {
        aplicarFiltroVencimento();
    });

    aplicarFiltroVencimento();

    return tabela;
};


$(document).ready(() => {
    $('#previas_orcamento td.clicavel, #tratativas td.clicavel, #previas_de_colaboradores td.clicavel').on('click', function () {
        if ($(this).data('tratativa')) {
            window.location.href = `/orcamento/ver_tratativa/${$(this).data('id_orcamento')}/`
        } else {
            window.location.href = `/orcamento/editar_previa/${$(this).data('id_orcamento')}/`
        }
    })

    moment.locale('pt-br');

    // Inicialização da tabela de orçamentos (caso exista)
    $('#tabela_previas_orcamento').iniciarlizarDataTableOrcamento([0, 1, 4, 5], 0, [7, 8]);
    $('#tabela_previas_de_colaboradores').iniciarlizarDataTableOrcamento([0, 1, 4, 5], 0, [7, 8]);
    $('#tabela_tratativas_em_aberto').iniciarlizarDataTableOrcamento([2, 3, 4], 0, [7]);
    $('#tabela_tratativas_negadas_vencidas').iniciarlizarDataTableOrcamento([3], 0, [5, 6]);
    $('#tabela_tratativas_ganhas').iniciarlizarDataTableOrcamento([], 0, [3, 4]);

    // Inicialização da tabela de pacotes promocionais
    var tabelaPacotes = $('#tabela_pacotes_promocionais table').iniciarlizarDataTablePacotes(2, [0, 1, 2, 3], []);

    // Redesenha a tabela após a inicialização (pode ser necessário, caso queira garantir a aplicação do filtro)
    tabelaPacotes.draw();

    moment.locale('pt-br')
    // $('#tabela_relatorio').iniciarlizarDataTable([], undefined)
    if ($('.monitoria').length == 0) {
        $('#tabela_adesao').iniciarlizarDataTable(4, 3)
        $('#status #tabela_status_ficha').iniciarlizarDataTable(5, 5)
        $('#status #tabela_status_pre_reserva, #tabela_status_agendado, #tabela_avisos, #tabela_sem_escala, #tabela_com_escala').iniciarlizarDataTable(3, 3)
        $('#fichas_financeiras_aprovar table').iniciarlizarDataTableOrcamento([0, 3, 4], 0, [])
        $('#fichas_financeiras table').iniciarlizarDataTableOrcamento([0, 1, 4, 5], 0, [])
        $('#fichas_financeiras_financeiro .aprovadas, #fichas_financeiras_financeiro .negadas').iniciarlizarDataTableOrcamento([0, 1, 4, 5], 0, [])
        $('#fichas_financeiras_financeiro .aguardando').iniciarlizarDataTableOrcamento([0, 3, 4], 0, [])
        $('#tabela_avaliacoes_monitoria, #tabela_avaliacoes_coordenadores').iniciarlizarDataTable([1], 1, 'desc')
        $('#tabela_avaliacoes_clientes').iniciarlizarDataTable([1], 1, 'desc')
        $('#tabela_status_ordem').iniciarlizarDataTable([4], 4, 'desc')
    } else {
        // Inicialização das tabelas do dashboard da monitoria
        $('#tabela_status_pre_reserva, #tabela_status_agendado').iniciarlizarDataTable([3, 4], 3)
        $('#tabela_status_ordem').iniciarlizarDataTable([5], 5)
        $('#tabela_status_ficha').iniciarlizarDataTable([5], 6)
    }
})

$.fn.iniciarlizarDataTable = function (columnData, columnOrder, senseOrder='asc') {
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
        order: [columnOrder, senseOrder]
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
                orderSequence: ['asc', 'desc', ''],
                render: function (data, type, row) {
                    if (type === 'display' || type === 'filter') {
                        return moment(data).format('DD/MM/YYYY HH:mm')
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

function perder_orcamento() {
    let orcamento_id = $('#modal_orcamento_perdido #id_orcamento_perdido').val()
    let motivo_recusa = $('#modal_orcamento_perdido #motivo_recusa').val()

    $.ajax({
        type: 'POST',
        url: '/orcamento/perdido/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': orcamento_id, 'motivo_recusa': motivo_recusa},
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
        // end_loading()
    })
}

function ganhar_orcamento(id_orcamento) {
    $.ajax({
        type: 'POST',
        url: '/orcamento/ganho/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_orcamento': id_orcamento},
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
        // end_loading()
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

function clonar_orcamento(resp) {
    if (resp) {
        let motivo_recusa = prompt('Qual o motivo da recusa do cliente?', 'Orçamento  clonado')
        $.ajax({
            type: 'POST',
            url: '/orcamento/perdido/',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {'id_orcamento': $('#id_orcamento_clonado').val(), 'motivo_recusa': motivo_recusa},
        }).then(() => {
            window.location.href = `/orcamento/clonar/${$('#id_orcamento_clonado').val()}`
        }).catch((xht, status, error) => {
            alert(xht['responseJSON']['msg'])
        })
    } else {
        window.location.href = `/orcamento/clonar/${$('#id_orcamento_clonado').val()}`
    }
}

const botoes = document.querySelectorAll('.btn-confirmar-escala');

botoes.forEach(function(botao) {
    // Alterar o texto quando o mouse estiver sobre o botão
    botao.addEventListener('mouseenter', function() {
        // Adiciona a classe de desvanecimento
        this.classList.add('fade-out');

        setTimeout(() => {
            this.textContent = 'Confirmar';
            this.classList.remove('fade-out');
            this.classList.add('fade-in'); // Adiciona a classe de fade-in
        }, 200); // Tempo para aguardar antes de mudar o texto
    });

    // Restaurar o texto original quando o mouse sair do botão
    botao.addEventListener('mouseleave', function() {
        this.classList.remove('fade-in'); // Remove a classe de fade-in
        this.classList.add('fade-out'); // Adiciona a classe de desvanecimento

        setTimeout(() => {
            this.textContent = 'Não';  // Texto original
            this.classList.remove('fade-out'); // Remove a classe de desvanecimento
        }, 50); // Tempo para aguardar antes de mudar o texto
    });
});


