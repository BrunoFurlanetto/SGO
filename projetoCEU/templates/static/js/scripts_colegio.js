function check_locacao(){

    if($("#checkAtividade").is(":checked")){
        $('.locacao').removeClass('none')
    }else{
        $('.locacao').addClass('none')
    }
}

function montar_cabecalho(dados){
    $('#id_serie').val(dados['serie'])
    $('#id_responsaveis').val(dados['responsaveis'])
    $('#id_participantes_previa').val(dados['previa'])
    $('#id_coordenador_peraltas').val(dados['coordenador_peraltas'])
    $('#corpo_tabela_atividade').empty()
    $('#corpo_tabela_locacao').empty()
}

function criar_linhas_colunas(){
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
        $(`#coluna_1_linha_${i+1}`).append(`<select class="form-control professores" id="prof_${j + 1}_ativ_${i + 1}" name="prf_${j}_ativ_${i + 1}" style="width: 45%; margin: 2px;"></select>`)
        $(`#prof_${j+1}_ativ_${i+1}`).append(`<option selected></option>`)
    }

     $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'professor'},
        success: function (response) {

            for(let k in response){
                for(let j = 0; j < 4; j++) {
                    $(`#prof_${j + 1}_ativ_${i + 1}`).append(`<option value="${k}">${response[k]}</option>`)
                }
            }

        }

     })
}
function popular_professores_locacao(i){

        $(`#coluna_1_linha_loc_${i+1}`).append(`<select class="form-control escalados professores_loc" id="prof_loc_${i + 1}" name="prf_loc_${i + 1}" style="width: 110px"></select>`)
        $(`#prof_loc_${i+1}`).append(`<option selected></option>`)

     $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'professor'},
        success: function (response) {

            for(let k in response) {
                $(`#prof_loc_${i + 1}`).append(`<option value="${k}">${response[k]}</option>`)
            }
        }

     })
}

function completar_informacoes(selecao) {
    let cliente = selecao.value

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'cliente': cliente},
        success: function (response) {

            check_locacao()
            console.log('Mudou')
            montar_cabecalho(response['cliente'])
            if(response['cliente']['atividades'] != null) {
                montar_tabela_atividades(response['cliente'])
            }

            if(response['cliente']['locacoes'] != null) {
                check_locacao()
                $('#checkAtividade').addClass('none')
                montar_tabela_locacoes(response['cliente'])
            } else {
                check_locacao()
                $('#checkAtividade').removeClass('none')
            }

        }

    })
}

function montar_tabela_atividades(dados){
    for (let i = 0; i < Object.keys(dados['atividades']).length; i++) {
        criar_linhas_colunas()
        popular_professores(i)

        $(`#coluna_2_linha_${i + 1}`).append(`<select class="form-control atividades" id="ativ_${i + 1}" name="ativ_${i + 1}"></select>`)
        colocar_atividades(dados['atividades'][`atividade_${i + 1}`]['atividade'], `ativ_${i + 1}`)

        let data = dados['atividades'][`atividade_${i + 1}`]['data_e_hora'].replace(' ', 'T')
        $(`#coluna_3_linha_${i + 1}`).append(`<input class="datas" type="datetime-local" id="data_hora_ativ${i + 1}" name="data_hora_ativ_${i + 1}" value="${data}"/>`)

        $(`#coluna_4_linha_${i + 1}`).append(`<input class="qtds" type="number" id="qtd_ativ${i + 1}" name="qtd_ativ_${i + 1}" value="${dados['atividades'][`atividade_${i + 1}`]['participantes']}"/>`)

        $(`#coluna_5_linha_${i + 1}`).append(`<button class="buton-x-" id="btn_${i + 1}" type="button" onClick="remover_linha(this)"><span><i class='bx bx-x' ></span></button>`)
    }
}

function colocar_atividades(atividade, id) {

    if (atividade != null) {
        $(`#${id}`).append(`<option></option>`)
        $(`#${id}`).append(`<option selected value="">${atividade}</option>`)
    } else {
        $(`#${id}`).append(`<option selected></option>`)
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'atividade'},
        success: function (response) {

            for (let k in response) {

                if(atividade != null){
                    if(atividade != response[k]) {
                        $(`#${id}`).append(`<option value="${k}">${response[k]}</option>`)
                    }
                } else {
                    $(`#${id}`).append(`<option value="${k}">${response[k]}</option>`)
                }

            }
        }
    })
}
function colocar_locacoes(local, id){

    if (local != null) {
        $(`#${id}`).append(`<option></option>`)
        $(`#${id}`).append(`<option selected value="">${local}</option>`)
    } else {
        $(`#${id}`).append(`<option selected></option>`)
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'locacao'},
        success: function (response) {

            for (let k in response) {

                if(local != null){
                    if(local != response[k]) {
                        console.log(response)
                        $(`#${id}`).append(`<option value="${k}">${response[k]}</option>`)
                    }
                } else {
                    $(`#${id}`).append(`<option value="${k}">${response[k]}</option>`)
                }

            }
        }
    })
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

        for(let i = 0; i <= 5; i++) {
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
function remover_linha_locacao(selecao){
    $(`#linha_loc_${selecao.id.split('_')[1]}`).remove()

    let linhas = document.querySelectorAll('.linhas_loc')
    let colunas_1 = document.querySelectorAll('.colunas_loc_1')
    let colunas_2 = document.querySelectorAll('.colunas_loc_2')
    let colunas_3 = document.querySelectorAll('.colunas_loc_3')
    let colunas_4 = document.querySelectorAll('.colunas_loc_4')
    let colunas_5 = document.querySelectorAll('.colunas_loc_5')
    let colunas_6 = document.querySelectorAll('.colunas_loc_6')
    let div_colunas_1 = document.querySelectorAll('.div_colunas_loc_1')
    let div_colunas_2 = document.querySelectorAll('.div_colunas_loc_2')
    let div_colunas_3 = document.querySelectorAll('.div_colunas_loc_3')
    let div_colunas_4 = document.querySelectorAll('.div_colunas_loc_4')
    let div_colunas_5 = document.querySelectorAll('.div_colunas_loc_5')
    let div_colunas_6 = document.querySelectorAll('.div_colunas_loc_6')

    let professores = document.querySelectorAll('.professores_loc')
    let locacoes = document.querySelectorAll('.locacoes')
    let check_in = document.querySelectorAll('.check_in')
    let check_out = document.querySelectorAll('.check_out')
    let qtds = document.querySelectorAll('.qtds_loc')
    let buton = document.querySelectorAll('.buton-x-loc')

    for(let k = 0; k < linhas.length; k++){
        $(linhas[k]).attr('id', 'linha_loc_'+(k+1))

        for(let i = 0; i <= 5; i++) {
            $(colunas_1[i]).attr('id', 'coluna_1_linha_loc_' + (k + 1))
            $(colunas_2[i]).attr('id', 'coluna_2_linha_loc_' + (k + 1))
            $(colunas_3[i]).attr('id', 'coluna_3_linha_loc_' + (k + 1))
            $(colunas_4[i]).attr('id', 'coluna_4_linha_loc_' + (k + 1))
            $(colunas_5[i]).attr('id', 'coluna_5_linha_loc_' + (k + 1))
            $(colunas_6[i]).attr('id', 'coluna_6_linha_loc_' + (k + 1))

            $(div_colunas_1[i]).attr('id', 'div_coluna_1_linha_loc_' + (k + 1))
            $(div_colunas_2[i]).attr('id', 'div_coluna_2_linha_loc_' + (k + 1))
            $(div_colunas_3[i]).attr('id', 'div_coluna_3_linha_loc_' + (k + 1))
            $(div_colunas_4[i]).attr('id', 'div_coluna_4_linha_loc_' + (k + 1))
            $(div_colunas_5[i]).attr('id', 'div_coluna_5_linha_loc_' + (k + 1))
            $(div_colunas_6[i]).attr('id', 'div_coluna_6_linha_loc_' + (k + 1))
        }

        $(professores[k]).attr('id', `prf_loc_${k+1}`).attr('name', `prf_loc_${k+1}`)

        $(locacoes[k]).attr('id', `ativ_${k+1}`).attr('name', `ativ_${k+1}`)
        $(check_in[k]).attr('id', `check_in_${k+1}`).attr('name', `check_in_${k+1}`)
        $(check_out[k]).attr('id', `check_out_${k+1}`).attr('name', `check_out_${k+1}`)
        $(qtds[k]).attr('id', `qtds_loc_${k+1}`).attr('name', `qtd_loc_${k+1}`)
        $(buton[k]).attr('id', `btn-loc_${k+1}`)
    }
}
function add_linha_atividade() {
    let i = criar_linhas_colunas()
    popular_professores(i)

    $(`#coluna_2_linha_${i+1}`).append(`<select class="form-control atividades" id="ativ_${i+1}" name="ativ_${i+1}"></select>`)
    $(`#coluna_3_linha_${i+1}`).append(`<input class="datas" type="datetime-local" id="data_hora_ativ${i+1}" name="data_hora_ativ_${i+1}"/>`)
    $(`#coluna_4_linha_${i+1}`).append(`<input class="qtds" type="number" id="qtd_ativ${i+1}" name="qtd_ativ_${i+1}"/>`)
    $(`#coluna_5_linha_${i+1}`).append(`<button class="buton-x-" id="btn_${i+1}" type="button" onClick="remover_linha(this)"><span><i class='bx bx-x' ></span></button>`)

    colocar_atividades(null, `ativ_${i+1}`)
}

// ------------------------------------------------------------------------------------------------------------------------------------
function criar_linhas_colunas_locacao(){
    let i = document.querySelectorAll('.linhas_loc').length

    $('#corpo_tabela_locacao').append(`<tr class="linhas_loc" id="linha_loc_${i+1}"></tr>`)
    $(`#linha_loc_${i+1}`).append(`<td class="div_colunas_loc_1" id="div_coluna_1_linha_loc_${i+1}"></td>`)
    $(`#div_coluna_1_linha_loc_${i+1}`).append(`<div class="colunas_loc_1" id="coluna_1_linha_loc_${i+1}"></div>`)
    $(`#linha_loc_${i+1}`).append(`<td class="div_colunas_loc_2" id="div_coluna_2_linha_loc_${i+1}"></td>`)
    $(`#div_coluna_2_linha_loc_${i+1}`).append(`<div class="colunas_loc_2" id="coluna_2_linha_loc_${i+1}"></div>`)
    $(`#linha_loc_${i+1}`).append(`<td class="div_colunas_loc_3" id="div_coluna_3_linha_loc_${i+1}"></td>`)
    $(`#div_coluna_3_linha_loc_${i+1}`).append(`<div class="colunas_loc_3" id="coluna_3_linha_loc_${i+1}"></div>`)
    $(`#linha_loc_${i+1}`).append(`<td class="div_colunas_loc_4" id="div_coluna_4_linha_loc_${i+1}"></td>`)
    $(`#div_coluna_4_linha_loc_${i+1}`).append(`<div class="colunas_loc_4" id="coluna_4_linha_loc_${i+1}"></div>`)
    $(`#linha_loc_${i+1}`).append(`<td class="div_colunas_loc_5" id="div_coluna_5_linha_loc_${i+1}"></td>`)
    $(`#div_coluna_5_linha_loc_${i+1}`).append(`<div class="colunas_loc_5" id="coluna_5_linha_loc_${i+1}"></div>`)
    $(`#linha_loc_${i+1}`).append(`<td class="div_colunas_loc_6" id="div_coluna_6_linha_loc_${i+1}"></td>`)
    $(`#div_coluna_6_linha_loc_${i+1}`).append(`<div class="colunas_loc_6" id="coluna_6_linha_loc_${i+1}"></div>`)

    return i
}

function add_linha_locacao(){
     let i = criar_linhas_colunas_locacao()
    popular_professores_locacao(i)

    $(`#coluna_2_linha_loc_${i + 1}`).append(`<select class="form-control locacoes" id="loc_${i + 1}" name="loc_${i + 1}" style="width: 110px"></select>`)
    $(`#coluna_3_linha_loc_${i + 1}`).append(`<input class="check_in" type="datetime-local" id="check_in_${i + 1}" name="check_in_${i + 1}" style="width: 210px"/>`)
    $(`#coluna_4_linha_loc_${i + 1}`).append(`<input class="check_out" type="datetime-local" id="check_out_${i + 1}" name="check_out_${i + 1}" style="width: 210px"/>`)
    $(`#coluna_5_linha_loc_${i + 1}`).append(`<input class="qtds_loc" type="number" id="qtd_loc${i + 1}" name="qtd_loc_${i + 1}"/>`)
    $(`#coluna_6_linha_loc_${i + 1}`).append(`<button class="buton-x-loc" id="btn-loc_${i + 1}" type="button" onClick="remover_linha_locacao(this)"><span><i class='bx bx-x' ></span></button>`)

    colocar_locacoes(null, `loc_${i+1}`)

}

function montar_tabela_locacoes(dados) {
    for (let i = 0; i < Object.keys(dados['locacoes']).length; i++) {
        criar_linhas_colunas_locacao()
        popular_professores_locacao(i)

        $(`#coluna_2_linha_loc_${i + 1}`).append(`<select class="form-control locacoes" id="loc_${i + 1}" name="loc_${i + 1}" style="width: 110px"></select>`)
        colocar_locacoes(dados['locacoes'][`locacao_${i + 1}`]['espaco'], `loc_${i + 1}`)

        let check_in = dados['locacoes'][`locacao_${i + 1}`]['check_in'].replace(' ', 'T')
        let check_out = dados['locacoes'][`locacao_${i + 1}`]['check_out'].replace(' ', 'T')
        $(`#coluna_3_linha_loc_${i + 1}`).append(`<input class="check_in" type="datetime-local" id="check_in_${i + 1}" name="check_in_${i + 1}" value="${check_in}" style="width: 210px"/>`)
        $(`#coluna_4_linha_loc_${i + 1}`).append(`<input class="check_out" type="datetime-local" id="check_out_${i + 1}" name="check_out_${i + 1}" value="${check_out}" style="width: 210px"/>`)
        $(`#coluna_5_linha_loc_${i + 1}`).append(`<input class="qtds_loc" type="number" id="qtd_loc${i + 1}" name="qtd_loc_${i + 1}" value="${dados['locacoes'][`locacao_${i + 1}`]['participantes']}"/>`)
        $(`#coluna_6_linha_loc_${i + 1}`).append(`<button class="buton-x-loc" id="btn-loc_${i + 1}" type="button" onClick="remover_linha_locacao(this)"><span><i class='bx bx-x' ></span></button>`)
    }
}