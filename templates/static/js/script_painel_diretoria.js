let chartProdutoInstance = null;
let chartEstagioInstance = null;
let outrosItemsProduto = [];
let outrosItemsEstagio = [];
let ultimo_estagio = null
let ulimo_mes_ano = null
let descritivo_refeicoes = null

$(document).ready(() => {
    $('#dialog').dialog({
        autoOpen: false,
        modal: false,
        width: 250,
        position: {my: "right top", at: "right top", of: window}
    });

    $('#campos_eventos').select2({
        maximumSelectionLength: 6
    })

    $('#campos_eventos').on("select2:select", function () {
        let selectedOptions = $(this).val()
        $('#mensagem_aviso').addClass('none')

        if (selectedOptions && selectedOptions.length >= 2) {
            mostrar_infos(ultimo_estagio, ulimo_mes_ano)
        } else {
            $('#mensagem_aviso').removeClass('none');
        }
    })

    $('#campos_eventos').on("select2:unselect", function () {
        let selectedOptions = $(this).val()
        $('#mensagem_aviso').addClass('none')

        if (selectedOptions && selectedOptions.length >= 2) {
            mostrar_infos(ultimo_estagio, ulimo_mes_ano)
        } else {
            $('#mensagem_aviso').removeClass('none');
        }
    })
})

function mostrar_infos(estagio, mes_ano) {
    loading()
    const campos_selecionados = $('#campos_eventos').val()
    ulimo_mes_ano = mes_ano
    ultimo_estagio = estagio

    $.ajax({
        url: '/painel-diretoria/infos_clientes_mes_estagios/',
        type: 'GET',
        data: {'estagio': estagio, 'mes_ano': mes_ano, 'campos': campos_selecionados},
        success: function (response) {
            const mes = mes_ano.split('/')[0]
            const ano = mes_ano.split('/')[1]
            const colunas = response['campos']
            const relatorios = response['relatorio']

            $('#infos_mes_estagio .titulo_info_extra h4').text(`Eventos no estágio ${response['estagio']} para ${mes} de ${ano}`)
            tabelar_colunas(colunas)
            tabelar_dados(relatorios)
        }
    }).done(() => {
        $('#infos_mes_estagio').removeClass('none')
        end_loading()
    }).catch((e) => {
        alert(e)
        end_loading()
    })
}

function tabelar_colunas(colunas) {
    const cabecalho_tabela = $('#tabela_dados_extra_eventos thead tr').empty()
    colunas.map((coluna) => {
        console.log(coluna)
        cabecalho_tabela.append(`<td>${coluna}</td>`)
    })
}

function tabelar_dados(relatorios) {
    const tabela_infos_mes_estagios = $('#infos_mes_estagio table tbody').empty()
    console.log(relatorios)
    for (let relatorio of relatorios) {
        let nova_linha = $(`<tr></tr>`)
        tabela_infos_mes_estagios.append(nova_linha)

        for (let campo in relatorio) {
            if (relatorio[campo]['url']) {
                nova_linha.append(`<td><a target="_blank" href="${relatorio[campo]['url']}">${relatorio[campo]['cliente']}</a></td>`)
            } else {
                nova_linha.append(`<td>${relatorio[campo]}</td>`)
            }
        }
    }
}

function graficar_produto_estagio(mes_ano) {
    loading()
    $('#grafico_info_extra').removeClass('none')
    $('#relatorio_produtos #grafico_info_extra h4').text(`${mes_ano.split('/')[0]} de ${mes_ano.split('/')[1]}`)

    $.ajax({
        url: '/painel-diretoria/infos_produtos_estagios/',
        type: 'GET',
        data: {'mes_ano': mes_ano},
        success: function (response) {
            if (chartProdutoInstance) {
                chartProdutoInstance.destroy();
            }

            if (chartEstagioInstance) {
                chartEstagioInstance.destroy();
            }

            drawChartEstagio(response['dados_estagio'])
            drawChartProduto(response['dados_produto'])
        }
    }).done(() => end_loading()).catch((e) => {
        alert(e)
        end_loading()
    })
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function generateRandomColors(numColors) {
    const colors = [];
    for (let i = 0; i < numColors; i++) {
        colors.push(getRandomColor());
    }
    return colors;
}

function processData(labels, data) {
    const maxItems = 10;
    let outrosItems = [];

    // Ordenar os dados por valor (crescente)
    const sortedData = labels.map((label, index) => ({
        label,
        value: data[index]
    })).sort((a, b) => a.value - b.value);

    if (data.length > maxItems) {
        const topData = sortedData.slice(-maxItems + 1);
        const outrosData = sortedData.slice(0, -maxItems + 1);

        outrosItems = outrosData.map(item => ({label: item.label, value: item.value}));

        const otherData = outrosItems.reduce((acc, item) => acc + item.value, 0);
        topData.push({label: 'Outros', value: otherData});

        return {
            labels: topData.map(item => item.label),
            data: topData.map(item => item.value),
            outrosItems
        };
    }

    return {
        labels: sortedData.map(item => item.label),
        data: sortedData.map(item => item.value),
        outrosItems
    };
}

function drawChartProduto(dadosProduto) {
    var ctx = document.getElementById('chart_produto').getContext('2d');
    const processedData = processData(dadosProduto['produtos'], dadosProduto['valores']);
    const backgroundColors = generateRandomColors(processedData.data.length);
    outrosItemsProduto = processedData.outrosItems;

    var dataProduto = {
        labels: processedData.labels,
        datasets: [{
            data: processedData.data,
            backgroundColor: backgroundColors
        }]
    };

    chartProdutoInstance = new Chart(ctx, {
        type: 'doughnut', // Gráfico de Rosca
        data: dataProduto,
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Distribuição por produto'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            let value = context.raw;
                            let lines = [`${label}: ${value}`];
                            if (label === 'Outros' && outrosItemsProduto.length > 0) {
                                lines.push('Itens agrupados:');
                                outrosItemsProduto.forEach(item => {
                                    lines.push(`- ${item.label}: ${item.value}`);
                                });
                            }
                            return lines;
                        }
                    }
                }
            }
        }
    });
}

function drawChartEstagio(dadosEstagio) {
    var ctx = document.getElementById('chart_estagio').getContext('2d');
    var dataEstagio = {
        labels: ['Pré-reserva', 'Confirmado', 'Ficha Evento', 'Ordem de Serviço'],
        datasets: [{
            data: [
                dadosEstagio[0]['pre_reserva'],
                dadosEstagio[0]['confirmado'],
                dadosEstagio[0]['ficha_evento'],
                dadosEstagio[0]['ordem_servico']
            ],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        }]
    };

    chartEstagioInstance = new Chart(ctx, {
        type: 'doughnut', // Gráfico de Rosca
        data: dataEstagio,
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Distribuição por estágio'
                }
            }
        }
    });
}

function montar_agendas_refeicoes(relatorios_eventos, descritivo_refeicoes) {
    const calendarUIDescritivo = document.getElementById('agenda_descritivo');
    const calendarUIAgendaRefeicoes = document.getElementById('agenda_cozinha');

    const agenda_refeicoes = new FullCalendar.Calendar(calendarUIAgendaRefeicoes, {
        headerToolbar: {
            left: '',
            center: 'title',
        },

        eventOrderStrict: true,
        locale: 'pt-br',
        dayMaxEvents: 5,
        fixedWeekCount: false,
        height: 'parent',
        contentHeight: 'auto',
        handleWindowResize: true,
        navLinks: true,
        navLinkDayClick: function (date, jsEvent) {
            const agenda_descritivo_refeicoes = new FullCalendar.Calendar(calendarUIDescritivo, {
                headerToolbar: {
                    left: 'prev, today',
                    center: 'title',
                    right: 'next',
                },

                initialDate: date,
                duration: {days: 4},
                initialView: 'timeGrid',
                eventOrderStrict: true,
                locale: 'pt-br',
                allDaySlot: false,
                slotMinTime: '06:00:00',
                nowIndicator: true,
                slotDuration: '00:10:00',
                events: descritivo_refeicoes,
                eventClick: function (calEvent, jsEvent) {
                    $('#cliente').text(calEvent.event.title);
                    $('#refeicao').text(calEvent.event.extendedProps['refeicao']);
                    $('#adultos').text(calEvent.event.extendedProps['adultos']);
                    $('#criancas').text(calEvent.event.extendedProps['criancas']);
                    $('#monitores').text(calEvent.event.extendedProps['monitoria']);
                    $('#total').text(calEvent.event.extendedProps['total']);
                    $('#dialog').dialog('open');
                },
            })
            $('#div_agenda_descritivo').removeClass('none')
            agenda_descritivo_refeicoes.render()
            agenda_descritivo_refeicoes.setOption('locale', 'pt-br')
        },
        events: relatorios_eventos,
        eventClick: function (info) {
            console.log(info)
        }
    })

    agenda_refeicoes.render();
    agenda_refeicoes.setOption('locale', 'pt-br')
}