function montar_agenda_cozinha(eventos, permissao_adicao_relatorios) {
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
        navLinkDayClick: function (date, jsEvent) {
            const data = date.toISOString().split('T')[0];
            window.location.href = `/cozinha/visualizar/relatorio/dia/${data}`
        },
        events: eventos,
    })

    calendar.render();
    calendar.setOption('locale', 'pt-br')
}