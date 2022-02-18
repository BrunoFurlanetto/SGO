
google.charts.load("current", {packages:["corechart"]});
//google.charts.setOnLoadCallback(drawChart);
//google.charts.setOnLoadCallback(drawChart2);
google.charts.setOnLoadCallback(drawChart3);

function getAno(){
    return parseInt($('#selecaoAno').val())
}

function getNumeroMes(mes){
    var meses = ['Janeiro', 'Fevereiro',
    'Março', 'Abril', 'Maio',
    'Junho','Julho', 'Agosto',
    'Setembro', 'Outrubro',
    'Novembro', 'Dezembro']

    return meses.indexOf(mes) + 1
}

function alterarMes(selecao){

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'ano': selecao.value, 'grafico': 0},
        success: function(response){
            var meses = response.split(',')
            $('#selecaoMes').empty()
            $('#selecaoMes').append('<option selected></option>')
            for (let i in meses){
                $('#selecaoMes').append('<option>' + meses[i] + '</option>')
            }
        }
    })
};

function pegarDadosGrafico2(){

    var mes = getNumeroMes($('#selecaoMes').val())
    var ano = getAno()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'mes': mes, 'ano': ano, 'grafico': 2},
        success: function (response){
            console.log(response)
            drawChart(response)
        }
    })
};

// -------------------------- Gráfico 2 ---------------------------
function drawChart(dados) {
    var dadosMes = [['Atividade', 'Incidência'],]

    for (let i in dados['dados']){
        var linha = [i, dados['dados'][i]];
        dadosMes.push(linha)
    }

    var options = {
        height: 300,
        chartArea:{left: 50, top: 50, width:'100%', height: '100%'},
        pieHole: 0.4,
    };

    var data = new google.visualization.arrayToDataTable(dadosMes);
    var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
    chart.draw(data, options);
};

function pegarDadosGrafico3(){

    var id_professor = $('#selecaoProfessor').val()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_professor': id_professor, 'grafico': 3},
        success: function (response){
            console.log(response)
            drawChart2(response)
        }
    })
};

// -------------------------- Gráfico 3 ---------------------------
function drawChart2(dados) {

    var dadosProfessor = [['Atividade', 'Incidência'],]

    for (let i in dados['dados']){
        var linha = [i, dados['dados'][i]];
        dadosProfessor.push(linha)
    }

    var options = {
        height: 300,
        chartArea:{left: 50, top: 50, width:'100%', height: '100%'},
    };

    var data = new google.visualization.arrayToDataTable(dadosProfessor);
    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options)

};

// -------------------------- Gráfico 4 ---------------------------
function drawChart3() {
    var data = google.visualization.arrayToDataTable([
        ['Year', 'Sales', 'Expenses'],
        ['2004',  1000,      400],
        ['2005',  1170,      460],
        ['2006',  660,       1120],
        ['2007',  1030,      540]
    ]);

    var options = {
        chartArea:{left: 40, top: 20, width:'100%', height:'80%'},
        title: 'Gráfico 4',
        curveType: 'function',
        legend: { position: 'bottom' }
    };

    var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

    chart.draw(data, options);
};
