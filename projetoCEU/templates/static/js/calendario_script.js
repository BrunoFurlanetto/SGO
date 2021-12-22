const date = new Date();

const prevLastDay = new Date(
    date.getFullYear(),
    date.getMonth() - 1,
    0
).getDate();

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
      days += `<div class="today">${i}</div>`;
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

document.querySelector(".days").addEventListener("click", (event) => {
    /*console.log(date.getMonth() + 1);
    console.log(date.getFullYear());*/

    var selecionado = document.getElementsByClassName("selected");

    if (selecionado.length > 0){
        selecionado[0].classList.remove("selected");
    };

    if (event.target.classList.contains("next-date")){
        var divAntiga = event.target.classList[1];
        date.setMonth(date.getMonth() + 1);
        renderCalendar();
        var novaDiv = document.getElementsByClassName(divAntiga)
    }else if (event.target.classList.contains("prev-date")){
        var divAntiga = event.target.classList[1];
        date.setMonth(date.getMonth() - 1);
        renderCalendar();
        var novaDiv = document.getElementsByClassName(String(prevLastDay-(parseInt(divAntiga)-1)))
    }else{
        var divAntiga = event.target.classList[0];
        var novaDiv = document.getElementsByClassName(divAntiga)
    };

    if (novaDiv.length > 1){
        novaDiv[1].classList.add("selected");
    }else{
        novaDiv[0].classList.add("selected");
    };

});

renderCalendar();
