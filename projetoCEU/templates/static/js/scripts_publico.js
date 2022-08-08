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
        $($(`#${selecao.id}`).parent().parent().parent()).prepend(`<td colspan="5" class="alert-danger" id="alert"><center>Professor não escalado</center></td>`)
        $(`#${selecao.id}`).val('')
    } else {
        $('#alert').remove()
    }
}

function colocar_atividades(atividade, id) {
    // - atividade: Atividade realizada pelo grupo
    // - id: Linha da tabela que vai ser adicionado a atividade

    // Verificação para saber qual opção ficará selecionada inicialmente
    // Isso para o caso de vir a chamada da função principal
    let id_atividade

    if (atividade != null) {
        $(`#${id}`).append(`<option></option>`)
    } else {
        $(`#${id}`).append(`<option selected></option>`)
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'atividade', 'publico': true},
        success: function (response) {

            for (let k in response) {
                // Verificação para não adicionar duas vezes a mesma atividade
                $(`#${id}`).append(`<option value="${k}">${response[k]}</option>`)

                if (atividade == response[k]){
                    id_atividade = k
                }

            }

            $(`#${id}`).val(id_atividade)

        }
    })
}

function criar_linhas_colunas(){
    let i = document.querySelectorAll('.linhas').length// Número de linhas já existentes na tabela

    $('#corpo_tabela_atividade_publico').append(
        `<tr class="linhas" id="linha_${i+1}">
            <td class="coluna_1" id="coluna_1_linha_${i + 1}"></td>
            <td class="coluna_2" id="coluna_2_linha_${i + 1}"></td>
            <td class="coluna_3" id="coluna_3_linha_${i + 1}"></td>
            <td class="coluna_4" id="coluna_4_linha_${i + 1}"></td>
        </tr>`
    )

    return i
}

function popular_professores(i){
    // No caso das atividades são criados 4 select's por atividade
    for(let j = 0; j < 4; j++) {
        // Faz a verificação para poder deixar o campo requerido para 2 professores
        if(j < 1) {
            $(`#coluna_1_linha_${i + 1}`).append(`<select id="prf${j + 1}atv${i + 1}" class="professores" name="prf${j + 1}atv${i + 1}" style="width: 23%" onchange="validacao(this)" required></select>`)
            $(`#prf${j + 1}atv${i + 1}`).append(`<option selected></option>`)
        } else {
            $(`#coluna_1_linha_${i + 1}`).append(`<select id="prf${j + 1}atv${i + 1}" class="professores" name="prf${j + 1}atv${i + 1}" style="width: 23%" onchange="validacao(this)"></select>`)
            $(`#prf${j + 1}atv${i + 1}`).append(`<option selected></option>`)
        }
    }

     $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'professor'},
        success: function (response) {
            // Adição de todos os nomes de professores cadastrados na base de dados
            for(let k in response){
                for(let j = 0; j < 4; j++) {
                    $(`#prf${j + 1}atv${i + 1}`).append(`<option value="${k}">${response[k]}</option>`)
                }
            }
        }
     })
}

function add_linha_atividade() {
    let i = criar_linhas_colunas() // Cria a linha e as colunas
    popular_professores(i) // Cria e popula os select's de professores

    // Crianção dos elementos da atividade, data/hora, quantidade e botão
    $(`#coluna_2_linha_${i+1}`).append(`<input class="horas" type="time" style="width: 100px" id="horaAtividade${ i+1 }" name="horaAtividade_${ i+1 }" onchange="validarTabelaPublico()"/>`)
    $(`#coluna_3_linha_${i+1}`).append(`<select class="atividades" style="width: 100%" name="ativ${ i+1 }" id="ativ${ i+1 }" onchange="validarTabelaPublico()"></select>`)
    $(`#coluna_4_linha_${i+1}`).append(`<button type="button" id="btn_${ i+1 }" class="btn-close" style="height: 2px; width: 1px" onclick="remover_linha(this)"></button>`)

    colocar_atividades(null, `ativ${i+1}`) // Populando o select das atividades
}

// Função necessária para a remoção e renumeração das linhas da tabela de atividades
function remover_linha(selecao){
    $(`#linha_${selecao.id.split('_')[1]}`).remove() // Remoção da linha selecionada

    // Seleção de todas as linhas, colunas e div's da tabela de atividades
    let linhas = document.querySelectorAll('.linhas')
    let coluna_1 = document.querySelectorAll('.coluna_1')
    let coluna_2 = document.querySelectorAll('.coluna_2')
    let coluna_3 = document.querySelectorAll('.coluna_3')
    let coluna_4 = document.querySelectorAll('.coluna_4')

    // Seleção dos elementos
    let professores = document.querySelectorAll('.professores')
    let atividades = document.querySelectorAll('.atividades')
    let datas = document.querySelectorAll('.horas')
    let buton = document.querySelectorAll('.btn-close')

    // Renumeração de todos os elementos
    for(let k = 0; k < linhas.length; k++){
        $(linhas[k]).attr('id', 'linha_'+(k+1)) // Renumeração das linhas

        // Renumeração de todas as colunas
        $(coluna_1[k]).attr('id', 'coluna_1_linha_' + (k + 1))
        $(coluna_2[k]).attr('id', 'coluna_2_linha_' + (k + 1))
        $(coluna_3[k]).attr('id', 'coluna_3_linha_' + (k + 1))
        $(coluna_4[k]).attr('id', 'coluna_4_linha_' + (k + 1))

        // Renumeração dos atributos dos professores. É necessário toda uma lógica para
        // que a renumeração seja feita corretamente, devido há presença de 4 selects por linha
        for(let j = 0; j < 4; j++) {
            $(professores[j+(k*4)]).attr('id', `prf_${(j+1)}_ativ_${k+1}`).attr('name', `prf_${j+2}_ativ_${k+1}`)
        }

        // Renumeração dos atributos dos demais elementos
        $(atividades[k]).attr('id', `ativ_${k+1}`).attr('name', `ativ_${k+1}`)
        $(datas[k]).attr('id', `data_hora_ativ${k+1}`).attr('name', `data_hora_ativ_${k+1}`)
        $(buton[k]).attr('id', `btn_${k+1}`)
    }
}