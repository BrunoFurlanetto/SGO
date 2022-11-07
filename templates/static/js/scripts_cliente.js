
function novo_cliente(){
    $('.busca').remove()
    $('.lista-clientes').addClass('none')
    $('.cadastro-novo').removeClass('none')
    $('.dados-cliente').addClass('none')

    // CEP
    setTimeout(() => {
        console.log('Foi')
        $("#id_cep").mask("00.000-000");
    }, 100)

}

function encaminhamento(){
    localStorage.setItem('encaminhado', true)
}

function completa_dados_cliente(selecao) {
    let cnpj = selecao.children[0].textContent.trim()
    let encaminhado = localStorage.getItem('encaminhado')
    $('#responsavel_evento').empty().append('<option></option>')

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

            for(let i in response['responsaveis']){
                $('#responsavel_evento').append(`<option value="${i}">${response['responsaveis'][i]}</option>`)
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

            if($('#responsavel_evento').val() !== ''){
                localStorage.setItem('nome_responsavel', $('#responsavel_evento :selected').text())
                localStorage.setItem('id_responsavel', $('#responsavel_evento').val())
                localStorage.setItem('id_cliente_responsavel', response['id'])
            }

        }
    })

    setTimeout(() => {  window.close(); }, 100);
}

function manter_botao(){
    setTimeout(() => {
        $('.btn-update').prop('disabled', true)
    }, 1)
}

function limpar_dados(){
    $('.search').addClass('none')
    $('#responsavel').val('')
    $('#id_responsavel_evento').val('')
}

function pegarCliente(){
    $('#id_cliente').val(localStorage.getItem('id'))
    $('#cliente').val(localStorage.getItem('fantasia'))

    if($('#id_cliente').val() !== ''){
        $('.search').removeClass('none')
    }

    localStorage.removeItem('id')
    localStorage.removeItem('fantasia')

    $.ajax({
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: {'id_cliente_app': $('#id_cliente').val()},
            success: function (response) {
                for(let i in response){
                    console.log(i, response[i])
                    $(`#${i}`).val(response[i]).prop('readonly', true)
                }
            }
        })
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

        // Telefone
    $('#id_fone').mask('(00) 0 0000-00009');
    $('#id_fone').blur(function(event) {
       if($(this).val().length == 16){ // Celular com 9 dígitos + 2 dígitos DDD e 4 da máscara
          $(this).mask('(00) 0 0000-0009');
       } else {
          $(this).mask('(00) 0000-0000');
       }
     });

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

$('document').ready(function() {
    jQuery('#form_responsavel').submit(function() {
        let div_responsavel = $('#responsavel-evento')
        let dados = jQuery(this).serialize();
        let url = $(this).attr('action');
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function(response) {
                $('#div-pai-responsavel-evento').prepend(`<p class="alert-success">${response['mensagem']}</p>`)
                div_responsavel.append(`<label>Nome do responsável</label>`)
                div_responsavel.append(`<input name="repsonsavel" value="${response['nome_responsavel']}" id="nome_do_responsavel" readonly/>`)
                div_responsavel.append(`<input type="hidden" name="id_responsavel" id="id_responsavel" value="${response['id_responsavel']}"/>`)
                $('#add_responsavel').addClass('none')
                $('#novo_responsavel').modal('hide')
            },
            error: function(response){
                div_responsavel.append(`<p class="alert-alert">${response['mensagem']}</p>`)
            }
        });
        return false;
    });
});

$('document').ready(function() {
    if(localStorage.getItem('encaminhado')) {
        jQuery('#cadastro_cliente').submit(function () {
            let dados = jQuery(this).serialize();
            let url = $(this).attr('action');
            $.ajax({
                url: url,
                headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
                type: "POST",
                data: dados,
                success: function (response) {
                    if(typeof response['mensagem'] === 'object'){
                        for(let i in response['mensagem']){
                            for(let j = 0; j < Object.keys(response['mensagem'][i]).length; j++){
                                $('#corpo_site').prepend(`<p class="alert-warning">${response['mensagem'][i][j]}</p>`)
                            }
                        }
                        return
                    } else {
                        $('#corpo_site').prepend(`<p class="alert-success">${response['mensagem']}</p>`)
                    }

                    localStorage.removeItem('encaminhado')
                    localStorage.setItem('id', response['id_cliente'])
                    localStorage.setItem('id_cliente_responsavel', response['id_cliente'])
                    localStorage.setItem('fantasia', response['nome_fantasia'])

                    if($('#nome_do_resposavel')){
                        localStorage.setItem('nome_responsavel', $('#nome_do_responsavel').val())
                        localStorage.setItem('id_responsavel', $('#id_responsavel').val())
                    }
                    setTimeout( () => {
                        window.close()
                    }, 3000)
                },
                error: function (response) {
                    $('#corpo_site').prepend(response['mensagem'])
                }
            });
            return false;
        });
    }
});
// ------------------------- Mascaras ---------------------
$(document).ready(function() {
    // CNPJ
    $('#search-input, #id_cnpj').mask("99.999.999/9999-99")
})