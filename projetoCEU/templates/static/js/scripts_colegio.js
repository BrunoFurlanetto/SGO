let equipe_escalada = []
function criar_lihas_colunas(){
    let i = document.querySelectorAll('.linhas').length

    $('#corpo_tabela_atividade').append(`<tr class="linhas" id="linha_${i+1}"></tr>`)
    $(`#linha_${i+1}`).append(`<td class="div_colunas_1" id="div_coluna_1_linha_${i+1}"></td>`)
    $(`#div_coluna_1_linha_${i+1}`).append(`<div class="row colunas_1" id="coluna_1_linha_${i+1}" style="margin-left: 2px"></div>`)
    $(`#linha_${i+1}`).append(`<td class="div_colunas_2" id="div_coluna_2_linha_${i+1}"></td>`)
    $(`#div_coluna_2_linha_${i+1}`).append(`<div class="colunas_2" id="coluna_2_linha_${i+1}"></div>`)
    $(`#linha_${i+1}`).append(`<td class="div_colunas_3" id="div_coluna_3_linha_${i+1}"></td>`)
    $(`#div_coluna_3_linha_${i+1}`).append(`<div class="colunas_3" id="coluna_3_linha_${i+1}"></div>`)
    $(`#linha_${i+1}`).append(`<td class="div_colunas_4" id="div_coluna_4_linha_${i+1}"></td>`)
    $(`#div_coluna_4_linha_${i+1}`).append(`<div class="colunas_4" id="coluna_4_linha_${i+1}"></div>`)
    $(`#linha_${i+1}`).append(`<td class="div_colunas_5" id="div_coluna_5_linha_${i+1}"></td>`)
    $(`#div_coluna_5_linha_${i+1}`).append(`<div class="colunas_5" id="coluna_5_linha_${i+1}"></div>`)
    return i
}

function popular_professores(i){
    for(let j = 0; j < 4; j++) {
        $(`#coluna_1_linha_${i+1}`).append(`<select class="form-control escalados professores" id="prof_${j + 1}_ativ_${i + 1}" name="prf_${j}_ativ_${i + 1}" style="width: 45%; margin: 2px;"></select>`)
        $(`#prof_${j+1}_ativ_${i+1}`).append(`<option selected></option>`)
    }

    // Mandar ajax pra pegar todos os professores e popular os selects

}

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
            $('#corpo_tabela_atividade').empty()

            for(let i = 0; i < Object.keys(response['colegio']['atividades']).length; i++){
                criar_lihas_colunas()
                popular_professores(i)

                $(`#coluna_2_linha_${i+1}`).append(`<select class="form-control atividades" id="ativ_${i+1}" name="ativ_${i+1}"></select>`)
                colocar_atividades(response['atividades'], response['colegio']['atividades'][`atividade_${i+1}`]['atividade'], `ativ_${i+1}`)

                let data = response['colegio']['atividades'][`atividade_${i+1}`]['data_e_hora'].replace(' ', 'T')
                $(`#coluna_3_linha_${i+1}`).append(`<input class="datas" type="datetime-local" id="data_hora_ativ${i+1}" name="data_hora_ativ_${i+1}" value="${data}"/>`)

                $(`#coluna_4_linha_${i+1}`).append(`<input class="qtds" type="number" id="qtd_ativ${i+1}" name="qtd_ativ_${i+1}" value="${response['colegio']['atividades'][`atividade_${i+1}`]['participantes']}"/>`)

                $(`#coluna_5_linha_${i+1}`).append(`<button class="buton-x-" id="btn_${i+1}" type="button" onClick="remover_linha(this)"><span><i class='bx bx-x' ></span></button>`)
            }



        }
    })
}

function colocar_atividades(atividades, atividade, id) {
    console.log(atividade)
    $(`#${id}`).append(`<option></option>`)
    $(`#${id}`).append(`<option selected value="">${atividade}</option>`)

    for(let i in atividades){

        if(atividades[i] != atividade) {
            $(`#${id}`).append(`<option value="${i}">${atividades[i]}</option>`)
        }

    }

}

function remover_linha(selecao){
    $(`#linha_${selecao.id.split('_')[1]}`).remove()

    let linhas = document.querySelectorAll('.linhas')
    let colunas_1 = document.querySelectorAll('.colunas_1')
    let colunas_2 = document.querySelectorAll('.colunas_2')
    let colunas_3 = document.querySelectorAll('.colunas_3')
    let colunas_4 = document.querySelectorAll('.colunas_4')
    let colunas_5 = document.querySelectorAll('.colunas_5')
    let div_colunas_1 = document.querySelectorAll('.div_colunas_1')
    let div_colunas_2 = document.querySelectorAll('.div_colunas_2')
    let div_colunas_3 = document.querySelectorAll('.div_colunas_3')
    let div_colunas_4 = document.querySelectorAll('.div_colunas_4')
    let div_colunas_5 = document.querySelectorAll('.div_colunas_5')

    let professores = document.querySelectorAll('.professores')
    let atividades = document.querySelectorAll('.atividades')
    let datas = document.querySelectorAll('.datas')
    let qtds = document.querySelectorAll('.qtds')
    let buton = document.querySelectorAll('.buton-x-')

    for(let k = 0; k < linhas.length; k++){
        $(linhas[k]).attr('id', 'linha_'+(k+1))

        console.log(linhas)

        for(let i = 0; i <= 5; i++) {
            console.log(i, k+1)
            $(colunas_1[i]).attr('id', 'coluna_1_linha_' + (k + 1))
            $(colunas_2[i]).attr('id', 'coluna_2_linha_' + (k + 1))
            $(colunas_3[i]).attr('id', 'coluna_3_linha_' + (k + 1))
            $(colunas_4[i]).attr('id', 'coluna_4_linha_' + (k + 1))
            $(colunas_5[i]).attr('id', 'coluna_5_linha_' + (k + 1))

            $(div_colunas_1[i]).attr('id', 'div_coluna_1_linha_' + (k + 1))
            $(div_colunas_2[i]).attr('id', 'div_coluna_2_linha_' + (k + 1))
            $(div_colunas_3[i]).attr('id', 'div_coluna_3_linha_' + (k + 1))
            $(div_colunas_4[i]).attr('id', 'div_coluna_4_linha_' + (k + 1))
            $(div_colunas_5[i]).attr('id', 'div_coluna_5_linha_' + (k + 1))
        }

        for(let j = 0; j < 4; j++) {
            $(professores[j+(k*4)]).attr('id', `prf_${(j+1)}_ativ_${k+1}`).attr('name', `prf_${j+2}_ativ_${k+1}`)
        }

        $(atividades[k]).attr('id', `ativ_${k+1}`).attr('name', `ativ_${k+1}`)
        $(datas[k]).attr('id', `data_hora_ativ${k+1}`).attr('name', `data_hora_ativ_${k+1}`)
        $(qtds[k]).attr('id', `qtd_ativ${k+1}`).attr('name', `qtd_ativ_${k+1}`)
        $(buton[k]).attr('id', `btn_${k+1}`)
    }
}

function add_linha_atividade() {
    let i = criar_lihas_colunas()
    popular_professores(i)

    $(`#coluna_2_linha_${i+1}`).append(`<select class="form-control atividades" id="ativ_${i+1}" name="ativ_${i+1}"></select>`)
    $(`#coluna_3_linha_${i+1}`).append(`<input class="datas" type="datetime-local" id="data_hora_ativ${i+1}" name="data_hora_ativ_${i+1}"/>`)
    $(`#coluna_4_linha_${i+1}`).append(`<input class="qtds" type="number" id="qtd_ativ${i+1}" name="qtd_ativ_${i+1}"/>`)
    $(`#coluna_5_linha_${i+1}`).append(`<button class="buton-x-" id="btn_${i+1}" type="button" onClick="remover_linha(this)"><span><i class='bx bx-x' ></span></button>`)
}
