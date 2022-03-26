
function novo_cliente(){
    $('.busca').remove()
    $('.lista-clientes').addClass('none')
    $('.cadastro-novo').removeClass('none')
    $('.dados-cliente').addClass('none')
}

function encaminhamento(){
    localStorage.setItem('encaminhado', true)
}

function completa_dados_cliente(selecao) {

    let cnpj = parseInt(selecao.children[0].textContent.replaceAll('.', '').replaceAll('/', '').replace('-', ''))
    let encaminhado = localStorage.getItem('encaminhado')

    if(!encaminhado){
        $('#btn_selecionar_cliente').addClass('none')
    }

    $('.dados-cliente').removeClass('none')

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'cnpj': cnpj},
        success: function (response) {

            for(let i in response){
                $(`#id_${i}`).val(response[i])
            }

        }
    })
}

function put(){
    $('.btn-update').prop('disabled', false)
}

function salvarCliente(){
    let cliente = document.getElementById('id_nome_fantasia')
    localStorage.setItem('fantasia', cliente.value);
    localStorage.removeItem('encaminhado')

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'cnpj': $('#id_cnpj').val()},
        success: function (response) {
            console.log(response['id'])
            localStorage.setItem('id', response['id'])
        }
    })

    setTimeout(() => {  window.close(); }, 100);
}

function pegarCliente(){
    $('#id_cliente').val(localStorage.getItem('id'))
    $('#cliente').val(localStorage.getItem('fantasia'))

    if($('#id_cliente').val() !== ''){
        $('.search').removeClass('none')
    } else {
        $('.search').addClass('none')
        $('#responsavel').val('')
        $('#id_responsavel_evento').val('')
    }

    localStorage.removeItem('id')
    localStorage.removeItem('fantasia')
}

function salvarIdCliente(){
    localStorage.setItem('id_cliente', $('#search-cliente').val())
    localStorage.setItem('fantasia_cliente', $('#search-cliente :selected').text())
}

function limpar_dados_salvos(){
    localStorage.removeItem('id_cliente')
    localStorage.removeItem('fantasia_cliente')
}

function pegarDadosResponsaveis(selecao){
    $('#corpo-tabela-responsaveis').empty()
    $('#id_responsavel_por').val(selecao.value)
    let id_cliente = selecao.value


    console.log(id_cliente)

     $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id': id_cliente},
        success: function (response) {

            for(let i in response){
                const ddd = String(response[i]['fone']).slice(0, 2)
                const parte_1_9 = String(response[i]['fone']).slice(2, 3)
                const parte_1 = String(response[i]['fone']).slice(3, 7)
                const parte_2 = String(response[i]['fone']).slice(7, 11)

                $('#corpo-tabela-responsaveis').append(`<tr id="${i}"></tr>`)
                $(`#${i}`).append(`<td><button type="button" class="button-responsavel" onclick="completa_dados_responsavel(this)"><span>${response[i]['nome']}</span></button></td>`)
                $(`#${i}`).append(`<td>${'(' + ddd + ') '+ parte_1_9 + ' ' + parte_1 + ' - ' + parte_2}</td>`)
                $(`#${i}`).append(`<td>${response[i]['email']}</td>`)
                $(`#${i}`).append(`<td id="responsavel_cliente">${response[i]['responsavel_por']}</td>`)
            }
        }
    })
}

function completa_dados_responsavel(selecao){
    let id = parseInt(selecao.id)
    $('.dados-responsavel').removeClass('none')
    $('.lista-responsaveis').addClass('none')

    console.log(id)

    $.ajax({
        type: 'POST',
        url: '/cadastro/lista_responsaveis/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_selecao': id},
        success: function (response) {
            console.log(response)
             for(let j in response){
                $(`#id_${j}`).val(response[j])
            }

        }
    })
}

function novo_responsavel(){
    $('.cadastro-responsavel').removeClass('none')
    $('.dados-responsavel').remove()
    $('.lista-responsaveis').addClass('none')

    $('#id_responsavel_por').val(localStorage.getItem('id_cliente'))
    $('#nome_fantasia_cliente').val(localStorage.getItem('fantasia_cliente'))

}

function putResponsavel(){
    $('.btn-update').prop('disabled', false)
}

function salvarResponsavel(){
    localStorage.removeItem('id_cliente')
    localStorage.setItem('nome_responsavel', $('#id_nome').val())
    localStorage.setItem('id_cliente_responsavel', $('#id_responsavel_por').val())
    localStorage.setItem('id_responsavel', $('#id_id').val())

    window.close()
}

function pegarResponsavel(){

    if($('#id_cliente').val() && localStorage.getItem('id_cliente_responsavel')) {
        $.ajax({
            type: 'POST',
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {'id_cliente': $('#id_cliente').val(), 'id_responsavel': localStorage.getItem('id_responsavel')},
            success: function (response) {
                console.log(response)
                if (!response['resposta']) {
                    alert(localStorage.getItem('nome_responsavel') + ' não está cadastrado como responsável de eventos pela ' + $('#cliente').val())
                    $('#responsavel').val('')
                    $('#id_responsavel_evento').val('')
                } else {
                    $('#responsavel').val(localStorage.getItem('nome_responsavel'))
                    $('#id_responsavel_evento').val(parseInt(localStorage.getItem('id_responsavel')))
                }
            }
        })
    }


    setTimeout(() => {
        localStorage.removeItem('id_cliente')
        localStorage.removeItem('nome_responsavel')
        localStorage.removeItem('id_cliente_responsavel') }, 450);

}
