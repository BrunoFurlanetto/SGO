function escalado(monitor){
    let setor = []
    let monitor_selecionado = $(`#${monitor.id} :selected`)
    let id_monitor = monitor_selecionado.val()
    let nome_monitor = monitor_selecionado.text()
    let teste = monitor_selecionado.option

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
        <button name = "${setor.join(' ')}" type = "button" id = "${id_monitor}" style = "font-size: larger" >
            &times
        </button>
    </span>`)
}