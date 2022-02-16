
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(drawChart2);
google.charts.setOnLoadCallback(drawChart3);

var listaDeDadosMes = []
var date = new Date()
var mesAtual = date.getMonth()
var anoAtual = date.getFullYear()

$.ajax({
    type: 'POST',
    url: '',
    headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
    data: {'mes': mesAtual, 'ano': anoAtual},
    success: function (response){
        tratarDados(response)
    }
})

var a = 4

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

function tratarDados(dados){
    var listaDeDadosMes = []

    for (let i in dados['dados'][0]){
        listaDeDadosMes.push([i, dados['dados'][0][i]])
    }

    drawChart();

}

function alterarMes(selecao){

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'ano': selecao.value},
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

function pegarDados(selecao){

    var mes = getNumeroMes(selecao.value)
    var ano = getAno()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'mes': mes, 'ano': ano},
        success: function (response){
            tratarDados(response)
        }
    })
};

// -------------------------- Gráfico 2 ---------------------------
function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Atividades');
    data.addColumn('number', 'Incidência');
    data.addRows(
        for (let i = 1; i < 5; i++){
            ['dfgad', i]
        }
    )

    var options = {
        height: 300,
        chartArea:{left: 50, top: 50, width:'100%', height: '100%'},
        pieHole: 0.4,
    };

    var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
    chart.draw(data, options);
};

// -------------------------- Gráfico 3 ---------------------------
function drawChart2() {

    var data = google.visualization.arrayToDataTable([
        ['Task', 'Hours per Day'],
        ['Work',     11],
        ['Eat',      2],
        ['Commute',  2],
        ['Watch TV', 2],
        ['Sleep',    7]
    ]);

    var options = {
        height: 300,
        chartArea:{left: 50, top: 50, width:'100%', height: '100%'},
    };

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
