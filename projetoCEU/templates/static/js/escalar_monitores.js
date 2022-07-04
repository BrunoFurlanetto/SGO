let monitores_escalados = []

function pegar_dados_evento(selecao){
    $('#monitores_acampamento, #monitores_hotelaria').empty()
    if(selecao.value !== '') {
        $.ajax({
            type: 'POST',
            async: false,
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {'id_cliente': selecao.value},
            success: function (response) {

                $('#check_in').val(moment(response['check_in']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))
                $('#check_out').val(moment(response['check_out']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))

                for(let monitor in response['disponiveis_evento']){

                    if(response['disponiveis_evento'][monitor]['setor'] === 'acampamento'){
                        if(response['disponiveis_evento'][monitor]['tecnica']){
                            $('#monitores_acampamento').append(`<option class="tecnica" value="${response['disponiveis_evento'][monitor]['id']}">${response['disponiveis_evento'][monitor]['nome']}</option>`)
                        }else{
                            $('#monitores_acampamento').append(`<option value="${response['disponiveis_evento'][monitor]['id']}">${response['disponiveis_evento'][monitor]['nome']}</option>`)
                        }
                    }else{
                        if(response['disponiveis_evento'][monitor]['tecnica']){
                            $('#monitores_hotelaria').append(`<option class="tecnica" value="${response['disponiveis_evento'][monitor]['id']}">${response['disponiveis_evento'][monitor]['nome']}</option>`)
                        }else{
                            $('#monitores_hotelaria').append(`<option value="${response['disponiveis_evento'][monitor]['id']}">${response['disponiveis_evento'][monitor]['nome']}</option>`)
                        }
                    }
                }

            }
        })
    }else{
        $('#check_in').val('')
        $('#check_out').val('')
    }
}

function escalado(monitor){
    let setor = []
    let monitor_selecionado = $(`#${monitor.id} :selected`)
    let id_monitor = monitor_selecionado.val()
    let nome_monitor = monitor_selecionado.text()
    const ja_escalado = verificar_escalado(id_monitor)

    $('#escalar').removeClass('none')
    monitores_escalados.push(id_monitor)

    if(monitor_selecionado[0].classList.contains('tecnica')){
        $.ajax({
            type: 'POST',
            async: false,
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {'id_monitor': id_monitor},
            success: function (response) {
                if(response['video'] && $('.mensagem-tecnica-video').length === 0){
                    $('#escalar').append('<p class="alert-warning mensagem-tecnica-video" style="width: 98%; margin-left: 1%; margin-bottom: -5px" id="mensagem_tecnica">Técnico de video</p>')
                }
                if(response['som'] && $('.mensagem-tecnica-som').length === 0){
                    $('#escalar').append('<p class="alert-warning mensagem-tecnica-som" style="width: 98%; margin-left: 1%; margin-bottom: -5px" id="mensagem_tecnica">Técnico de som</p>')
                }
                if(response['fotos_e_filmagens'] && $('.mensagem-tecnica-fotos').length === 0){
                    $('#escalar').append('<p class="alert-warning mensagem-tecnica-fotos" style="width: 98%; margin-left: 1%" id="mensagem_tecnica">Técnico de fotos e filmagens</p>')
                }
            }
        })
    }

    $('#monitores_hotelaria option').each(function (id, nome){
        if(nome.value === id_monitor){
            if(nome.parentNode.name !== setor){
                setor.push(nome.parentNode.name.split('_')[1])
            }
            nome.remove()
        }
    })

    $('#monitores_acampamento option').each(function (id, nome){
        if(nome.value === id_monitor){
            if(nome.parentNode.name !== setor){
                setor.push(nome.parentNode.name.split('_')[1])
            }
            nome.remove()
        }
    })

    if(ja_escalado){
        if (monitor_selecionado.attr("class") === 'tecnica') {
            setor.push('tecnica')
            $('#escalados').append(
                `<span class="alert-danger ja_escalado tecnica" id = "nome_monitor_botao" style="background-color: #f8d7da">
                    ${nome_monitor} 
                    <button name = "${setor.join(' ')}" type = "button" id = "${id_monitor}" onclick="remover_monitor_escalado(this)">
                        &times
                    </button>
                </span>`
            )
        } else {
            $('#escalados').append(
                `<span class="alert-danger ja_escalado" id = "nome_monitor_botao" style="background-color: #f8d7da" >
                    ${nome_monitor} 
                    <button name = "${setor.join(' ')}" type = "button" id = "${id_monitor}" onclick="remover_monitor_escalado(this)">
                        &times
                    </button>
                </span>`
            )
        }
    }else {
        if (monitor_selecionado.attr("class") === 'tecnica') {
            setor.push('tecnica')
            $('#escalados').append(
                `<span class="tecnica" id = "nome_monitor_botao">
                    ${nome_monitor} 
                    <button name = "${setor.join(' ')}" type = "button" id = "${id_monitor}" onclick="remover_monitor_escalado(this)">
                        &times
                    </button>
                </span>`
            )
        } else {
            $('#escalados').append(
                `<span id = "nome_monitor_botao" >
                    ${nome_monitor} 
                    <button name = "${setor.join(' ')}" type = "button" id = "${id_monitor}" onclick="remover_monitor_escalado(this)">
                        &times
                    </button>
                </span>`
            )
        }
    }
}

function remover_monitor_escalado(monitor, editando=false){

    if(editando){
        $('#botao_salvar_escala').prop('disabled', false)
    }

    let setor = monitor.name.split(' ')
    let id_monitor = monitor.id
    let nome_monitor = monitor.parentNode.textContent.trim().split('\n')[0]

    if (setor.includes('acampamento')){
        if(setor.includes('tecnica')){
            $('#monitores_acampamento').append(`<option class="tecnica" value="${id_monitor}">${nome_monitor}</option>`)
        }else {
            $('#monitores_acampamento').append(`<option value="${id_monitor}">${nome_monitor}</option>`)
        }
    }

    if (setor.includes('hotelaria')){
        if(setor.includes('tecnica')){
            $('#monitores_hotelaria').append(`<option class="tecnica" value="${id_monitor}">${nome_monitor}</option>`)
        }else {
            $('#monitores_hotelaria').append(`<option value="${id_monitor}">${nome_monitor}</option>`)
        }
    }

    monitores_escalados.splice(monitores_escalados.indexOf(id_monitor), 1)
    monitor.parentNode.remove()

    if($('#escalados .tecnica').length === 0){
        let mensagens = document.querySelectorAll('#mensagem_tecnica')
        for(let i = 0; i <= mensagens.length; i++){
            mensagens[i].remove()
        }
    }

    if($('.ja_escalado').length === 0){
        $('#mensagem').remove()
    }

}

function salvar_monitores_escalados(){

    if(monitores_escalados.length === 0){
        $('.alert-warning').empty()
        $('#corpo_site').prepend('<p class="alert-warning">Nenhum monitor foi selecionado</p>')
    }else{
        $('.alert-warning').empty()
        $('#monitores_escalados').val(monitores_escalados)
        $('#enviar_formulario').click()
    }
}

function verificar_escalado(id_monitor, editando=false){
    let ja_escalado = false
    let id_cliente

    if(editando){
        id_cliente = $('#id_cliente').val()
    }else{
        id_cliente = $('#cliente').val()
    }

    $.ajax({
        type: 'POST',
        async: false,
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_monitor': id_monitor, 'cliente': id_cliente},
        success: function (response){

            if(response['acampamento']){
                if($('#mensagem').length === 0){
                    $('#escalar').append('<p class="alert-danger" style="width: 98%; margin-left: 1%" id="mensagem">Monitor(es) presente(s) em escala do acampamento na data em questão!</p>')
                }
                ja_escalado = true
            }

            if(response['hotelaria']){
                if($('#mensagem').length === 0) {
                    $('#escalar').append('<p class="alert-danger" style="width: 98%; margin-left: 1%" id="mensagem">Monitor(es) presente(s) em escala da hotelaria na data em questão!</p>')
                }
                ja_escalado = true
            }
        }
    })
    return ja_escalado
}

function pegar_escalados(){
    let monitores = $('#monitores_escalados').val().replace('[', '').replace(']', '').split(', ')

    for(let i = 0; i < monitores.length; i++){
        if(monitores[i] !== '') {
            monitores_escalados.push(monitores[i])
        }
    }
}

function active_botao_salvar(){
    $('#botao_salvar_escala').prop('disabled', false)
}