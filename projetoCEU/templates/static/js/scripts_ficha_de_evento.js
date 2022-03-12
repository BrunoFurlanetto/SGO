
/* Função responsável pelo aparecimento da div de informações de colégio */
function verifica_colegio(selecao){
    let dados_colegio = document.querySelector(".colegios");
    let dados_colegio_barra = document.querySelector(".colegios_barra");

    if (selecao.value === 'Colégio'){
        dados_colegio.classList.remove('none')
        dados_colegio_barra.classList.remove('none')
    } else {
        dados_colegio.classList.add('none')
        dados_colegio_barra.classList.add('none')
    }
}

/* Função responsável pela adição de uma nova atividade que será realizada no CEU */
function add_atividade(){
    /* Ajax responsável por puxar todas as atividades do banco de dados */
    $.ajax({
        type: 'GET',
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        success: function(response){
            let i = document.querySelectorAll('.div_pai').length + 1
            console.log(i)
            $('.atividades').append(`<div class="row div_pai" id="div_pai_${i}"></div>`)

            let div_atividade = `<div class="mb-2" id="div_atividade_${i}" style="width: 50%"></div>`
            let div_data_hora = `<div class="mb-2" id="div_data_hora_atividade_${i}" style="width: 42%"></div>`
            let div_icone = `<div class="mt-4" id="div_icone_${i}" style="width: 4%; margin-top: auto"></div>`

            $(`#div_pai_${i}`).append(div_atividade, div_data_hora, div_icone)

            let label_atividade = `<label>Atividade</label>`
            let select_atividade = `<select class="atividade" id="ativ_${i}" name="atividade_${i}" ></select>`
            let label_data = `<label>Data e hora da atividade</label>`
            let data_hora_atividade = `<input type="datetime-local" name="data_hora_atividade_${i}"/>`

            $(`#div_atividade_${i}`).append(label_atividade, select_atividade)
            $(`#div_data_hora_atividade_${i}`).append(label_data, data_hora_atividade)

            for (let j in response['dados']) {
                $(`#ativ_${i}`).append(`<option value="${j}">${response['dados'][j]}</option>`)
            }

            $(`#ativ_${i}`).prepend(`<option selected></option>`)

            $(`#div_icone_${i}`).append(`<button class="buton-x" id="btn_${i}" type="button" onClick="remover_atividade(this)">`)
            $(`#btn_${i}`).append(`<span id="spn_${i}"></span>`)
            $(`#spn_${i}`).append(`<i class='bx bx-x'></i>`)

        }
    })

}

function remover_atividade(selecao){
    $(`#div_pai_${selecao.id.split('_')[1]}`).remove()

    let divs_pai = document.querySelectorAll('.div_pai')
    console.log(divs_pai)

    for(let k = 0; k <= divs_pai.length; k++) {
        $(divs_pai[k]).attr('id', 'div_pai_'+(k+1));
    }
    let dp = document.querySelectorAll('.div_pai')

}
