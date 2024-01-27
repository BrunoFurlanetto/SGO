// Função principal de tod o o arquivo, responável por preenchar todos os dados
// já existêntes na ficha de evento
// Função para verificar se o check da locação/atividade está ativo
$('document').ready(function () {
    $('#id_coordenador_peraltas').select2({'style': "pointer-events: none"})
})
function check_locacao(){
    if($("#checkAtividade").is(":checked")){
        $('#tabela').removeClass('none')
    }else{
        $('#tabela').addClass('none')
    }
}

// Responsável por preencher todo o cabeçalho dos relatórios com as informações
// do grupo, pega da ficha de evento
// Responsável por verificar o número mínimo de professores por atividade
function verificar_n_professores(){
    let linhas = document.querySelectorAll('.linhas').length

    for(let linha = 1; linha <= linhas; linha++){

        // Com excessão do planetário, todas as outras atividades precisam de ao menos um professor
        if($(`#ativ_${linha} :selected`).text() == 'Planetário'){
            $(`#prof_2_ativ_${linha}`).prop('required', false)
        }
    }
}

// Função responsável por não deixar colcoar professor não escalado nas atividades
function validacao(selecao){
    let professor = selecao.value

    let coordenador = $('#coordenador').val()
    let professor_2 = $('#professor_2').val()
    let professor_3 = $('#professor_3').val()
    let professor_4 = $('#professor_4').val()
    let professor_5 = $('#professor_5').val()

    if(professor !== coordenador && professor !== professor_2 && professor !== professor_3 && professor !== professor_4 && professor !== professor_5){
        $('#alert').remove()
        $($(`#${selecao.id}`).parent().parent().parent().parent()).prepend(`<td colspan="5" class="alert-danger" id="alert"><center>Professor não escalado</center></td>`)
        $(`#${selecao.id}`).val('')
    } else {
        $('#alert').remove()
    }


}

// -------------------- Funçõe úteis para as tabelas de atividades -------------------------

// Cria as linhas e colunas das tabelas de atividades, para receber os inputs
function criar_linhas_colunas(){
    let i = document.querySelectorAll('.linhas').length// Número de linhas já existentes na tabela

    $('#corpo_tabela_atividade').append(
        `<tr class="linhas" id="linha_${i+1}" style="vertical-align: middle">
            <td class="colunas_1" id="coluna_1_linha_${i+1}" style="display: flex; flex-wrap: wrap"></td>
            <td class="colunas_2" id="coluna_2_linha_${i+1}"></td>
            <td class="colunas_3" id="coluna_3_linha_${i+1}"></td>
            <td class="colunas_4" id="coluna_4_linha_${i+1}"></td>
            <td class="colunas_5" id="coluna_5_linha_${i+1}"></td>
        </tr>`
    )

    return i
}

// Responsável por popular os select's dos professores na tabela
function popular_professores(i){

    // No caso das atividades é são criados 4 select's por atividade
    for(let j = 0; j < 4; j++) {

        // Faz a verificação pra poder deixar o campo requerido para 2 professores
        if(j < 1) {
            $(`#coluna_1_linha_${i + 1}`).append(`<select class="professores" id="prof_${j + 1}_ativ_${i + 1}" name="professores_ativ_${i + 1}" style="width: 45%; margin: 2px;" onchange="validacao(this)" required></select>`)
            $(`#prof_${j + 1}_ativ_${i + 1}`).append(`<option selected></option>`)
        } else {
            $(`#coluna_1_linha_${i + 1}`).append(`<select class="professores" id="prof_${j + 1}_ativ_${i + 1}" name="professores_ativ_${i + 1}" style="width: 45%; margin: 2px;" onchange="validacao(this)"></select>`)
            $(`#prof_${j + 1}_ativ_${i + 1}`).append(`<option selected></option>`)
        }
    }

     $.ajax({
        type: 'POST',
        url: '/cadastro/colegio/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'professor'},
        success: function (response) {

            // Adição de todos os nomes de professores cadastrados na base de dados
            for(let k in response){

                for(let j = 0; j < 4; j++) {
                    $(`#prof_${j + 1}_ativ_${i + 1}`).append(`<option value="${k}">${response[k]}</option>`)
                }

            }
        }
     })
}

// Função responsável por montar toda a tabela de atividades
function montar_tabela_atividades(dados){
    for (let i = 0; i < Object.keys(dados['atividades']).length; i++) {
        criar_linhas_colunas() // Função responsável pela crianção da primeira linha e as colunas
        popular_professores(i) // Cria e popula os select's de professores

        // Coluna 2: Referênte as atividades realizadas pelo grupo
        $(`#coluna_2_linha_${i + 1}`).append(`<select class="atividades" id="ativ_${i + 1}" name="ativ_${i + 1}" onchange="verificar_n_professores()" required></select>`)
        colocar_atividades(dados['atividades'][`atividade_${i + 1}`]['atividade'], `ativ_${i + 1}`) // Responsável pela crianção dos selects e população com as atividades

        // Coluna 3: Referênte a data e hora da atividade
        let data = dados['atividades'][`atividade_${i + 1}`]['data_e_hora'].replace(' ', 'T') // Replace necessário pelo formato que a data é salvo no BD inicialmente
        $(`#coluna_3_linha_${i + 1}`).append(`<input class="datas" type="datetime-local" id="data_hora_ativ${i + 1}" name="ativ_${i + 1}" value="${data}" required/>`)

        // Coluna 4: Referênte a quantidade por atividade
        $(`#coluna_4_linha_${i + 1}`).append(`<input class="qtds" type="number" id="qtd_ativ${i + 1}" name="ativ_${i + 1}" value="${dados['atividades'][`atividade_${i + 1}`]['participantes']}" required/>`)

        // Coluna 5: Botão para exclusão da linha da tabela
        $(`#coluna_5_linha_${i + 1}`).append(`<button class="buton-x-" id="btn_${i + 1}" type="button" onClick="remover_linha(this)"><span><i class='bx bx-x'></i></span></button>`)
    }
}

// Função responsável pela criação do select e população com as atividades do BD
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
        url: '/cadastro/colegio/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'atividade'},
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

// Função necessária para a remoção e renumeração das linhas da tabela de atividades
function remover_linha(selecao){
    $(`#linha_${selecao.id.split('_')[1]}`).remove() // Remoção da linha selecionada
    console.log($(`#linha_${selecao.id.split('_')[1]}`))
    // Seleção de todas as linhas, colunas e div's da tabela de atividades
    let linhas = document.querySelectorAll('.linhas')
    let colunas_1 = document.querySelectorAll('.colunas_1')
    let colunas_2 = document.querySelectorAll('.colunas_2')
    let colunas_3 = document.querySelectorAll('.colunas_3')
    let colunas_4 = document.querySelectorAll('.colunas_4')
    let colunas_5 = document.querySelectorAll('.colunas_5')

    // Seleção dos elementos
    let professores = document.querySelectorAll('.professores')
    let atividades = document.querySelectorAll('.atividades')
    let datas = document.querySelectorAll('.datas')
    let qtds = document.querySelectorAll('.qtds')
    let buton = document.querySelectorAll('.buton-x-')

    // Renumeração de todos os elementos
    for(let k = 0; k < linhas.length; k++){
        $(linhas[k]).attr('id', 'linha_'+(k+1)) // Renumeração das linhas

        // Renumeração de todas as colunas
        $(colunas_1[k]).attr('id', 'coluna_1_linha_' + (k + 1))
        $(colunas_2[k]).attr('id', 'coluna_2_linha_' + (k + 1))
        $(colunas_3[k]).attr('id', 'coluna_3_linha_' + (k + 1))
        $(colunas_4[k]).attr('id', 'coluna_4_linha_' + (k + 1))
        $(colunas_5[k]).attr('id', 'coluna_5_linha_' + (k + 1))

        // Renumeração dos atributos dos professores. É necessário toda uma lógica para
        // que a renumeração seja feita corretamente, devido há presença de 4 selects por linha
        for(let j = 0; j < 4; j++) {
            $(professores[j+(k*4)]).attr('id', `prf_${(j+1)}_ativ_${k+1}`).attr('name', `professores_ativ_${k+1}`)
        }

        // Renumeração dos atributos dos demais elementos
        $(atividades[k]).attr('id', `ativ_${k+1}`).attr('name', `ativ_${k+1}`)
        $(datas[k]).attr('id', `data_hora_ativ${k+1}`).attr('name', `ativ_${k+1}`)
        $(qtds[k]).attr('id', `qtd_ativ${k+1}`).attr('name', `ativ_${k+1}`)
        $(buton[k]).attr('id', `btn_${k+1}`)
    }
}

// Função resposável pela adição de uma nova linha na tabela de atividades quando clicado no botão
function add_linha_atividade() {
    let i = criar_linhas_colunas() // Cria a linha e as colunas
    popular_professores(i) // Cria e popula os select's de professores

    // Crianção dos elementos da atividade, data/hora, quantidade e botão
    $(`#coluna_2_linha_${i+1}`).append(`<select class="atividades" id="ativ_${i+1}" name="ativ_${i+1}" onchange="verificar_n_professores()" required></select>`)
    $(`#coluna_3_linha_${i+1}`).append(`<input class="datas" type="datetime-local" id="data_hora_ativ${i+1}" name="ativ_${i+1}" required/>`)
    $(`#coluna_4_linha_${i+1}`).append(`<input class="qtds" type="number" id="qtd_ativ${i+1}" name="ativ_${i+1}" required/>`)
    $(`#coluna_5_linha_${i+1}`).append(`<button class="buton-x-" id="btn_${i+1}" type="button" onClick="remover_linha(this)"><span><i class='bx bx-x' ></span></button>`)

    colocar_atividades(null, `ativ_${i+1}`) // Populão o select das atividades
}

// ------------------------------------ Funções utéis para a montagem da parte de locação -------------------------------------

// Função responsável pela criação da linhas e colunas da tabela de locação
// Função semelhante com a responsável pela tabela de atividades
function criar_linhas_colunas_locacao(){
    let i = document.querySelectorAll('.linhas_loc').length

    $('#corpo_tabela_locacao').append(
        `<tr class="linhas_loc" id="linha_loc_${i+1}" style="vertical-align: middle">
            <td class="colunas_loc_1" id="coluna_1_linha_loc_${i+1}"></td>
            <td class="colunas_loc_2" id="coluna_2_linha_loc_${i+1}"></td>
            <td class="colunas_loc_3" id="coluna_3_linha_loc_${i+1}"></td>
            <td class="colunas_loc_4" id="coluna_4_linha_loc_${i+1}"></td>
            <td class="colunas_loc_5" id="coluna_5_linha_loc_${i+1}"></td>
            <td class="colunas_loc_6" id="coluna_6_linha_loc_${i+1}"></td>
        </tr>`
    )

    return i
}

// Função responsável por popular tod o os selects de professores da table ade locação
function popular_professores_locacao(i){

    // Nesse caso é apenas um professor por locação
    $(`#coluna_1_linha_loc_${i+1}`).append(`<select class="form-control escalados professores_loc" id="prof_loc_${i + 1}" name="professores_locacao_${i + 1}" onchange="validacao(this)" required></select>`)
    $(`#prof_loc_${i+1}`).append(`<option selected></option>`)

    $.ajax({
        type: 'POST',
        url: '/cadastro/empresa/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'professor'},
        success: function (response) {
            // Adição de todos os nome da base de dados
            for(let k in response) {
                $(`#prof_loc_${i + 1}`).append(`<option value="${k}">${response[k]}</option>`)
            }
        }
    })
}

// Função necessária para a criação e população dos select's da locação
function colocar_locacoes(local, id){
    // - local: Local locado pelo grupo
    // - id: Linha da tabela que vai ser adicionado a locação

    // A partir de agora tem as mesmas funcionalidades da função de atividade
    console.log(local)
    if (local != null) {
        $(`#${id}`).append(`<option></option>`)
    } else {
        $(`#${id}`).append(`<option selected></option>`)
    }

    let id_local

    $.ajax({
        type: 'POST',
        url: '/cadastro/empresa/',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'campo': 'locacao'},
        success: function (response) {

            for (let k in response) {
                // Verificação para não adicionar duas vezes a mesma atividade
                $(`#${id}`).append(`<option value="${k}">${response[k]}</option>`)

                if (local === response[k]){
                    id_local = k
                }

            }

            $(`#${id}`).val(id_local)
        }
    })
}

// Responsável pea adção individual de uma nova linha na tabla de locação e criação de todos os elementos
// Semelhante a sua respectiva função da tabela atividades
function add_linha_locacao(){
    let i = criar_linhas_colunas_locacao()
    popular_professores_locacao(i)

    $(`#coluna_2_linha_loc_${i + 1}`).append(`<select class="form-control locacoes" id="loc_${i + 1}" name="loc_${i + 1}" required></select>`)
    $(`#coluna_3_linha_loc_${i + 1}`).append(`<input class="check_in" type="datetime-local" id="check_in_${i + 1}" name="loc_${i + 1}" required/>`)
    $(`#coluna_4_linha_loc_${i + 1}`).append(`<input class="check_out" type="datetime-local" id="check_out_${i + 1}" name="loc_${i + 1}" required/>`)
    $(`#coluna_5_linha_loc_${i + 1}`).append(`<input class="qtds_loc" type="number" id="qtd_loc${i + 1}" name="loc_${i + 1}" required/>`)
    $(`#coluna_6_linha_loc_${i + 1}`).append(`<button class="buton-x-loc" id="btn-loc_${i + 1}" type="button" onClick="remover_linha_locacao(this)"><span><i class='bx bx-x'></i></span></button>`)

    colocar_locacoes(null, `loc_${i+1}`)
}

// Responsável por montar a tabela de locação
// Funcionamento semelhante ao da tabela de atividades
function montar_tabela_locacoes(dados) {
    for (let i = 0; i < Object.keys(dados['locacoes']).length; i++) {
        criar_linhas_colunas_locacao()
        popular_professores_locacao(i)

        $(`#coluna_2_linha_loc_${i + 1}`).append(`<select class="form-control locacoes" id="loc_${i + 1}" name="loc_${i + 1}" required></select>`)
        colocar_locacoes(dados['locacoes'][`locacao_${i + 1}`]['espaco'], `loc_${i + 1}`)

        let check_in = dados['locacoes'][`locacao_${i + 1}`]['check_in'].replace(' ', 'T')
        let check_out = dados['locacoes'][`locacao_${i + 1}`]['check_out'].replace(' ', 'T')
        $(`#coluna_3_linha_loc_${i + 1}`).append(`<input class="check_in" type="datetime-local" id="check_in_${i + 1}" name="loc_${i + 1}" style="width: 200px" value="${check_in}" required/>`)
        $(`#coluna_4_linha_loc_${i + 1}`).append(`<input class="check_out" type="datetime-local" id="check_out_${i + 1}" name="loc_${i + 1}" style="width: 200px" value="${check_out}" required/>`)
        $(`#coluna_5_linha_loc_${i + 1}`).append(`<input class="qtds_loc" type="number" id="qtd_loc${i + 1}" name="loc_${i + 1}" value="${dados['locacoes'][`locacao_${i + 1}`]['participantes']}" required/>`)
        $(`#coluna_6_linha_loc_${i + 1}`).append(`<button class="buton-x-loc" id="btn-loc_${i + 1}" type="button" onClick="remover_linha_locacao(this)"><span><i class='bx bx-x' ></span></button>`)
    }
}

// Responsável pela exclusão e renumeração das linhas da tabela de locação
function remover_linha_locacao(selecao){
    // Essa função segue a lógica parecida com a função relacionada a tabela de atividades
    // coma a adição das colunas de check in e check out
    $(`#linha_loc_${selecao.id.split('_')[1]}`).remove()

    let linhas = document.querySelectorAll('.linhas_loc')
    let colunas_1 = document.querySelectorAll('.colunas_loc_1')
    let colunas_2 = document.querySelectorAll('.colunas_loc_2')
    let colunas_3 = document.querySelectorAll('.colunas_loc_3')
    let colunas_4 = document.querySelectorAll('.colunas_loc_4')
    let colunas_5 = document.querySelectorAll('.colunas_loc_5')
    let colunas_6 = document.querySelectorAll('.colunas_loc_6')

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
        }

        $(professores[k]).attr('id', `prf_loc_${k+1}`).attr('name', `professores_loc_${k+1}`)
        $(locacoes[k]).attr('id', `loc_${k+1}`).attr('name', `loc_${k+1}`)
        $(check_in[k]).attr('id', `check_in_${k+1}`).attr('name', `loc_${k+1}`)
        $(check_out[k]).attr('id', `check_out_${k+1}`).attr('name', `loc_${k+1}`)
        $(qtds[k]).attr('id', `qtds_loc_${k+1}`).attr('name', `loc_${k+1}`)
        $(buton[k]).attr('id', `btn-loc_${k+1}`)
    }
}

function abrir_modal(){
    $(window).on('load',function(){
        $('#modal_dados_usuario_colegio').modal('show')
    });
}