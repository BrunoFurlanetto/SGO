
function novo_cliente(){
    $('.busca').remove()
    $('.lista-clientes').addClass('none')
    $('.cadastro-novo').removeClass('none')
}

function completa_dados_cliente(selecao) {
    let cnpj = parseInt(selecao.children[0].textContent.replaceAll('.', '').replaceAll('/', '').replace('-', ''))

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
    localStorage.removeItem('id')
    localStorage.removeItem('fantasia')
}

function salvarIdCliente(){
    localStorage.setItem('id_cliente', $('#id_cliente').val())
    localStorage.setItem('fantasia_cliente', $('#cliente').val())
}
function pegarDadosResponsaveis(){
    let id_cliente = localStorage.getItem('id_cliente')
    console.log(id_cliente)
    $('.titulo-responsaveis').append(`<h4>Lista de responsáveis por ${localStorage.getItem('fantasia_cliente')}</h4>`)

     $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id': id_cliente},
        success: function (response) {

            for(let i in response){
                const ddd = String(response[i]['fone']).slice(0, 2)
                const parte_1 = String(response[i]['fone']).slice(3, 7)
                const parte_2 = String(response[i]['fone']).slice(7, 11)

                $('#corpo-tabela-responsaveis').append(`<tr id="${i}"></tr>`)
                $(`#${i}`).append(`<td><button type="button" class="button-responsavel" onclick="completa_dados_responsavel(this)"><span>${response[i]['nome']}</span></button></td>`)
                $(`#${i}`).append(`<td>${'(' + ddd + ')' + ' 9 ' + parte_1 + ' - ' + parte_2}</td>`)
                $(`#${i}`).append(`<td>${response[i]['email']}</td>`)
                $(`#${i}`).append(`<td id="responsavel_cliente">${response[i]['responsavel_por']}</td>`)
            }
        }
    })
}

function completa_dados_responsavel(selecao){
    let id = parseInt(selecao.parentNode.parentNode.id)
    $('.dados-responsavel').removeClass('none')

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_selecao': id},
        success: function (response) {

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
}

function putResponsavel(){
    $('.btn-update').prop('disabled', false)
}

function salvarResponsavel(){
    localStorage.removeItem('id_cliente')
    console.log($('#responsavel_cliente'))
    localStorage.setItem('nome_responsavel', $('#id_nome').val())
    localStorage.setItem('id_cliente_responsavel', $('#id_responsavel_por').val())

    window.close()
}

function pegarResponsavel(){
    $('#responsavel').val(localStorage.getItem('nome_responsavel'))
    $('#id_responsavel_evento').val(parseInt(localStorage.getItem('id_cliente_responsavel')))

    localStorage.removeItem('nome_responsavel')
    localStorage.removeItem('id_cliente_responsavel')
}