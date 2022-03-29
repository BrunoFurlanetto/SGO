
setTimeout(() => {
        $.ajax({
            type: 'POST',
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {'id_relatorio': $('#id_relatorio').val(), 'tipo': $('#id_tipo').val()},
            success: function (response) {

                for(let i in response['equipe']){
                    $(`#${i}`).val(response['equipe'][i])
                }

                if(response['atividades'] !== null){
                    montar_tabela_atividades(response)
                }

                if(response['locacoes'] !== null){
                    // $('#tabela').removeClass('none')
                    // $('#div_check').addClass('none')
                    montar_tabela_locacoes(response)
                } else {
                    check_locacao()
                    $('#checkAtividade').removeClass('none')
                }

                setTimeout(() => {
                    for(let i in response['professores_atividade']){
                        $(`#${i}`).val(response['professores_atividade'][i])
                    }
                },100)

                setTimeout(() =>{
                    for(let i in response['professores_locacoes']){
                        $(`#${i}`).val(response['professores_locacoes'][i])
                    }
                    verificar_n_professores()
                },200)

            }
        })
    }, 100
)

function edita(){
    $('#formulario').prop('disabled', false)
    $('#salvar').prop('disabled', false)
}
