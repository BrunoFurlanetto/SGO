
setTimeout(() =>
    {
        $.ajax({
            type: 'POST',
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {'id_relatorio_publico': $('#id_publico').val()},
            success: function (response) {

                $('#id_data_atendimento').val(response['id_data_atendimento'])
                $('#id_relatorio').val(response['observacoes'])

                for(let i in response['equipe']){
                    $(`#${i}`).val(response['equipe'][i])
                }

                for(let i in response['atividades']){
                    $(`#${i}`).val(response['atividades'][i])
                }

                for(let i in response['professores']){
                    $(`#${i}`).val(response['professores'][i])
                }

                for(let i in response['horas']){
                     $(`#${i}`).val(response['horas'][i])
                }

            }
        })
    },100
)

function edita(){
    $('#formulario').prop('disabled', false)
    $('#salvar').prop('disabled', false)
}

function validacao(selecao){
    let professor = selecao.value

    let coordenador = $('#coordenador').val()
    let professor_2 = $('#professor_2').val()
    let professor_3 = $('#professor_3').val()
    let professor_4 = $('#professor_4').val()

    if(professor !== coordenador && professor !== professor_2 && professor !== professor_3 && professor !== professor_4){
        $('#alert').remove()
        $($(`#${selecao.id}`).parent().parent().parent().parent().parent()).prepend(`<td colspan="5" class="alert-danger" id="alert"><center>Professor não escalado</center></td>`)
        $(`#${selecao.id}`).val('')
    } else {
        $('#alert').remove()
    }


}