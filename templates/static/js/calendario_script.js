const date = new Date();
const queryString = window.location.search
const url = window.location.href
const urlParams = new URLSearchParams(queryString)
let data_relatorios = new Date()

if (url.indexOf("data_relatorios=") !== -1) {
    let data_url = urlParams.get('data_relatorios').split('-')
    data_relatorios = new Date(data_url[0], data_url[1] - 1, data_url[2]);
}

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
    let days = "";
    document.querySelector(".date p").innerHTML = dia_semana + ' ' + dia_mes + ' ' + mes + ' ' + ano;

    for (let x = firstDayIndex; x > 0; x--) {
        days += `<div class="prev-date ${x}">${prevLastDay - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDay; i++) {
        if (i === new Date().getDate() && date.getMonth() === new Date().getMonth()) {
            days += `<div class="${i} today">${i}</div>`;
        } else if (i === data_relatorios.getDate() && data_relatorios.getMonth() == date.getMonth()) {
            days += `<div class="${i} selected">${i}</div>`;
        } else {
            days += `<div class="${i}">${i}</div>`;
        }
    }

    if (nextDays !== 0) {
        for (let j = 1; j <= nextDays; j++) {
            days += `<div class="next-date ${j}">${j}</div>`;
            monthDays.innerHTML = days;
        }
    } else {
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

jQuery(document).ready(function ($) {
    $(".clickable-row").click(function () {
        window.location = $(this).data("href");
    });
});

// ----------------- Parte do script que é responsável pela interação calendário -> tabela dashboard -------------------
document.querySelector(".days").addEventListener("click", (event) => {
    var novaDiv
    var mes_selecionado
    var ano_selecionado
    var dia_selecionado
    var data_selecionada
    var divAntiga;
    /* Constante necessária para saber o último dia do mês anterior */
    const prevLastDay = new Date(
        date.getFullYear(),
        date.getMonth(),
        0
    ).getDate();

    /* Tanto a variável quanto o if a seguir são para selecionar a div com o selected antigo */
    /* e remover para que não fique com duas div's selecionadas */
    var selecionado = document.getElementsByClassName("selected");

    if (selecionado.length > 0) {
        selecionado[0].classList.remove("selected");
    }

    /* Testes para conseguir adcionar a class 'selected' na div certa, já que tem diferença */
    /* entre as div's do mês mostrado pelo calendário e as div's do próximo mês e do anterior */
    if (event.target.classList.contains("next-date")) {
        divAntiga = event.target.classList[1];
        /* Pulando pro próximo mês antes de fazer a seleção do dia */
        date.setMonth(date.getMonth() + 1);
        renderCalendar();
        /* Pegando o valor da div antiga pra conseguir selecionar o dia certo na nova div */
        novaDiv = document.getElementsByClassName(divAntiga);
        /* Pegando os valores do dia, mês e ano pra poder retornar a data completa */
        /* Será usada com o BD */
        mes_selecionado = date.getMonth();
        ano_selecionado = date.getFullYear();
        dia_selecionado = event.target.classList[1];
        data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado)
    } else if (event.target.classList.contains("prev-date")) {
        divAntiga = event.target.classList[1];
        /* Voltando o mês antes de fazer a seleção do dia */
        date.setMonth(date.getMonth() - 1);
        renderCalendar();
        /* Fazendo a conta utilizando a div antiga pra poder selecionar a div certa */
        novaDiv = document.getElementsByClassName(String(prevLastDay - (parseInt(divAntiga) - 1)));
        /* Pegando os valores do dia, mês e ano pra poder retornar a data completa */
        /* Será usada com o BD */
        mes_selecionado = date.getMonth();
        ano_selecionado = date.getFullYear();
        dia_selecionado = novaDiv[0].classList;
        data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);
    } else {
        /* Caso que a seleção é dentro do mês que está sendo mostrados */
        divAntiga = event.target.classList[0];
        novaDiv = document.getElementsByClassName(divAntiga);
        /* Pegando os valores do dia, mês e ano pra poder retornar a data completa */
        /* Será usada com o BD */
        mes_selecionado = date.getMonth();
        ano_selecionado = date.getFullYear();
        dia_selecionado = event.target.classList[0];
        data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);
    }

    completar_data(data_selecionada).then(() => {
        $('#form_data_relatorios').submit()
    })

});

renderCalendar();

async function completar_data(data_selecionada) {
    $('#data_relatorios').val(moment(data_selecionada).format('YYYY-MM-DD'))
}