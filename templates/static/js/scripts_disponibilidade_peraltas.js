async function adicionar_disponibilidade(infos, eventos_intervalo, id_monitor, id_enfermeira, dia_adicionado, hoje_mais_30, coordenador, coordenador_hotelaria, coodenador_acampamento) {
    function teste_escalacao() {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'GET',
                url: '/escala/disponibilidade_peraltas/verificar_dias_hospedagem/',
                headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                data: {'data': dia_adicionado},
                success: function (response) {
                    resolve(response)
                },
                error: function (error) {
                    reject(error)
                }
            })
        })
    }


    let ids_monitor = []
    let ids_enfermeira = []
    const hoje = new Date(Date.now())

    if (!coordenador) {
        if (hoje.getDate() > 15 && moment(dia_adicionado).month() === hoje.getMonth() + 1) return false

        if (dia_adicionado < hoje_mais_30) return false

        if (moment(dia_adicionado).month() > hoje.getMonth() + 4) return false
    }

    if (coordenador_hotelaria && !coodenador_acampamento) {
        const adicao = await teste_escalacao()

        if (!adicao['hospedagem']) return adicao['hospedagem']
    }

    let eventos_dia = eventos_intervalo.filter((event) => {
        if (moment(event.start).format('YYYY-MM-DD') === dia_adicionado) {

            return event
        }
    })

    if (id_monitor !== undefined) {
        if (eventos_dia.length > 1) {
            ids_monitor = eventos_dia.filter((evento) => {
                if (evento.extendedProps['id_monitor'] === id_monitor) {
                    return evento
                }
            })
        }

        return ids_monitor.length <= 1;
    }

    if (id_enfermeira !== undefined) {
        if (eventos_dia.length > 1) {
            ids_enfermeira = eventos_dia.filter((evento) => {
                if (evento.extendedProps['id_enfermeira'] === id_enfermeira) {
                    return evento
                }
            })
        }

        return ids_enfermeira.length <= 1;
    }
}

function montar_disponibilidades(disponibilidade, coordenador_acampamento, coordenador_hotelaria) {
    const monitores = document.getElementById('nomes_monitores')
    const hoje = new Date(Date.now())
    const data_mais_30 = moment(hoje).add(30, 'days').format('YYYY-MM-DD')
    const coordenacao_hotelaria = coordenador_hotelaria === 'True'
    const coordenacao_acampamento = coordenador_acampamento === 'True'
    let coordena = false

    if (coordenacao_hotelaria || coordenacao_acampamento) coordena = true

    new FullCalendar.Draggable(monitores, {
        itemSelector: '.card-monitor',
    })

    if (!coordena) {
        $(document).ready(function () {
            $('button.fc-prev-button').prop('disabled', true)
        })
    }

    function onChangeMonth(coordenacao) {
        if (!coordenacao) {
            if (moment(calendar.currentData.currentDate).month() !== moment(hoje).month()) {
                $('button.fc-prev-button').prop('disabled', false)
            } else {
                $('button.fc-prev-button').prop('disabled', true)
            }
        } else {
            $('button.fc-prev-button').prop('disabled', false)
        }
    }

    let calendarUI = document.getElementById('calendario_escala');
    let calendar = new FullCalendar.Calendar(calendarUI, {

        headerToolbar: {
            left: '',
            center: 'title',
            right: 'prev, next'
        },

        customButtons: {
            prev: {
                text: 'Voltar',
                click: function () {
                    calendar.prev();
                    onChangeMonth(coordena);
                },
            },

            next: {
                text: 'Avançar',
                click: function () {
                    calendar.next();
                    onChangeMonth(coordena);
                }
            },
        },

        dayMaxEvents: 3,
        editable: true,
        droppable: true,
        eventOrderStrict: true,
        fixedWeekCount: false,
        locale: 'pt-br',
        initialDate: moment(new Date(Date.now())).add(30, 'days').format('YYYY-MM-DD'),
        events: disponibilidade,
        height: 'parent',
        contentHeight: 'auto',
        handleWindowResize: true,

        dayCellDidMount: function (info) {
            if (!coordena) {
                if (moment(info.date).format('YYYY-MM-DD') < data_mais_30) {
                    info.el.classList.add('not_selected')
                }

                if (hoje.getDate() > 15 && info.date.getMonth() === hoje.getMonth() + 1) {
                    info.el.classList.add('not_selected')
                }

                if (hoje.getDate() > 15 && info.date.getMonth() > hoje.getMonth() + 4) {
                    info.el.classList.add('not_selected')
                }
            }
        },

        datesSet: function () {
            const cells = document.querySelectorAll('#calendario_escala .fc-day.fc-day')
            $('.container_loading').removeClass('none')

            if (!coordena) {
                cells.forEach(function (cell) {
                    if (moment(cell.getAttribute('data-date')).format('YYYY-MM-DD') < data_mais_30) {
                        cell.classList.add('not_selected')
                    }

                    if (hoje.getDate() > 15 && moment(cell.getAttribute('data-date')).month() === hoje.getMonth() + 1) {
                        cell.classList.add('not_selected')
                    }

                    if (hoje.getDate() > 15 && moment(cell.getAttribute('data-date')).month() > hoje.getMonth() + 4) {
                        cell.classList.add('not_selected')
                    }
                })

            }

            setTimeout(() => {
                $('.container_loading').addClass('none')
            }, 500)

            if (coordenacao_hotelaria && !coordenacao_acampamento) {

                cells.forEach(function (cell) {
                    if (cell.role !== 'columnheader') {
                        $.ajax({
                            type: 'GET',
                            url: '/escala/disponibilidade_peraltas/verificar_dias_hospedagem/',
                            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                            data: {'data': cell.getAttribute('data-date')},
                            success: function (response) {
                                if (!response['hospedagem']) {
                                    cell.classList.add('not_selected')
                                } else {
                                    cell.classList.remove('not_selected')
                                }
                            }
                        }).done(() => {
                            setTimeout(() => {
                                $('.container_loading').addClass('none')
                            }, 500)
                        })
                    }
                })
            }
        },

        eventDidMount: function (info) {
            info.event.setProp('color', info.event.extendedProps['color'])

            if (!coordena) {
                if (hoje.getDate() > 15 && hoje.getMonth() + 1 === moment(info.event.start).month()) {
                    info.el.classList.remove('fc-event-draggable')
                }

                if (moment(info.event.start).format('YYYY-MM-DD') < data_mais_30) {
                    info.el.classList.remove('fc-event-draggable')
                }
            } else if (coordenacao_hotelaria && !coordenacao_acampamento) {
                $.ajax({
                    type: 'GET',
                    url: '/escala/disponibilidade_peraltas/verificar_dias_hospedagem/',
                    headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                    data: {'data': moment(info.event.start).format('YYYY-MM-DD')},
                    success: function (response) {
                        if (!response['hospedagem']) {
                            info.el.classList.remove('fc-event-draggable')
                        }
                    }
                }).done(() => {
                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 500)
                })
            }
        },

        eventReceive: async function (info) {
            $('.container_loading').removeClass('none')
            const id_monitor = info.event.extendedProps['id_monitor']
            const id_enfermeira = info.event.extendedProps['id_enfermeira']
            const dia_adicionado = moment(info.event.start).format('YYYY-MM-DD')
            const hoje = new Date(Date.now())
            const hoje_mais_30 = moment(hoje).add(30, 'days').format('YYYY-MM-DD')
            const eventos_intervalo = calendar.getEvents(hoje_mais_30.sub(30, 'days'), hoje_mais_30)

            if (await adicionar_disponibilidade(info, eventos_intervalo, id_monitor, id_enfermeira, dia_adicionado, hoje_mais_30, coordena, coordenacao_hotelaria, coordenacao_acampamento)) {
                $.ajax({
                    type: 'POST',
                    url: '/escala/disponibilidade_peraltas/alterar_dias_disponibilidade/',
                    headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                    data: {
                        'adicionar_dia': true,
                        'id_monitor': id_monitor,
                        'id_enfermeira': id_enfermeira,
                        'dia_adicionado': dia_adicionado
                    },
                }).then((response) => {
                    if (response === 'False') {
                        alert('Limite de 22 dias disponiveis no mês atingido pelo monitor')
                        info.revert()
                    }

                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 300)
                }).catch((response) => {
                    if (response.status == 500) alert('Operação não realizada. Erro interno do servidor!')

                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 300)
                    info.revert()
                })

                info.event.setProp('id', `disponibilidade_${id_monitor}_${dia_adicionado}`)
                info.event.setProp('color', info.event.extendedProps['color'])
            } else {
                setTimeout(() => {
                    $('.container_loading').addClass('none')
                }, 300)
                info.revert()
            }

        }
        ,

        eventDrop: function (info) {
            $('.container_loading').removeClass('none')
            const id_monitor = info.event.extendedProps['id_monitor']
            const id_enfermeira = info.event.extendedProps['id_enfermeira']
            const dia_adicionado = moment(info.event.start).format('YYYY-MM-DD')
            const dia_removido = moment(info.oldEvent.start).format('YYYY-MM-DD')
            const hoje = new Date(Date.now())
            const hoje_mais_30 = moment(hoje).add(30, 'days').format('YYYY-MM-DD')
            const eventos_intervalo = calendar.getEvents(hoje_mais_30.sub(30, 'days'), hoje_mais_30)

            if (adicionar_disponibilidade(info, eventos_intervalo, id_monitor, id_enfermeira, dia_adicionado, hoje_mais_30, coordena)) {
                $.ajax({
                    type: 'POST',
                    url: '/escala/disponibilidade_peraltas/alterar_dias_disponibilidade/',
                    headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                    data: {
                        'alterar_dia': true,
                        'id_monitor': id_monitor,
                        'id_enfermeira': id_enfermeira,
                        'dia_adicionado': dia_adicionado,
                        'dia_removido': dia_removido
                    },
                }).then((response) => {
                    if (response === 'False') {
                        alert('Limite de 22 dias disponiveis no mês atingido pelo monitor')
                    }

                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 300)
                }).catch((response) => {
                    if (response.status == 500) alert('Operação não realizada. Erro interno do servidor!')

                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 300)
                    info.revert()
                })
            } else {
                setTimeout(() => {
                    $('.container_loading').addClass('none')
                }, 300)
                info.revert()
            }
        }
        ,

        eventDragStop: (info) => {
            if (info.jsEvent.pageX < $('#calendario_escala').offset().left || info.jsEvent.pageX > ($('#calendario_escala').offset().left + $('#calendario_escala').width()) ||
                info.jsEvent.pageY < $('#calendario_escala').offset().top || info.jsEvent.pageY > ($('#calendario_escala').offset().top + $('#calendario_escala').height())) {
                $('.container_loading').removeClass('none')
                const id_monitor = info.event.extendedProps['id_monitor']
                const id_enfermeira = info.event.extendedProps['id_enfermeira']
                const dia_removido = moment(info.event.start).format('YYYY-MM-DD')

                $.ajax({
                    type: 'POST',
                    url: '/escala/disponibilidade_peraltas/alterar_dias_disponibilidade/',
                    headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                    data: {
                        'remover_disponibilidade': true,
                        'id_monitor': id_monitor,
                        'id_enfermeira': id_enfermeira,
                        'dia_removido': dia_removido
                    },
                }).then(() => {
                    calendar.getEventById(info.event.id).remove()

                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 300)
                }).catch((response) => {
                    if (response.status == 500) alert('Operação não realizada. Erro interno do servidor!')

                    setTimeout(() => {
                        $('.container_loading').addClass('none')
                    }, 300)
                })
            }
        },
    })

    calendar.render()
    calendar.setOption('locale', 'pt-br')
}
