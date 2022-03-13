
/* Função responsável pelo aparecimento da div de informações de colégio */
// noinspection JSJQueryEfficiency

function verifica_colegio(selecao){
    let dados_colegio = document.querySelectorAll(".colegios")
    let tipo_empresa = document.querySelector('.locacao-ceu')
    let tipo_colegio = document.querySelector('.atividade-ceu')

    if (selecao.value === 'Colégio'){
        tipo_colegio.classList.remove('none')

        for(let l = 0; l < dados_colegio.length; l++) {
            dados_colegio[l].classList.remove('none')
        }

        tipo_empresa.classList.add('none')

    } else {
        tipo_colegio.classList.add('none')

        for(let l = 0; l < dados_colegio.length; l++) {
            dados_colegio[l].classList.add('none')
        }

        if(selecao.value === 'Empresa'){
            tipo_empresa.classList.remove('none')
        } else {
            tipo_empresa.classList.add('none')
        }

    }
}
function mostrar_locacao(){
    let locacao_ceu = document.querySelector('.locacao-ceu')
    locacao_ceu.classList.toggle('none')
}
function mostrar_atividade(){
    let atividade_ceu = document.querySelector('.atividade-ceu')
    atividade_ceu.classList.toggle('none')
}

/* Função responsável pela adição de uma nova atividade que será realizada no CEU */
function add_atividade(){
    /* Ajax responsável por puxar todas as atividades do banco de dados */
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'tipo': 'Colégio'},
        success: function(response){
            console.log(response)

            let i = document.querySelectorAll('.div_pai').length + 1

            $('.atividades').append(`<div class="row div_pai" id="div_pai_${i}"></div>`)

            let div_atividade = `<div class="mb-2 div-atividade" id="div_atividade_${i}" style="width: 46%"></div>`
            let div_data_hora = `<div class="mb-2 div-data" id="div_data_hora_atividade_${i}" style="width: 35%"></div>`
            let div_participantes = `<div class="mb-2 div-participantes" id="div_participantes_${i}" style="width: 15%"></div>`
            let div_icone = `<div class="my-0 div-icone" id="div_icone_${i}" style="width: 4%; margin-top: auto"></div>`
            let div_serie = `<div class="mb-2 colegios div_serie" id="div_serie_${i}" style="width: 50%"></div>`;

            $(`#div_pai_${i}`).append(div_atividade, div_data_hora, div_participantes, div_icone, div_serie, `<hr class="barra" style="margin-left: 10px">`)

            let label_atividade = `<label>Atividade</label>`
            let select_atividade = `<select class="atividade" id="ativ_${i}" name="atividade_${i}" onchange="verificar_limitacoes(this)" required></select>`
            let label_data = `<label>Data e hora da atividade</label>`
            let data_hora_atividade = `<input class="hora_atividade" id="data_${i}" type="datetime-local" name="data_hora_atividade_${i}" onchange="verificar_limitacoes(this)" required/>`
            let label_participantes = `<label>QTD</label>`
            let participantes = `<input class="qtd_participantes" id="participantes_${i}" type="number" name="participantes_${i}" onchange="verificar_limitacoes(this)" required/>`
            let label_serie = `<label>Serie</label>`
            let serie = `<input class="serie_participantes" id="serie_${i}" type="text" name="serie_participantes_${i}"/>`

            $(`#div_atividade_${i}`).append(label_atividade, select_atividade)
            $(`#div_data_hora_atividade_${i}`).append(label_data, data_hora_atividade)
            $(`#div_participantes_${i}`).append(label_participantes, participantes)
            $(`#div_serie_${i}`).append(label_serie, serie)

            for (let j in response['dados']) {
                $(`#ativ_${i}`).append(`<option value="${j}">${response['dados'][j]}</option>`)
            }

            $(`#ativ_${i}`).prepend(`<option selected></option>`)

            $(`#div_icone_${i}`).append(`<button class="buton-x" id="btn_${i}" type="button" onClick="remover_atividade(this)">`)
            $(`#btn_${i}`).append(`<span id="spn_${i}"><i class='bx bx-x'></i></span>`)

        }
    })

}

function remover_atividade(selecao){
    $(`#div_pai_${selecao.id.split('_')[1]}`).remove()

    let divs_pai = document.querySelectorAll('.div_pai')
    let divs_atividades = document.querySelectorAll('.div-atividade')
    let divs_data = document.querySelectorAll('.div-data')
    let divs_participantes = document.querySelectorAll('.div-participantes')
    let divs_icones = document.querySelectorAll('.div-icone')
    let divs_serie = document.querySelectorAll('.div_serie')

    let select_atividade = document.querySelectorAll('.atividade')
    let hora_atividade = document.querySelectorAll('.hora_atividade')
    let qtd_atividade = document.querySelectorAll('.qtd_participantes')
    let icone = document.querySelectorAll('.buton-x')
    let serie = document.querySelectorAll('.serie_participantes')

    for(let k = 0; k <= divs_pai.length; k++) {
        $(divs_pai[k]).attr('id', 'div_pai_'+(k+1));
        $(divs_atividades[k]).attr('id', 'div_atividade_'+(k+1));
        $(divs_data[k]).attr('id', 'div_data_hora_atividade_'+(k+1));
        $(divs_participantes[k]).attr('id', 'div_participantes_'+(k+1));
        $(divs_icones[k]).attr('id', 'div_icone_'+(k+1));
        $(divs_serie[k]).attr('id', 'div_serie_'+(k+1));

        $(select_atividade[k]).attr('id', `ativ_${k+1}`, 'name', `atividade_${k+1}`);
        $(hora_atividade[k]).attr('name', 'data_hora_atividade_'+(k+1));
        $(qtd_atividade[k]).attr('name', 'participantes_'+(k+1));
        $(icone[k]).attr('id', 'btn_'+(k+1));
        $(serie[k]).attr('name', 'serie_participantes_'+(k+1));
    }

}

function verificar_limitacoes(selecao) {
    let participantes = $(`#participantes_${selecao.id.split('_')[1]}`).val()
    let atividade = $(`#ativ_${selecao.id.split('_')[1]}`).val()
    let teste = $(`#ativ_${selecao.id.split('_')[1]}`).text()
    console.log(teste)
    let data_atividade = $(`#data_${selecao.id.split('_')[1]}`).val()

    if (atividade !== '') {

        $.ajax({
            type: 'POST',
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            data: {"atividade": atividade},
            success: function (response) {
                console.log(response)

                if(data_atividade !== ''){

                    let hora_atividade = parseFloat(data_atividade.split('T')[1].replace(':', '.'))

                    if (response['limitacoes'].includes('Não pode acontecer durante a noite')) {
                        if (hora_atividade < 7.00 || hora_atividade >= 18.00) {
                            alert('Atividade selecionada não pode acontecer durante a noite, verifique se no horário informado ainda terá sol!')
                        }
                    }

                    if (response['limitacoes'].includes('Não pode acontecer em local abert')) {
                        if (hora_atividade > 7.00 && hora_atividade <= 19.30) {
                            alert('Atividade selecionada não pode acontecer durante o dia, verifique se a atividade selecionada pode acontecer nesse horário!')
                        }
                    }
                }

                if(participantes !== ''){

                    if(participantes < response['participantes_minimo']){
                        alert('A quantidade de participantes cadastrado é menor do que o mínimo pra atividade selecionada acontecer (' + response['participantes_minimo'] + ')!' )
                    }

                    if(participantes > response['participantes_maximo']){
                        dividar_atividade(selecao.id.split('_')[1])
                        alert('A quantidade de participantes cadastrado é menor do que o mínimo pra atividade selecionada acontecer (' + response['participantes_maximo'] + ')!')
                    }
                }
            }
        })
    }
}

function dividar_atividade(indicie){
    let qtd = $(`#participantes_${indicie}`)
    let atividade_ = $(`#ativ_${indicie} :selected`).text()
    let atividade_value_ = $(`#ativ_${indicie}`).val()
    let participantes_ = qtd.val() / 2
    let serie_ = $(`#serie_${indicie}`).val()

    qtd.val(participantes_)

    let div_serie;
    let i = document.querySelectorAll('.div_pai').length + 1

    $('.atividades').append(`<div class="row div_pai" id="div_pai_${i}"></div>`)

    let div_atividade = `<div class="mb-2 div-atividade" id="div_atividade_${i}" style="width: 46%"></div>`
    let div_data_hora = `<div class="mb-2 div-data" id="div_data_hora_atividade_${i}" style="width: 35%"></div>`
    let div_participantes = `<div class="mb-2 div-participantes" id="div_participantes_${i}" style="width: 15%"></div>`
    let div_icone = `<div class="my-0 div-icone" id="div_icone_${i}" style="width: 4%; margin-top: auto"></div>`

    if($('#id_tipo').val() === 'Colégio'){
        div_serie = `<div class="mb-2 colegios div_serie" id="div_serie_${i}" style="width: 50%"></div>`;
    }else{
        div_serie = `<div class="mb-2 colegios div_serie none" id="div_serie_${i}" style="width: 50%"></div>`;
    }

    $(`#div_pai_${i}`).append(div_atividade, div_data_hora,div_participantes, div_icone, div_serie, `<hr class="barra" style="margin-left: 10px">`)

    let label_atividade = `<label>Atividade</label>`
    let select_atividade = `<select class="atividade" id="ativ_${i}" name="atividade_${i}" onchange="verificar_limitacoes(this)" required></select>`
    let label_data = `<label>Data e hora da atividade</label>`
    let data_hora_atividade = `<input class="hora_atividade" id="data_${i}" type="datetime-local" name="data_hora_atividade_${i}" onchange="verificar_limitacoes(this)" required/>`
    let label_participantes = `<label>QTD</label>`
    let participantes = `<input class="qtd_participantes" id="participantes_${i}" type="number" name="participantes_${i}" onchange="verificar_limitacoes(this)" value="${participantes_}" required/>`
    let label_serie = `<label>Serie</label>`
    let serie = `<input class="serie_participantes" type="text" name="serie_participantes_${i}" value="${serie_}"/>`

    $(`#div_atividade_${i}`).append(label_atividade, select_atividade)
    $(`#div_data_hora_atividade_${i}`).append(label_data, data_hora_atividade)
    $(`#div_participantes_${i}`).append(label_participantes, participantes)
    $(`#div_serie_${i}`).append(label_serie, serie)

    $(`#ativ_${i}`).prepend(`<option value="${atividade_value_}">${atividade_}</option>`)

    $(`#div_icone_${i}`).append(`<button class="buton-x" id="btn_${i}" type="button" onClick="remover_atividade(this)">`)
    $(`#btn_${i}`).append(`<span id="spn_${i}"><i class='bx bx-x'></i></span>`)

}


function add_locacao(){
    /* Ajax responsável por puxar todas as atividades do banco de dados */
    $.ajax({
        type: 'POST',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {'tipo': 'Empresa'},
        success: function(response){
            console.log(response)

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
            let select_locacao = `<select class="locacao" id="loc_${i}" name="locacao_${i}" onchange="verificar_limitacoes(this)" required></select>`
            let label_entrada = `<label>Check in</label>`
            let entrada = `<input class="entrada" id="entrada_${i}" type="datetime-local" name="entrada_${i}" onchange="verificar_limitacoes(this)" required/>`
            let label_saida = `<label>Check out</label>`
            let saida = `<input class="saida" id="saida_${i}" type="datetime-local" name="saida_${i}" onchange="verificar_limitacoes(this)" required/>`
            let label_local_coffee = `<label>Local do coffee</label>`
            let local_coffee = `<input class="local_coffee" id="local_coffee_${i}" type="text" name="local_coffee_${i}"/>`
            let label_hora_coffee = `<label>Hora</label>`
            let hora_coffee = `<input class="hora_coffee" id="hora_coffee_${i}" type="time" name="hora_coffee_${i}" onchange="verificar_limitacoes(this)" required/>`
            let label_participantes_loc = `<label>QTD</label>`
            let participantes_loc = `<input class="qtd_participantes" id="participantes_${i}" type="number" name="participantes_${i}" onchange="verificar_limitacoes(this)" required/>`

            $(`#div_locacao_${i}`).append(label_locacao, select_locacao)
            $(`#div_entrada_${i}`).append(label_entrada, entrada)
            $(`#div_saida_${i}`).append(label_saida, saida)
            $(`#div_local_coffee_${i}`).append(label_local_coffee, local_coffee)
            $(`#div_hora_coffee_${i}`).append(label_hora_coffee, hora_coffee)
            $(`#div_participantes_loc_${i}`).append(label_participantes_loc, participantes_loc)

            for (let j in response) {
                $(`#loc_${i}`).append(`<option value="${j}">${response[j]}</option>`)
            }

            $(`#loc_${i}`).prepend(`<option selected></option>`)

            $(`#div_icone_loc_${i}`).append(`<button class="buton-x" id="btn_loc_${i}" type="button" onClick="remover_locacao(this)">`)
            $(`#btn_loc_${i}`).append(`<span id="spn_loc${i}"><i class='bx bx-x'></i></span>`)

        }
    })

}

function remover_locacao(selecao){
    console.log(selecao.id.split('_')[2])
    $(`#div_pai_loc_${selecao.id.split('_')[2]}`).remove()

    let divs_pai_loc = document.querySelectorAll('.div_pai_loc')
    let divs_locacoes = document.querySelectorAll('.div-locacao')
    let divs_data = document.querySelectorAll('.div-data')
    let divs_participantes = document.querySelectorAll('.div-participantes')
    let divs_icones = document.querySelectorAll('.div-icone')
    let divs_serie = document.querySelectorAll('.div_serie')

    let select_atividade = document.querySelectorAll('.atividade')
    let hora_atividade = document.querySelectorAll('.hora_atividade')
    let qtd_atividade = document.querySelectorAll('.qtd_participantes')
    let icone = document.querySelectorAll('.buton-x')
    let serie = document.querySelectorAll('.serie_participantes')

    for(let k = 0; k <= divs_pai.length; k++) {
        $(divs_pai[k]).attr('id', 'div_pai_'+(k+1));
        $(divs_atividades[k]).attr('id', 'div_atividade_'+(k+1));
        $(divs_data[k]).attr('id', 'div_data_hora_atividade_'+(k+1));
        $(divs_participantes[k]).attr('id', 'div_participantes_'+(k+1));
        $(divs_icones[k]).attr('id', 'div_icone_'+(k+1));
        $(divs_serie[k]).attr('id', 'div_serie_'+(k+1));

        $(select_atividade[k]).attr('id', `ativ_${k+1}`, 'name', `atividade_${k+1}`);
        $(hora_atividade[k]).attr('name', 'data_hora_atividade_'+(k+1));
        $(qtd_atividade[k]).attr('name', 'participantes_'+(k+1));
        $(icone[k]).attr('id', 'btn_'+(k+1));
        $(serie[k]).attr('name', 'serie_participantes_'+(k+1));
    }

}
