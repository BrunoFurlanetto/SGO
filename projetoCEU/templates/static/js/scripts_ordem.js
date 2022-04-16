
function completar_dados_os(selecao){
    $('.atividades').empty()
    $('.locacoes').empty()
    $('#id_ficha_de_evento').val(selecao.value)

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_ficha': selecao.value},
        success: function (response) {

            for(let i in response){
                $(`#${i}`).val(response[i])
            }

            $('#id_check_in').val(moment(response['id_check_in']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))
            $('#id_check_out').val(moment(response['id_check_out']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))

            if($('#id_serie').val() === ''){
                $('.colegios').addClass('none')
            }

            if(response['corporativo']){
                $('#id_tipo').val('Empresa')

            } else {
                $('#id_tipo').val('Colégio')
            }

            if(response['atividades_eco'] !== ''){
                $('.name').each(function (index, value){
                    for (let i in response['atividades_eco']){
                        if(value.textContent === response['atividades_eco'][i]){
                            value.parentElement.children[0].children[0].checked = true
                        }
                    }
                })
            }

            if(response['atividades_peraltas'] !== ''){
                $('.name').each(function (index, value){
                    for (let i in response['atividades_peraltas']){
                        if(value.textContent === response['atividades_peraltas'][i]){
                            value.parentElement.children[0].children[0].checked = true
                        }
                    }
                })
            }

            if(response['atividades_ceu'] !== ''){
                for(let i in response['atividades_ceu']){
                    add_atividade(parseInt(response['id_n_participantes']), parseInt(i), response['atividades_ceu'][i], response['id_serie'])
                }
            }

            if(response['locacoes_ceu'] !== ''){
                for(let i in response['locacoes_ceu']){
                    add_locacao(parseInt(i), response['locacoes_ceu'][i], parseInt(response['id_n_participantes']))
                }
            }

        }
    })
}

//  ------------------------------------------------- Fim das funcionalidades gerais da página ---------------------------------------------------------

// ------------------------------------------ Início das funcionalidades responsáveis pelas atividades -------------------------------------------------

/* Função responsável pela adição de uma nova atividade que será realizada no CEU */
function add_atividade(participantes_=parseInt(''), atividade_id_=parseInt(''), atividade_='', serie_=''){
    /* Ajax responsável por puxar as atividades do banco de dados */
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'tipo': 'Colégio'},
        success: function(response){
            // Variável responsável pelo indicie da nova atividade
            // a 'div_pai' é a div que ira receber todos os elementos relacionado a mesma atividade
            let i = document.querySelectorAll('.div_pai').length + 1

            // Adição da div pai na div de atividades no CEU
            $('.atividades').append(`<div class="row div_pai" id="div_pai_${i}"></div>`)

            // As div's de cada dado que precisára ser informad no momento do cadas
            let div_atividade = `<div class="mb-2 div-atividade" id="div_atividade_${i}" style="width: 46%"></div>`
            let div_data_hora = `<div class="mb-2 div-data" id="div_data_hora_atividade_${i}" style="width: 35%"></div>`
            let div_participantes = `<div class="mb-2 div-participantes" id="div_participantes_${i}" style="width: 15%"></div>`
            let div_icone = `<div class="my-0 div-icone" id="div_icone_${i}" style="width: 4%; margin-top: auto"></div>`
            let div_serie = `<div class="mb-2 colegios div_serie" id="div_serie_${i}" style="width: 50%"></div>`;

            // Adição das div's na div pai
            $(`#div_pai_${i}`).append(div_atividade, div_data_hora, div_participantes, div_icone, div_serie, `<hr class="barra" style="margin-left: 10px">`)

            //Criação dos elementos html necessários par o cadastro de uma nova atividade contratada pelo cliente
            let label_atividade = `<label>Atividade</label>`
            let select_atividade = `<select class="atividade" id="ativ_${i}" name="atividade_${i}" onchange="verificar_limitacoes(this)" required></select>`
            let label_data = `<label>Data e hora da atividade</label>`
            let data_hora_atividade = `<input class="hora_atividade" id="data_${i}" type="datetime-local" name="data_hora_${i}" onchange="verificar_limitacoes(this)" required/>`
            let label_participantes = `<label>QTD</label>`
            let participantes = `<input class="qtd_participantes" id="participantes_${i}" type="number" name="participantes_${i}" onchange="verificar_limitacoes(this)" required value="${participantes_}"/>`
            let label_serie = `<label>Serie</label>`
            let serie = `<input class="serie_participantes" id="serie_${i}" type="text" name="serie_participantes_${i}" value="${serie_}"/>`

            // Adição dos elemntos em suas respectivas div's
            $(`#div_atividade_${i}`).append(label_atividade, select_atividade)
            $(`#div_data_hora_atividade_${i}`).append(label_data, data_hora_atividade)
            $(`#div_participantes_${i}`).append(label_participantes, participantes)
            $(`#div_serie_${i}`).append(label_serie, serie)

            // Todas as atividades que serão dcionadas no select da atividade
            for (let j in response['dados']) {
                if(response['dados'][j] != atividade_) {
                    $(`#ativ_${i}`).append(`<option value="${j}">${response['dados'][j]}</option>`)
                }
            }

            // Adição das opções no select
            $(`#ativ_${i}`).prepend(`<option selected value="${atividade_id_}">${atividade_}</option>`)

            // Criação e adição do botão responsável por excluir uma atividade iniciada
            $(`#div_icone_${i}`).append(`<button class="buton-x" id="btn_${i}" type="button" onClick="remover_atividade(this)">`)
            $(`#btn_${i}`).append(`<span id="spn_${i}"><i class='bx bx-x'></i></span>`)

        }
    })

}
// Função responsável pela remoção de uma atividade já iniciada e
// renumeração dos id's e nomes dos elementos pai e filho
function remover_atividade(selecao){
    $(`#div_pai_${selecao.id.split('_')[1]}`).remove() // Remoção do elemento selecionado

    // Seleção de todas as div's a ser renumeradas/renomeadas
    let divs_pai = document.querySelectorAll('.div_pai')
    let divs_atividades = document.querySelectorAll('.div-atividade')
    let divs_data = document.querySelectorAll('.div-data')
    let divs_participantes = document.querySelectorAll('.div-participantes')
    let divs_icones = document.querySelectorAll('.div-icone')
    let divs_serie = document.querySelectorAll('.div_serie')

    // Seleção dos elementos que serão renumerados/renomeados
    let select_atividade = document.querySelectorAll('.atividade')
    let hora_atividade = document.querySelectorAll('.hora_atividade')
    let qtd_atividade = document.querySelectorAll('.qtd_participantes')
    let icone = document.querySelectorAll('.buton-x')
    let serie = document.querySelectorAll('.serie_participantes')

    // Renumeração/renomeação das div's e elementos antes selecionados
    for(let k = 0; k <= divs_pai.length; k++) {
        // Começa trabalhando em cima das div's
        $(divs_pai[k]).attr('id', 'div_pai_'+(k+1));
        $(divs_atividades[k]).attr('id', 'div_atividade_'+(k+1));
        $(divs_data[k]).attr('id', 'div_data_hora_atividade_'+(k+1));
        $(divs_participantes[k]).attr('id', 'div_participantes_'+(k+1));
        $(divs_icones[k]).attr('id', 'div_icone_'+(k+1));
        $(divs_serie[k]).attr('id', 'div_serie_'+(k+1));

        // Então passa a renumeração/renomeação dos elementos
        $(select_atividade[k]).attr('id', `ativ_${k+1}`).attr('name', `atividade_${k+1}`);
        $(hora_atividade[k]).attr('name', 'data_hora_'+(k+1));
        $(qtd_atividade[k]).attr('name', 'participantes_'+(k+1));
        $(icone[k]).attr('id', 'btn_'+(k+1));
        $(serie[k]).attr('name', 'serie_participantes_'+(k+1));
    }

}

// Função responsável por verificar as limitações da atividades sendo cadastrada.
// Verifica tanto número de participantes máximo e mínimo para a atividade acontecer,
// quanto o horário que ela ta sendo cadastrada, necessário por haver atividades que
// não podem acontecer durante a noite ou durante o dia.
function verificar_limitacoes(selecao) {
    // Seleção dos valores necessários para as verificações
    let participantes = $(`#participantes_${selecao.id.split('_')[1]}`).val()
    let atividade = $(`#ativ_${selecao.id.split('_')[1]}`).val()
    let data_atividade = $(`#data_${selecao.id.split('_')[1]}`).val()

    // É preciso ter selecionado a atividade antes de prosseguir com a verificação
    // isso porque o ajax vai mandar a atividade para receber todas as limitações e números de participantes
    if (atividade !== '') {
        $.ajax({
            type: 'POST',
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {"atividade": atividade},
            success: function (response) {
                // Participantes máximo da atividade em questão
                var limite = response['participantes_maximo']

                // A primeira verificação é do horário
                if(data_atividade !== ''){

                    // Horário informado durante o cadastro da atividade
                    let hora_atividade = parseFloat(data_atividade.split('T')[1].replace(':', '.'))

                    // Verificando se o horário informado é durante a noite. Como o sol se põe e nasce em horários
                    // diferentes ao longo do ano, é apenas lançado um aviso para verificar isso
                    if (response['limitacoes'].includes('Não pode acontecer durante a noite')) {
                        if (hora_atividade < 7.00 || hora_atividade >= 18.00) {

                            if(hora_atividade >= 19){
                                $(`#alert_noite_${selecao.id.split('_')[1]}`).remove()
                                $(`#div_pai_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-danger"  id="alert_noite_${selecao.id.split('_')[1]}" style="margin-left: 10px">A atividade não pode ser realizada no horário informado!</p>`)
                                $(`#data_${selecao.id.split('_')[1]}`).val('')
                            } else {
                                $(`#alert_noite_${selecao.id.split('_')[1]}`).remove()
                                $(`#div_pai_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-warning"  id="alert_noite_${selecao.id.split('_')[1]}" style="margin-left: 10px">Verificar se atividade pode ser realizada no horário informado!</p>`)
                            }

                        } else {
                            $(`#alert_noite_${selecao.id.split('_')[1]}`).remove()
                        }
                    }

                    // Verificando se o horário informado é durante o dia. Como o sol se põe e nasce em horários
                    // diferentes ao longo do ano, é apenas lançado um aviso para verificar isso
                    if (response['limitacoes'].includes('Não pode acontecer durante o dia')) {
                        if (hora_atividade <= 20) {

                            if (hora_atividade <= 18) {
                                $(`#alert_dia_${selecao.id.split('_')[1]}`).remove()
                                $(`#div_pai_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-danger" id="alert_dia_${selecao.id.split('_')[1]}" style="margin-left: 10px">A atividade não pode ser realizada o horário informado!</p>`)
                                $(`#data_${selecao.id.split('_')[1]}`).val('')
                            } else {
                                $(`#alert_dia_${selecao.id.split('_')[1]}`).remove()
                                $(`#div_pai_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-warning" id="alert_dia_${selecao.id.split('_')[1]}" style="margin-left: 10px">Verificar se atividade pode ser realizada no horário informado!</p>`)
                            }

                        } else {
                            $(`#alert_dia_${selecao.id.split('_')[1]}`).remove()
                        }
                    }
                }

                // Verificação de número de participantes
                if(participantes !== ''){

                    // Verifica se o número de participantes está acima do mínimo para a atividade acontecer.
                    // É lançado apenas um aviso.
                    if(participantes < response['participantes_minimo']){
                        $(`#div_pai_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-danger" id="alert_participantes_${selecao.id.split('_')[1]}" style="margin-left: 10px">Participantes abaixo do mínimo necessário para a atividade cadsatrada!</p>`)
                    } else {
                        $(`#alert_participantes_${selecao.id.split('_')[1]}`).remove()
                    }

                    // Verifica se o número de participantes está acimsa do limite de lotação.
                    // Essa verificação já chama a função responsável pela divisão das turmas, já que é uma limitação física.
                    if(participantes > limite){
                        dividar_atividade(selecao.id.split('_')[1], limite)
                        $(`#div_pai_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-warning" style="margin-left: 10px">O grupo foi dividido por execeder a lotação máxima!</p>`)
                    }
                }
            }
        })
    }
}

// Função responsável pela divisão das turmas caso a lotação máxima seja excedida
function dividar_atividade(indicie, limite){
    let participantes_apx, k, aproximado, sobra;
    // Pegando os valores necessários para a divisão
    let qtd = $(`#participantes_${indicie}`)
    let atividade_ = $(`#ativ_${indicie} :selected`).text()
    let atividade_value_ = $(`#ativ_${indicie}`).val()
    let serie_ = $(`#serie_${indicie}`).val()

    // Aqui é feito uma verificação do número de turmas necessário
    for(k = 2; k > 1; k++){

        // Vê se o número e turmas já é o suficiente
        if(qtd.val() / k <= limite){
            // Aproximação necessária para não haver número fracionado
            participantes_apx = Math.trunc(qtd.val() / k)
            // Booleano para dizer se houve aproximação
            aproximado = qtd.val() / k !== participantes_apx
            // Paticipantes sobrando devido a aproximação, caso tenha acontecido
            sobra = qtd.val() - (participantes_apx * k)
            break
        }

    }

    // Troca do número de participantes da atividade já inicado
    if (aproximado){
        qtd.val(participantes_apx + 1)
    } else {
        qtd.val(participantes_apx)
    }

    // Looping para adcionar o número de turmas que faltam
    for (let j = 1; j < k; j++) {
        // Variável do número de participantes das turmas
        let participantes_ = participantes_apx

        // Caso haja participantes sobrando pelo arredondamento é adcionado nas primeiras turmas
        if(j < sobra){
            participantes_ = participantes_apx + 1
        }
        // Chama a função para adcionar atividades e manda os vlores da turma
        add_atividade(participantes_, atividade_value_, atividade_, serie_)
    }

}
// ------------------------------------------ Final das funções que trabalham com atividades ------------------------------------

// ----------------------------------------- Início das funções que trabalham com as locações -----------------------------------

// Função responsável por adicionar uma nova locação
function add_locacao(id_local_=parseInt(''), local_='', qtd_=parseInt('')){
    // Ajax responsável por puxar todas as estruturas do banco de dados

    if(isNaN(qtd_)){
        qtd_ = ($('#id_n_participantes').val())
    }

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'tipo': 'Empresa'},
        success: function(response){
            // A partir daqui os processos dessa parte são semelhantes a função de adcionar atividade,
            // com alguns elementos a mais, importante para a locação.
            let i = document.querySelectorAll('.div_pai_loc').length + 1

            $('.locacoes').append(`<div class="row div_pai_loc" id="div_pai_loc_${i}"></div>`)

            let div_locacao = `<div class="mb-2 div-locacao" id="div_locacao_${i}" style="width: 25%"></div>`
            let div_entrada = `<div class="mb-2 div-entrada-loc" id="div_entrada_${i}" style="width: 35%"></div>`
            let div_saida = `<div class="mb-2 div-saida-loc" id="div_saida_${i}" style="width: 35%"></div>`
            let div_participantes_loc = `<div class="mb-2 div-participantes-loc" id="div_participantes_loc_${i}" style="width: 15%"></div>`
            let div_local_coffee = `<div class="mb-2 div-local-coffee" id="div_local_coffee_${i}" style="width: 50%"></div>`
            let div_hora_coffee = `<div class="mb-2 div-hora-coffee" id="div_hora_coffee_${i}" style="width: 20%"></div>`
            let div_icone_loc = `<div class="my-0 div-icone-loc" id="div_icone_loc_${i}" style="width: 4%; margin-top: auto"></div>`


            $(`#div_pai_loc_${i}`).append(div_locacao, div_entrada, div_saida, div_icone_loc, div_local_coffee, div_hora_coffee, div_participantes_loc, `<hr class="barra" style="margin-left: 10px">`)

            let label_locacao = `<label>Locação</label>`
            let select_locacao = `<select class="locacao" id="loc_${i}" name="locacao_${i}" onchange="verificar_lotacao(this)" required value=""></select>`
            let label_entrada = `<label>Check in</label>`
            let entrada = `<input class="entrada" id="entrada_${i}" type="datetime-local" name="entrada_${i}" onchange="verificar_lotacao(this)" required/>`
            let label_saida = `<label>Check out</label>`
            let saida = `<input class="saida" id="saida_${i}" type="datetime-local" name="saida_${i}" onchange="verificar_lotacao(this)" required/>`
            let label_local_coffee = `<label>Local do coffee</label>`
            let local_coffee = `<input class="local_coffee" id="local-coffee_${i}" type="text" name="local-coffee_${i}"/>`
            let label_hora_coffee = `<label>Hora</label>`
            let hora_coffee = `<input class="hora_coffee" id="hora-coffee_${i}" type="time" name="hora-coffee_${i}" onchange="verificar_lotacao(this)"/>`
            let label_participantes_loc = `<label>QTD</label>`
            let participantes_loc = `<input class="qtd_participantes_loc" id="participantes-loc_${i}" type="number" name="participantes-loc_${i}" onchange="verificar_lotacao(this)" required value="${qtd_}"/>`

            $(`#div_locacao_${i}`).append(label_locacao, select_locacao)
            $(`#div_entrada_${i}`).append(label_entrada, entrada)
            $(`#div_saida_${i}`).append(label_saida, saida)
            $(`#div_local_coffee_${i}`).append(label_local_coffee, local_coffee)
            $(`#div_hora_coffee_${i}`).append(label_hora_coffee, hora_coffee)
            $(`#div_participantes_loc_${i}`).append(label_participantes_loc, participantes_loc)

            for (let j in response) {
                $(`#loc_${i}`).append(`<option value="${j}">${response[j]}</option>`)
            }

            $(`#loc_${i}`).prepend(`<option selected value="${id_local_}">${local_}</option>`)

            $(`#div_icone_loc_${i}`).append(`<button class="buton-x buton-loc" id="btn-loc_${i}" type="button" onClick="remover_locacao(this)">`)
            $(`#btn-loc_${i}`).append(`<span id="spn_loc${i}"><i class='bx bx-x'></i></span>`)

        }
    })

}

// Função semelhante a de remover atividade, mas para a parte de locação
function remover_locacao(selecao){
    console.log(selecao.id.split('_')[1])
    $(`#div_pai_loc_${selecao.id.split('_')[1]}`).remove()

    let divs_pai_loc = document.querySelectorAll('.div_pai_loc')
    let divs_locacoes = document.querySelectorAll('.div-locacao')
    let divs_entrada = document.querySelectorAll('.div-entrada-loc')
    let divs_saida = document.querySelectorAll('.div-saida-loc')
    let divs_local_coffee = document.querySelectorAll('.div-local-coffee')
    let divs_hora_coffee = document.querySelectorAll('.div-hora-coffee')
    let divs_participantes_loc = document.querySelectorAll('.div-participantes-loc')
    let divs_icones_loc = document.querySelectorAll('.div-icone-loc')

    let select_locacao = document.querySelectorAll('.locacao')
    let entrada = document.querySelectorAll('.entrada')
    let saida = document.querySelectorAll('.saida')
    let local_coffee = document.querySelectorAll('.local_coffee')
    let hora_coffee = document.querySelectorAll('.hora_coffee')
    let participantes_lo = document.querySelectorAll('.qtd_participantes_loc')
    let icone_loc = document.querySelectorAll('.buton-loc')

    for(let k = 0; k <= divs_pai_loc.length; k++) {
        $(divs_pai_loc[k]).attr('id', 'div_pai_loc'+(k+1));
        $(divs_locacoes[k]).attr('id', 'div_locacao_'+(k+1));
        $(divs_entrada[k]).attr('id', 'div_entrada_'+(k+1));
        $(divs_saida[k]).attr('id', 'div_saida_'+(k+1));
        $(divs_local_coffee[k]).attr('id', 'div_local_coffee_'+(k+1));
        $(divs_hora_coffee[k]).attr('id', 'div_hora_coffee_'+(k+1));
        $(divs_participantes_loc[k]).attr('id', 'div-hora-coffee_'+(k+1));
        $(divs_icones_loc[k]).attr('id', 'div_icone_loc_'+(k+1));

        $(select_locacao[k]).attr('id', `loc_${k+1}`).attr('name', `locacao_${k+1}`);
        $(entrada[k]).attr('id', `entrada_${k+1}`).attr('name', `entrada_${k+1}`);
        $(saida[k]).attr('id',`saida_${k+1}`).attr('name', 'saida_'+(k+1));
        $(local_coffee[k]).attr('id', `local-coffee_${k+1}`).attr('name', 'local-coffee_'+(k+1));
        $(hora_coffee[k]).attr('id', `hora-coffee_${k+1}`).attr('name', 'hora-coffee_'+(k+1));
        $(participantes_lo[k]).attr('id', `participantes-loc_${k+1}`).attr('name', 'participantes-loc_'+(k+1));
        $(icone_loc[k]).attr('id', 'btn-loc_'+(k+1));
    }

}
// Responsável pela verificação da lotação da estrutura
function verificar_lotacao(selecao){
    let participantes = $(`#participantes-loc_${selecao.id.split('_')[1]}`).val()
    let locacao = $(`#loc_${selecao.id.split('_')[1]}`).val()

    console.log(selecao.id.split('_')[1])

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'local': locacao},
        success: function(response){

            if(locacao !== ''){

                // Verifica se a lotação informada excede 70% da lotação máxima do prédio e lança
                // um alerta para pedindo a verificação de uma nova lotação caso haja uma disposição
                // de mesas e cadeiras diferente
                if(participantes > (response['lotacao'] * 0.7)){

                    if(participantes > response['lotacao']){
                        $(`#div_pai_loc_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-danger" id="alert_participantes_loc_${selecao.id.split('_')[1]}" style="margin-left: 10px">Lotação máxima da sala ultrapassada!</p>`)
                        $(`#participantes-loc_${selecao.id.split('_')[1]}`).empty()
                    } else {
                        $(`#alert_participantes_loc_${selecao.id.split('_')[1]}`).remove()
                        $(`#div_pai_loc_${selecao.id.split('_')[1]}`).prepend(`<p class="alert-danger" id="alert_participantes_loc_${selecao.id.split('_')[1]}" style="margin-left: 10px">Lotação acima de 70%. Necessário verificação acerca da disposição da sala!</p>`)
                    }

                } else {
                    $(`#alert_participantes_loc_${selecao.id.split('_')[1]}`).remove()
                }
            }
        }
    })
}

// Scripts da parte de visialização da ordem de serviço

function dadosVerOrdem(){

    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'id_ordem_de_servico': $('#id_ordem').val()},
        success: function (response) {
            $('#id_check_in').val(moment(response['check_in']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))
            $('#id_check_out').val(moment(response['check_out']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))

            if(response['atividades_ceu']){
                for(let i in response['atividades_ceu']){
                    add_atividade(response['atividades_ceu'][i]['participantes'], response['atividades_ceu'][i]['id_atividade'], response['atividades_ceu'][i]['atividade'], response['atividades_ceu'][i]['serie'])
                    setTimeout(() => {
                        for(let j = 1; j <= Object.keys(response['atividades_ceu']).length; j++) {
                            $(`#data_${j}`).val(moment(response['atividades_ceu'][i]['data_e_hora']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))
                        }
                    }, 100)
                }
            } else {
                $('.atividade-ceu').addClass('none')
            }

            if(response['locacoes_ceu']){
                let j = 1
                for (let i in response['locacoes_ceu']) {
                    add_locacao(response['locacoes_ceu'][i]['id_espaco'], response['locacoes_ceu'][i]['espaco'], response['locacoes_ceu'][i]['participantes'])
                    setTimeout(() => {
                        $(`#entrada_${j}`).val((moment(response['locacoes_ceu'][i]['check_in']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm')))
                        $(`#saida_${j}`).val((moment(response['locacoes_ceu'][i]['check_out']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm')))
                        $(`#local-coffee_${j}`).val(response['locacoes_ceu'][i]['local_coffee'])
                        $(`#hora-coffee_${j}`).val(response['locacoes_ceu'][i]['hora_coffee'])
                        j++
                    }, 150)
                }

            } else {
                $('.locacao-ceu').addClass('none')
            }
        }
    })

    //Cronograma
    if($('.cronograma-cliente').children('a').prop('href')) {
        $('.cliente-cronograma').append(`<a href="${$('.cronograma-cliente').children('a').prop('href')}">Cronograma do grupo</a>`)
    } else {
        $('.cliente-cronograma').addClass('none')
    }

    //Observações
    if($('#id_observacoes').val() === ''){
        $('.observacoes').addClass('none')
    }
}

function edita_os(){
    let ver_os = $('#ver_os')
    $('#fieldset_form').prop('disabled', false)
    $('.salvar').prop('disabled', false)
    ver_os.removeClass('conteudo-ver-os')
    ver_os.addClass('conteudo-os')
    $('.atividades_eco_os, .buton-plus, .atividade-ceu, .atividades_peraltas_os, .cronograma-cliente, .locacao-ceu').removeClass('none')
    $('.cliente-cronograma, .p-atividades-eco, .p-atividades-peraltas').addClass('none')
    atividades_eco_peraltas_selecionadas()
}

function atividades_eco_peraltas_selecionadas(){
    let atividades_eco = $('#atividades_ecoturismo_os').text().split(', ')
    let atividades_peraltas = $('#atividades_peraltas_os').text().split(', ')

    $('.name').each(function (index, value){
        for (let i = 0; i < atividades_eco.length; i++){
            if(value.textContent === atividades_eco[i]){
                value.parentElement.children[0].children[0].checked = true
            }
        }
        for (let i = 0; i < atividades_peraltas.length; i++){
            if(value.textContent === atividades_peraltas[i]){
                value.parentElement.children[0].children[0].checked = true
            }
        }
    })
}
function teste(){

    // $('.cont').children('div').children('input').prop('checked', true)
}