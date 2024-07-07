let chartProdutoInstance = null;
let chartEstagioInstance = null;
let outrosItemsProduto = [];
let outrosItemsEstagio = [];

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

function graficar_produto_estagio(mes_ano) {
    loading()
    $('#grafico_info_extra').removeClass('none')
    $('#relatorio_produtos .conteudo_grafico_painel_diretoria h4').text(`${mes_ano.split('/')[0]} de ${mes_ano.split('/')[1]}`)

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