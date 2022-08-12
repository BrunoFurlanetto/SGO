
function chamar_select2(){
    $('#id_equipe').select2().on("select2:select", function (evt) {
        let element = evt.params.data.element;
        let $element = $(element);

        $element.detach();
        $(this).append($element);
        $(this).trigger("change");
    });
}

function ver_tipo_escala(escolha){
    $('#id_equipe').empty()
    const data = $('#id_data_publico').val()

    if(escolha.value === '1'){
        if(data !== ''){
            pegar_professores_disponiveis(data)
        }

        $('.publico, .escala, .botoes').removeClass('none')
        $('.grupo').addClass('none')
        chamar_select2()
    } else if (escolha.value === '2'){
        $('.grupo, .escala, .botoes').removeClass('none')
        $('.publico').addClass('none')
        chamar_select2()
    } else {
        $('.publico, .grupo, .escala, .botoes').addClass('none')
    }
}

function pegar_dados_grupo(selecao){
    const grupo = selecao.value

    if(grupo === ''){
        $('.datas').addClass('none')
        $('#id_check_in_grupo').val('')
        $('#id_check_out_grupo').val('')

        return
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'grupo': grupo},
        success: function (response) {
            $('#id_check_in_grupo').val(moment(response['check_in']).format('yyyy-MM-DDTHH:mm'))
            $('#id_check_out_grupo').val(moment(response['check_out']).format('yyyy-MM-DDTHH:mm'))
            $('.datas').removeClass('none')

            pegar_professores_disponiveis_grupo(
                moment(response['check_in']).format('yyyy-MM-DDTHH:mm'),
                moment(response['check_out']).format('yyyy-MM-DDTHH:mm')
                )
        }
    })
}

function pegar_professores_disponiveis(data){
    $('#id_equipe').empty()
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'data': data},
        success: function (response) {
            for(let professor in response['disponiveis']){
                $('#id_equipe').append(`<option value="${response['disponiveis'][professor]['id']}">${response['disponiveis'][professor]['nome']}</option>`)
            }
        }
    })
}

function pegar_professores_disponiveis_grupo(check_in, check_out){
    $('#id_equipe').empty()
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'check_in': check_in, 'check_out': check_out},
        success: function (response) {
            for(let professor in response['disponiveis']){
                $('#id_equipe').append(`<option value="${response['disponiveis'][professor]['id']}">${response['disponiveis'][professor]['nome']}</option>`)
            }
        }
    })
}