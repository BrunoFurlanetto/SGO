function montar_agenda_cozinha(eventos) {
    const calendarUI = document.getElementById('agenda_cozinha');
    const calendar = new FullCalendar.Calendar(calendarUI, {
        headerToolbar: {
            left: '',
            center: 'title',
        },

        eventOrderStrict: true,
        locale: 'pt-br',
        dayMaxEvents: 5,
        fixedWeekCount: false,
        height: 'parent',
        contentHeight: 'auto',
        handleWindowResize: true,
        navLinks: true,
        eventDayClick: true,
        navLinkDayClick: function (date, jsEvent) {
            const data = moment(date).format('YYYY-MM-DD')
            window.location.href = `/cozinha/verificar_relatorios_dia/${data}`
        },
        events: eventos,
        eventClick: function (info) {
            console.log(info)
        }
    })

    calendar.render();
    calendar.setOption('locale', 'pt-br')
}