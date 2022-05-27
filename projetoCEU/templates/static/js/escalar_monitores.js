monitores_escalados = []

function escalado(monitor){
    let setor = []
    let monitor_selecionado = $(`#${monitor.id} :selected`)
    let id_monitor = monitor_selecionado.val()
    let nome_monitor = monitor_selecionado.text()

    $('#escalar').removeClass('none')
    monitores_escalados.push(id_monitor)

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
    console.log(setor)
    $('#escalados').append(
    `<span id = "nome_monitor_botao" onClick = "console.log(this)" >
        ${nome_monitor} 
        <button name = "${setor.join(' ')}" type = "button" id = "${id_monitor}" onclick="remover_monitor_escalado(this)">
            &times
        </button>
    </span>`)
}

function remover_monitor_escalado(monitor){
    let setor = monitor.name.split(' ')
    let id_monitor = monitor.id
    let nome_monitor = monitor.parentNode.textContent.trim().split('\n')[0]

    if (setor.includes('acampamento')){
        $('#monitores_acampamento').append(`<option value="${id_monitor}">${nome_monitor}</option>`)
    }

    if (setor.includes('hotelaria')){
        $('#monitores_hotelaria').append(`<option value="${id_monitor}">${nome_monitor}</option>`)
    }

    monitores_escalados.splice(monitores_escalados.indexOf(id_monitor), 1)
    monitor.parentNode.remove()

}

function salvar_monitores_escalados(){

    if(monitores_escalados.length === 0){
        $('.alert-warning').empty()
        $('#corpo_site').prepend('<p class="alert-warning">Nenhum monitor foi selecionado</p>')
    }else{
        $('.alert-warning').empty()
    }

    $('#monitores_escalados').val(monitores_escalados)
    $('#enviar_formulario').click()
}