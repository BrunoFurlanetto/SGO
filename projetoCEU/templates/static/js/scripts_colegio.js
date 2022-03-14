
function completar_informacoes(selecao) {
    let colegio = selecao.value

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'colegio': colegio},
        success: function (response) {

            $('#id_serie').val(response['colegio']['serie'])
            $('#id_responsaveis').val(response['colegio']['responsaveis'])
            $('#id_participantes_previa').val(response['colegio']['previa'])
            $('#id_coordenador_peraltas').val(response['colegio']['coordenador_peraltas'])

            //console.log(response['colegio']['atividades'])
            let select_prof_tb = []
            console.log(Object.keys(response['colegio']['atividades']).length)

            for(let i = 1; i <= Object.keys(response['colegio']['atividades']).length; i++){

                for(let j = 1; j <= 4; j++) {
                    select_prof_tb[j] = `<select class="select-control d mr-sm-2" id="prof_${j}_ativ_${i}" name="colegio"></select>`
                }

                for(let j = 1; j <= 4; j++){
                    select_prof_tb[i] += select_prof_tb[j]
                }

            }
            console.log(select_prof_tb[1,0])
        }
    })
}