const date_disponibilidade_acampamento = new Date();

const renderCalendar_disponibilidade_acampamento = () => {
    date_disponibilidade_acampamento.setDate(1);

    const monthDays_disponibilidade_acampamento = document.querySelector(".days-disponibilidade-acampamento");

    var lastDay_disponibilidade_acampamento = new Date(
        date_disponibilidade_acampamento.getFullYear(),
        date_disponibilidade_acampamento.getMonth() + 1,
        0
    ).getDate();

    const prevLastDay_disponibilidade_acampamento = new Date(
        date_disponibilidade_acampamento.getFullYear(),
        date_disponibilidade_acampamento.getMonth(),
        0
    ).getDate();

    const firstDayIndex_disponibilidade_acampamento = date_disponibilidade_acampamento.getDay();

    const lastDayIndex_disponibilidade_acampamento = new Date(
        date_disponibilidade_acampamento.getFullYear(),
        date_disponibilidade_acampamento.getMonth() + 1,
        0
    ).getDay();

    const nextDays_disponibilidade_acampamento = 7 - lastDayIndex_disponibilidade_acampamento - 1;

    const months_disponibilidade_acampamento = [
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

    const dias_disponibilidade_acampamento = [
        "Dom",
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sab",
    ];

    if (document.getElementsByClassName("fa-angle-left").length > 0){
        document.querySelector(".date-disponibilidade-acampamento h1").innerHTML = months_disponibilidade_acampamento[date_disponibilidade_acampamento.getMonth()];
    } else {
        document.querySelector(".date-disponibilidade-acampamento h1").innerHTML = months_disponibilidade_acampamento[date_disponibilidade_acampamento.getMonth() + 1];
    }

    let days_disponibilidade_acampamento = "";

    for (let x = firstDayIndex_disponibilidade_acampamento; x > 0; x--) {
        days_disponibilidade_acampamento += `<div class="prev-date-disponibilidade-acampamento ${x}">${prevLastDay_disponibilidade_acampamento - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDay_disponibilidade_acampamento; i++) {
        if (
            i === new Date().getDate() &&
            date_disponibilidade_acampamento.getMonth() === new Date().getMonth()
        ) {
            days_disponibilidade_acampamento += `<div id='${i}' class="$day {i} acampamento today-disponibilidade-acampamento">${i}</div>`;
        } else {
            days_disponibilidade_acampamento += `<div id='${i}' class="day ${i} acampamento">${i}</div>`;
        }
    }

    if(nextDays_disponibilidade_acampamento !== 0){
        for (let j = 1; j <= nextDays_disponibilidade_acampamento; j++) {
            days_disponibilidade_acampamento += `<div class="next-date-disponibilidade-acampamento ${j}">${j}</div>`;
            monthDays_disponibilidade_acampamento.innerHTML = days_disponibilidade_acampamento;
        }
    }else{
        monthDays_disponibilidade_acampamento.innerHTML = days_disponibilidade_acampamento;
    }

};

 if (document.getElementsByClassName("fa-angle-left").length > 0){
    document.querySelector(".prev-disponibilidade-acampamento").addEventListener("click", () => {
        date_disponibilidade_acampamento.setMonth(date_disponibilidade_acampamento.getMonth() - 1);
        renderCalendar_disponibilidade_acampamento();
    });

    document.querySelector(".next-disponibilidade-acampamento").addEventListener("click", () => {
        date_disponibilidade_acampamento.setMonth(date_disponibilidade_acampamento.getMonth() + 1);
        renderCalendar_disponibilidade_acampamento();
    });
}

document.querySelector(".days-disponibilidade-acampamento").addEventListener("click", (event) => {

    if (event.target.classList[0] !== 'days-disponibilidade-acampamento'){
        event.target.classList.toggle('selected-disponibilidade-acampamento')

        var mes_selecionado = date_disponibilidade_acampamento.getMonth();
        var ano_selecionado = date_disponibilidade_acampamento.getFullYear();
        var dia_selecionado = event.target.classList[0];
        var data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);

    }

})

function selecionar_acampamento(){
    let lastDay_disponibilidade_acampamento = new Date(
        date_disponibilidade_acampamento.getFullYear(),
        date_disponibilidade_acampamento.getMonth() + 1,
        0
    ).getDate();
    $('.acampamento').toggleClass('selected-disponibilidade-acampamento')

}

function enviar_acampamento(){
    var dias_selecionados = document.getElementsByClassName('selected-disponibilidade-acampamento')
    var mes_selecionado = date_disponibilidade_acampamento.getMonth();
    var ano_selecionado = date_disponibilidade_acampamento.getFullYear();
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
    }

}

renderCalendar_disponibilidade_acampamento();
