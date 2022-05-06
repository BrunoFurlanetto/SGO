const date_disponibilidade_hotelaria = new Date();

const renderCalendar_disponibilidade_hotelaria = () => {
    date_disponibilidade_hotelaria.setDate(1);

    const monthDays_disponibilidade_hotelaria = document.querySelector(".days-disponibilidade-hotelaria");

    var lastDay_disponibilidade_hotelaria = new Date(
        date_disponibilidade_hotelaria.getFullYear(),
        date_disponibilidade_hotelaria.getMonth() + 1,
        0
    ).getDate();

    const prevLastDay_disponibilidade_hotelaria = new Date(
        date_disponibilidade_hotelaria.getFullYear(),
        date_disponibilidade_hotelaria.getMonth(),
        0
    ).getDate();

    const firstDayIndex_disponibilidade_hotelaria = date_disponibilidade_hotelaria.getDay();

    const lastDayIndex_disponibilidade_hotelaria = new Date(
        date_disponibilidade_hotelaria.getFullYear(),
        date_disponibilidade_hotelaria.getMonth() + 1,
        0
    ).getDay();

    const nextDays_disponibilidade_hotelaria = 7 - lastDayIndex_disponibilidade_hotelaria - 1;

    const months_disponibilidade_hotelaria = [
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

    const dias_disponibilidade_hotelaria = [
        "Dom",
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sab",
    ];

    if (document.getElementsByClassName("fa-angle-left").length > 0){
        document.querySelector(".date-disponibilidade-hotelaria h1").innerHTML = months_disponibilidade_hotelaria[date_disponibilidade_hotelaria.getMonth()];
    } else {
        document.querySelector(".date-disponibilidade-hotelaria h1").innerHTML = months_disponibilidade_hotelaria[date_disponibilidade_hotelaria.getMonth() + 1];
    }

    let days_disponibilidade_hotelaria = "";

    for (let x = firstDayIndex_disponibilidade_hotelaria; x > 0; x--) {
        days_disponibilidade_hotelaria += `<div class="prev-date-disponibilidade-hotelaria ${x}">${prevLastDay_disponibilidade_hotelaria - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDay_disponibilidade_hotelaria; i++) {
        if (
            i === new Date().getDate() &&
            date_disponibilidade_hotelaria.getMonth() === new Date().getMonth()
        ) {
            days_disponibilidade_hotelaria += `<div id='${i}' class="$day {i} hotelaria today-disponibilidade-hotelaria">${i}</div>`;
        } else {
            days_disponibilidade_hotelaria += `<div id='${i}' class="day ${i} hotelaria">${i}</div>`;
        }
    }

    if(nextDays_disponibilidade_hotelaria !== 0){
        for (let j = 1; j <= nextDays_disponibilidade_hotelaria; j++) {
            days_disponibilidade_hotelaria += `<div class="next-date-disponibilidade-hotelaria ${j}">${j}</div>`;
            monthDays_disponibilidade_hotelaria.innerHTML = days_disponibilidade_hotelaria;
        }
    }else{
        monthDays_disponibilidade_hotelaria.innerHTML = days_disponibilidade_hotelaria;
    }

};

 if (document.getElementsByClassName("fa-angle-left").length > 0){
    document.querySelector(".prev-disponibilidade-hotelaria").addEventListener("click", () => {
        date_disponibilidade_hotelaria.setMonth(date_disponibilidade_hotelaria.getMonth() - 1);
        renderCalendar_disponibilidade_hotelaria();
    });

    document.querySelector(".next-disponibilidade-hotelaria").addEventListener("click", () => {
        date_disponibilidade_hotelaria.setMonth(date_disponibilidade_hotelaria.getMonth() + 1);
        renderCalendar_disponibilidade_hotelaria();
    });
}

document.querySelector(".days-disponibilidade-hotelaria").addEventListener("click", (event) => {

    if (event.target.classList[0] !== 'days-disponibilidade-hotelaria'){
        event.target.classList.toggle('selected-disponibilidade-hotelaria')

        var mes_selecionado = date_disponibilidade_hotelaria.getMonth();
        var ano_selecionado = date_disponibilidade_hotelaria.getFullYear();
        var dia_selecionado = event.target.classList[0];
        var data_selecionada = new Date(ano_selecionado, mes_selecionado, dia_selecionado);

    }

})

function selecionar_hotelaria(){
    let lastDay_disponibilidade_hotelaria = new Date(
        date_disponibilidade_hotelaria.getFullYear(),
        date_disponibilidade_hotelaria.getMonth() + 1,
        0
    ).getDate();
    $('.hotelaria').toggleClass('selected-disponibilidade-hotelaria')

}

function enviar_hotelaria(){
    let dias_selecionados = document.getElementsByClassName('selected-disponibilidade-hotelaria')
    let mes_selecionado = date_disponibilidade_hotelaria.getMonth();
    let ano_selecionado = date_disponibilidade_hotelaria.getFullYear();
    let todas_as_datas_list = [];

    if (dias_selecionados[0]){
        for (let i = 0; i < dias_selecionados.length; i++){
            let datas_selecionadas = new Date(ano_selecionado, mes_selecionado, dias_selecionados[i].textContent);
            todas_as_datas_list.push(datas_selecionadas.toLocaleDateString('pt-BR'))
        };

        let todas_as_datas = todas_as_datas_list.join(', ')
        $('#entrada').val(todas_as_datas)
        document.getElementById('enviando_hotelaria').click();

    } else {
        alert('Selecione algum dia disponivel para enviar')
    }

}

jQuery('document').ready(function() {
  jQuery('#hotelaria').submit(function() {
      let dados = jQuery(this).serialize();
      let url = $(this).attr('action');

      $.ajax({
          url: url,
          headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
          type: "POST",
          data: dados,
          success: function (response) {
              let div_conteudo = $('.conteudo-disponibilidade-hotelaria')

              div_conteudo.empty()
              div_conteudo.append('<h5 style="display: flex; align-items: center"><center>Disponibilidade para a hotelaria enviado com sucesso!!</center></h5>')
              div_conteudo.addClass('texto-final')
          }
      })
      return false;
  })
})

renderCalendar_disponibilidade_hotelaria();
