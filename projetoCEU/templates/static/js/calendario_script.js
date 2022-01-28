const date = new Date();

const months = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
];

const renderCalendar = () => {
    date.setDate(1);

    const monthDays = document.querySelector(".days");

    const lastDay = new Date(
        date.getFullYear(),
        date.getMonth() + 1,
        0
    ).getDate();

    const prevLastDay = new Date(
        date.getFullYear(),
        date.getMonth(),
        0
    ).getDate();

    const firstDayIndex = date.getDay();

    const lastDayIndex = new Date(
        date.getFullYear(),
        date.getMonth() + 1,
        0
    ).getDay();

    const nextDays = 7 - lastDayIndex - 1;

    const months = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ];

    const dias = [
        "Dom",
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sab",
    ];

    document.querySelector(".date h1").innerHTML = months[date.getMonth()];

    let data = new Date();
    let dia_semana = dias[data.getDay()];
    let dia_mes = String(data.getDate());
    let mes = months[data.getMonth()];
    let ano = data.getFullYear();
    document.querySelector(".date p").innerHTML = dia_semana + ' ' + dia_mes + ' ' + mes + ' ' + ano;

    let days = "";

    for (let x = firstDayIndex; x > 0; x--) {
        days += `<div class="prev-date ${x}">${prevLastDay - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDay; i++) {
        if (
              i === new Date().getDate() &&
              date.getMonth() === new Date().getMonth()
        ) {
              days += `<div class="${i} today">${i}</div>`;
        } else {
              days += `<div class="${i}">${i}</div>`;
        }
    }

    for (let j = 1; j <= nextDays; j++) {
        days += `<div class="next-date ${j}">${j}</div>`;
        monthDays.innerHTML = days;
    }
};

document.querySelector(".prev").addEventListener("click", () => {
    date.setMonth(date.getMonth() - 1);
    renderCalendar();
});

document.querySelector(".next").addEventListener("click", () => {
    date.setMonth(date.getMonth() + 1);
    renderCalendar();
});

jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});

document.querySelector(".days").addEventListener("click", (event) => {

    /* Constante necessária para saber o último dia do mês anterior */
    const prevLastDay = new Date(
        date.getFullYear(),
        date.getMonth(),
        0
    ).getDate();

    /* Tanto a variável quanto o if a seguir são para selecionar a div com o selected antigo */
    /* e remover para que não fique com duas div's selecionadas */
    var selecionado = document.getElementsByClassName("selected");

    if (selecionado.length > 0){
        selecionado[0].classList.remove("selected");
    };

    /* Testes para conseguir adcionar a class 'selected' na div certa, já que tem diferença */
    /* entre as div's do mês mostrado pelo calendário e as div's do próximo mês e do anterior */
    if (event.target.classList.contains("next-date")){
        var divAntiga = event.target.classList[1];
        /* Pulando pro próximo mês antes de fazer a seleção do dia */
        date.setMonth(date.getMonth() + 1);
        renderCalendar();
        /* Pegando o valor da div antiga pra conseguir selecionar o dia certo na nova div */
        var novaDiv = document.getElementsByClassName(divAntiga);
        /* Pegando os valores do dia, mês e ano pra poder retornar a data completa */
        /* Será usada com o BD */
        var mes_selecionado = date.getMonth();
        var ano_selecionado = date.getFullYear();
        var dia_selecionado = event.target.classList[1];
        var data_salacionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado)
    }else if (event.target.classList.contains("prev-date")){
        var divAntiga = event.target.classList[1];
        /* Voltando o mês antes de fazer a seleção do dia */
        date.setMonth(date.getMonth() - 1);
        renderCalendar();
        /* Fazendo a conta utilizando a div antiga pra poder selecionar a div certa */
        var novaDiv = document.getElementsByClassName(String(prevLastDay-(parseInt(divAntiga)-1)));
        /* Pegando os valores do dia, mês e ano pra poder retornar a data completa */
        /* Será usada com o BD */
        var mes_selecionado = date.getMonth();
        var ano_selecionado = date.getFullYear();
        var dia_selecionado = novaDiv[0].classList;
        var data_salacionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);
    }else{
        /* Caso que a seleção é dentro do mês que está sendo mostrados */
        var divAntiga = event.target.classList[0];
        var novaDiv = document.getElementsByClassName(divAntiga);
        /* Pegando os valores do dia, mês e ano pra poder retornar a data completa */
        /* Será usada com o BD */
        var mes_selecionado = date.getMonth();
        var ano_selecionado = date.getFullYear();
        var dia_selecionado = event.target.classList[0];
        var data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);
    };

    /* Adcionando a class 'selected' na posição certa */
    if (novaDiv.length > 1){
        novaDiv[1].classList.add("selected");
    }else{
        novaDiv[0].classList.add("selected");
    };

    $.ajax({
        type: 'POST',
        url: '',
        data: {'data_selecionada': data_selecionada.toLocaleDateString('fr-CA')},
        success: function(response){
            if (response[1] == ']'){
                $('#dados').empty();
                var novaLinha = document.createElement('tr')
                novaLinha.id = 'dados0'
                $('#dados').append(novaLinha)
                var mensagem = "<td colspan='5'>"+'Sem ordens de serviço para o dia '+ data_selecionada.toLocaleDateString('pt-BR') +'</td>'
                $('#dados0').append(mensagem)
                $('h5').empty();
                $('h5').append('Ordens de serviço do dia: ' + data_selecionada.toLocaleDateString('pt-BR'))
                return
            };
            var ids = [];
            var tipos = [];
            var instituicoes = [];
            var coordenadores = [];
            var equipe = [];
            var dados = response.split('][')

            var temp = dados[0].split(',')
            for (var j in temp){
                ids.push(temp[j].slice(1).trim())
            };

            temp = dados[1].split(',')
            for (var j in temp){
                tipos.push(temp[j].slice(7, -1))
            };

            var temp = dados[2].split(',')
            for (var j in temp){
                instituicoes.push(temp[j].trim().slice(1, -1))
            };
            temp = dados[3].split(',')
            for (var j in temp){
                coordenadores.push(temp[j].slice(14, -1).trim())
            };
            temp = dados[4].split(',')
            var temp2 = 0
            for (var i in tipos){
                var equipe_i = []
                for (var j = temp2; j < temp2+3; j++){
                    equipe_i.push(temp[j].slice(14, -1).replace('>', '').trim())
            };
            equipe.push(equipe_i)
            temp2 += 3
            };

            $('#dados').empty();
            for (var key = 0; key < tipos.length; key++){
                var novaLinha = `<tr id='dados${key}' class='clickable-row' data-href="/ordem-de-servico/${ids[key]}"></>`
                $('#dados').append(novaLinha)
                var script_tag = document.createElement('script')
                script_tag.text = 'jQuery(document).ready(function($){$(".clickable-row").click(function(){window.location = $(this).data("href");});});'
                $('#dados').append(script_tag)

                var tipo = '<td>'+tipos[key]+'</td>';
                var instituicao = '<td>'+ instituicoes[key] +'</td>';
                var coordenador = '<td>'+coordenadores[key]+'</td>';
                var equipe_j = new String();
                equipe_j = coordenadores[key]
                if (equipe[key][0] != ''){
                    equipe_j = equipe_j.concat(', ', equipe[key].join(', ').replace(/,(\s+)?$/, ''))
                };
                equipe_mostrar = '<td>' + equipe_j + '</td>';
                var data_atendimento = '<td>'+data_selecionada.getDate() + ' de ' + months[data_selecionada.getMonth()] + ' de ' + data_selecionada.getFullYear()+'</td>';
                $('#dados'+key).append(tipo, instituicao, coordenador, equipe_mostrar, data_atendimento);
                $('h5').empty();
                $('h5').append('Ordens de serviço do dia: ' + data_selecionada.toLocaleDateString('pt-BR'))
            }
        }
    });
});

renderCalendar();
