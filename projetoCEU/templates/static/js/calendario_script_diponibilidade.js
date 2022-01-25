const date_disponibilidade = new Date();

const renderCalendar_disponibilidade = () => {
    date_disponibilidade.setDate(1);

    const monthDays_disponibilidade = document.querySelector(".days-disponibilidade");

    var lastDay_disponibilidade = new Date(
        date_disponibilidade.getFullYear(),
        date_disponibilidade.getMonth() + 1,
        0
    ).getDate();

    const prevLastDay_disponibilidade = new Date(
        date_disponibilidade.getFullYear(),
        date_disponibilidade.getMonth(),
        0
    ).getDate();

    const firstDayIndex_disponibilidade = date_disponibilidade.getDay();

    const lastDayIndex_disponibilidade = new Date(
        date_disponibilidade.getFullYear(),
        date_disponibilidade.getMonth() + 1,
        0
    ).getDay();

    const nextDays_disponibilidade = 7 - lastDayIndex_disponibilidade - 1;

    const months_disponibilidade = [
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

    const dias_disponibilidade = [
        "Dom",
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sab",
    ];

    if (document.getElementsByClassName("fa-angle-left").length > 0){
        document.querySelector(".date-disponibilidade h1").innerHTML = months_disponibilidade[date_disponibilidade.getMonth()];
    } else {
        document.querySelector(".date-disponibilidade h1").innerHTML = months_disponibilidade[date_disponibilidade.getMonth() + 1];
    }

    let days_disponibilidade = "";

    for (let x = firstDayIndex_disponibilidade; x > 0; x--) {
        days_disponibilidade += `<div class="prev-date-disponibilidade ${x}">${prevLastDay_disponibilidade - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDay_disponibilidade; i++) {
        if (
            i === new Date().getDate() &&
            date_disponibilidade.getMonth() === new Date().getMonth()
        ) {
            days_disponibilidade += `<div id='${i}' class="$day {i} today-disponibilidade">${i}</div>`;
        } else {
            days_disponibilidade += `<div id='${i}' class="day ${i}">${i}</div>`;
        }
    }

    for (let j = 1; j <= nextDays_disponibilidade; j++) {
        days_disponibilidade += `<div class="next-date-disponibilidade ${j}">${j}</div>`;
        monthDays_disponibilidade.innerHTML = days_disponibilidade;
    }
};

 if (document.getElementsByClassName("fa-angle-left").length > 0){
    document.querySelector(".prev-disponibilidade").addEventListener("click", () => {
        date_disponibilidade.setMonth(date_disponibilidade.getMonth() - 1);
        renderCalendar_disponibilidade();
    });

    document.querySelector(".next-disponibilidade").addEventListener("click", () => {
        date_disponibilidade.setMonth(date_disponibilidade.getMonth() + 1);
        renderCalendar_disponibilidade();
    });
}

document.querySelector(".days-disponibilidade").addEventListener("click", (event) => {

    if (event.target.classList[0] != 'days-disponibilidade'){
        event.target.classList.toggle('selected-disponibilidade')

        var mes_selecionado = date_disponibilidade.getMonth();
        var ano_selecionado = date_disponibilidade.getFullYear();
        var dia_selecionado = event.target.classList[0];
        var data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);

    }

})

function selecionar(){
    var lastDay_disponibilidade = new Date(
        date_disponibilidade.getFullYear(),
        date_disponibilidade.getMonth() + 1,
        0
    ).getDate();

    for (let i = 1; i <= lastDay_disponibilidade; i++){
        var todos_dias = document.getElementById(i)
        todos_dias.classList.toggle('selected-disponibilidade')
    }
};

function enviar(){
    var dias_selecionados = document.getElementsByClassName('selected-disponibilidade')
    var mes_selecionado = date_disponibilidade.getMonth();
    var ano_selecionado = date_disponibilidade.getFullYear();
    var todas_as_datas_list = []
    var token = document.getElementById('token')

    console.log(dias_selecionados[0])

    if (dias_selecionados[0]){
        for (let i = 0; i < dias_selecionados.length; i++){
            var datas_selecionadas = new Date(ano_selecionado, mes_selecionado, dias_selecionados[i].textContent);
            todas_as_datas_list.push(datas_selecionadas.toLocaleDateString('pt-BR'))
        };

        var todas_as_datas = todas_as_datas_list.join(', ')
        $('#entrada').val(todas_as_datas)
        document.getElementById('enviando').click();

    } else {
        alert('Selecione algum dia disponivel para enviar')
    };

};

renderCalendar_disponibilidade();
