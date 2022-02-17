
google.charts.load("current", {packages:["corechart"]});
//google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(drawChart2);
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

function pegarDadosGrafico2(){

    var mes = getNumeroMes($('#selecaoMes').val())
    var ano = getAno()

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'mes': mes, 'ano': ano},
        success: function (response){
            drawChart(response)
        }
    })
};

function pegarDadosGrafico3(){

    var id_professor = $('#selecaoProfessor').val()
    console.log(id_professor)

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_professor': id_professor},
        success: function (response){
            console.log(response)
        }
    })
};


// -------------------------- Gráfico 2 ---------------------------
function drawChart(dados) {
    var dadosMes = [['Atividade', 'Incidência'],]

    for (let i in dados['dados'][0]){
        var linha = [i, dados['dados'][0][i]];
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
