const date_disponibilidade = new Date();

const renderCalendar_disponibilidade = () => {
  date_disponibilidade.setDate(1);

  const monthDays_disponibilidade = document.querySelector(".days-disponibilidade");

  const lastDay_disponibilidade = new Date(
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

  document.querySelector(".date-disponibilidade h1").innerHTML = months_disponibilidade[date.getMonth()];

  let data_disponibilidade = new Date();
  let dia_semana_disponibilidade = dias_disponibilidade[data_disponibilidade.getDay()];
  let dia_mes_disponibilidade = String(data_disponibilidade.getDate());
  let mes_disponibilidade = months[data_disponibilidade.getMonth()];
  let ano_disponibilidade = data_disponibilidade.getFullYear();
  document.querySelector(".date p").innerHTML = dia_semana_disponibilidade + ' ' + dia_mes_disponibilidade + ' ' + mes_disponibilidade + ' ' + ano_disponibilidade;

  let days_disponibilidade = "";

  for (let x = firstDayIndex_disponibilidade; x > 0; x--) {
    days_disponibilidade += `<div class="prev-date-disponibilidade ${x}">${prevLastDay_disponibilidade - x + 1}</div>`;
  }

  for (let i = 1; i <= lastDay_disponibilidade; i++) {
    if (
      i === new Date().getDate() &&
      date_disponibilidade.getMonth() === new Date().getMonth()
    ) {
      days_disponibilidade += `<div class="${i} today-disponibilidade">${i}</div>`;
    } else {
      days_disponibilidade += `<div class="${i}">${i}</div>`;
    }
  }

  for (let j = 1; j <= nextDays_disponibilidade; j++) {
    days_disponibilidade += `<div class="next-date-disponibilidade ${j}">${j}</div>`;
    monthDays_disponibilidade.innerHTML = days_disponibilidade;
  }
};

document.querySelector(".prev-disponibilidade").addEventListener("click", () => {
  date_disponibilidade.setMonth(date_disponibilidade.getMonth() - 1);
  renderCalendar_disponibilidade();
});

document.querySelector(".next-disponibilidade").addEventListener("click", () => {
  date_disponibilidade.setMonth(date_disponibilidade.getMonth() + 1);
  renderCalendar_disponibilidade();
});

document.querySelector(".days-disponibilidade").addEventListener("click", (event) => {
    console.log('Foi')
    if (event.target.classList[0] != 'days-disponibilidade'){
        event.target.classList.add('selected-disponibilidade')
    }
})

renderCalendar_disponibilidade();
