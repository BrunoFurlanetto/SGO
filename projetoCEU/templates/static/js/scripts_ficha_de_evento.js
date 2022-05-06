function encaminhamento(){
    localStorage.setItem("encaminhado", true)
}

function teste(){
    for(let i = 0; i < $('#id_produto').children('div').length; i++){
            verQuantidades($(`#id_produto_${i}`))
        }
}

function verQuantidades(id_produto){
    if(id_produto.is(':checked')){
        $.ajax({
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: {'id_produto': id_produto.val()},
            success: function (response) {

                if(response['so_ceu']){
                    $('.peraltas').addClass('none')
                }

                if(response['colegio']){
                    $('.professores').removeClass('none')
                    if(response['outro']){
                        $('.outro-produto').removeClass('none')
                    }

                    if(response['pernoite']){
                        $('.alunos-pernoite, .professores-pernoite').removeClass('none')
                    }

                    if(response['vt']){
                        $('.alunos-pernoite').addClass('none')
                    }

                } else {
                    $('.corporativo').removeClass('none')
                }
            }
        })
    } else {
        $('.alunos-pernoite, .professores-pernoite, .corporativo, .professores, .outro-produto').addClass('none')
        $('.peraltas').removeClass('none')
    }
}

function pegarDias(){
    if($('#id_check_in').val() !== '' && $('#id_check_out').val() !== ''){
        const data_1 = $('#id_check_in').val().split('T')[0]
        const data_2 = $('#id_check_out').val().split('T')[0]
        var intervalo = moment(data_2,"YYYY-MM-DD").diff(moment(data_1,"YYYY-MM-DD"));
        var dias = moment.duration(intervalo).asDays();

        $('#corpo-tabela-refeicao').empty()

        for(let i = 0; i <= dias; i++){
            add_refeicao(moment(data_1).add(i, 'days').format('YYYY-MM-DD'))
        }

    }
}

function obs(){
    $('#observacoes_refeicoes').toggleClass('none')
}

function add_refeicao(data=null){
    let i = document.querySelectorAll('.linha').length

    $('#corpo-tabela-refeicao').append(`<tr class="linha" id="linha_${i+1}"></tr>`)

    let linha = document.querySelector(`#linha_${i+1}`)

    $(linha).append(`<td><input type="date" class="data" name="data_refeicao_${i+1}" style="width:  180px" value="${data}"></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input cafe" id="cafe_${i+1}" name="cafe_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input coffee_m" id="coffee_m_${i+1}" name="coffee_m_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input almoco" id="almoco_${i+1}" name="almoco_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input lanche_t" id="lanche_t_${i+1}" name="lanche_t_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input coffee_t" id="coffee_t_${i+1}" name="coffee_t_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input jantar" id="jantar_${i+1}" name="jantar_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input lanche_n" id="lanche_n_${i+1}" name="lanche_n_${i+1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><button class="buton-x-ref" id="btn-ref_${i + 1}" type="button" onClick="remover_dia_refeicao(this)"><span><i class='bx bx-x' ></span></button></center></td>`)
}

function remover_dia_refeicao(selecao){
    $(`#linha_${selecao.id.split('_')[1]}`).remove()

    let n_linhas = document.querySelectorAll('.linha').length

    let linhas = document.querySelectorAll('.linha')
    let datas = document.querySelectorAll('.data')
    let cafes = document.querySelectorAll('.cafe')
    let coffes_m = document.querySelectorAll('.coffee_m')
    let almocos = document.querySelectorAll('.almoco')
    let lanches_t = document.querySelectorAll('.lanche_t')
    let coffees_t = document.querySelectorAll('.coffee_t')
    let jantares = document.querySelectorAll('.jantar')
    let lanches_n = document.querySelectorAll('.lanche_n')
    let butons = document.querySelectorAll('.buton-x-ref')

    for(let k = 0; k <= n_linhas; k++){
        $(linhas[k]).attr('id', `linha_${k+1}`)
        $(datas[k]).attr('id', `data_${k+1}`).attr('name', `data_refeicao_${k+1}`)
        $(cafes[k]).attr('id', `cafe_${k+1}`).attr('name', `cafe_${k+1}`)
        $(coffes_m[k]).attr('id', `coffee_m_${k+1}`).attr('name', `coffee_m_${k+1}`)
        $(almocos[k]).attr('id', `almoco_${k+1}`).attr('name', `almoco_${k+1}`)
        $(lanches_t[k]).attr('id', `lanche_t_${k+1}`).attr('name', `lanche_t_${k+1}`)
        $(coffees_t[k]).attr('id', `coffee_t_${k+1}`).attr('name', `coffee_t_${k+1}`)
        $(jantares[k]).attr('id', `jantar_${k+1}`).attr('name', `jantar_${k+1}`)
        $(lanches_n[k]).attr('id', `lanche_n_${k+1}`).attr('name', `lanche_n_${k+1}`)
        $(butons[k]).attr('id', `btn-ref_${k+1}`).attr('name', `btn-ref_${k+1}`)
    }
}

function pegarEndereco(){
    if($('#id_transporte').prop('checked')){
        $('#endereco_embarque, #terceirizado').removeClass('none')
    } else {
        $('#endereco_embarque, #terceirizado').addClass('none')
    }
}

function servicoBordo(){
    if($('#id_etiquetas_embarque').prop('checked')){
        $('#servico_de_bordo').removeClass('none')
    } else {
        $('#servico_de_bordo').addClass('none')
    }
}

function pegar_atividades_eco(){
    $('#biologo .MultiCheckBoxDetailBody').empty()

    $('#atividades_ecoturismo .cont').each(function (index, value){

        if (value.children[0].children[0].checked){
            let div_nova = $(value).clone()

            $('#biologo .MultiCheckBoxDetailBody').append(div_nova)
            $('#biologo .cont').children('div').children().prop('checked', false)

        }

    })

}

function quaisAtividades(){
    if($('#id_biologo').prop('checked')){
        $('#quais_atividades').removeClass('none')
    } else {
        $('#quais_atividades').addClass('none')
    }
}

function horario(selecao){
    if(selecao.value === '2'){
        $('#horario').removeClass('none')
    } else {
        $('#horario').addClass('none')
    }
}
function pegarIdInfosAdicionais(){
    if($('#id_informacoes_adcionais').val() !== ''){
        $('#infos').append(`<input type="hidden" name="id_infos_adicionais" value="${$('#id_informacoes_adcionais').val()}"/>`)
    }
}

jQuery('document').ready(function() {
  jQuery('#infos').submit(function() {
    var dados = jQuery(this).serialize();
    var url = $(this).attr('action');

    $.ajax({
      url: url,
      headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
      type: "POST",
      data: dados,
      success: function(response) {
          $('#id_informacoes_adcionais').val(response['id'])
          $('#modal-adicionais').modal('hide')

          if($('#id_informacoes_adcionais')){
              $('#info_adicionais_ok').prop('checked', true)
          }

          if(response['mensagem']){
              $('#corpo_site').prepend(response['mensagem'])
          }

      }
    });

    return false;
  });
});

function pegarIdCodigosApp(){

    if($('#id_codigos_app').val() !== ''){
        $('#codigos_app').append(`<input type="hidden" name="id_codigo_app" value="${$('#id_codigos_app').val()}"/>`)
    }
}

$('document').ready(function() {
  jQuery('#codigos_app').submit(function() {
    var dados = jQuery(this).serialize();
    //aqui voce pega o conteudo do atributo action do form
    var url = $(this).attr('action');
    $.ajax({
      url: url,
      headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
      type: "POST",
      data: dados,
      success: function(response) {
          $('#id_codigos_app').val(response['id'])
          $('#modal_codigos_app').modal('hide')

          if($('#id_codigos_app')){
              $('#codigos_app_ok').prop('checked', true)
          }
      }
    });

    return false;
  });
});

// -------------------------- Máscaras ---------------------------------

$(document).ready(function() {
    // CNPJ
    $('#search-input').mask("99.999.999/9999-99")
})

// Visualização Ficha de evento

function completar_visualizacao_ficha(id_ficha){
    if($('#id_observacoes').val() === ''){
        $('.observacoes-ver-ficha').addClass('none')
    }

    $('#info_adicionais_ok, #codigos_app_ok').prop('checked', true)

    $.ajax({
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "POST",
        data: {'id_ficha_de_evento': id_ficha},
        success: function (response) {
            $('#cliente').val(response['cliente'])
            $('#responsavel').val(response['responsavel'])

            $('#id_check_in').val(moment(response['check_in']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))
            $('#id_check_out').val(moment(response['check_out']).tz('America/Sao_Paulo').format('yyyy-MM-DDTHH:mm'))
            pegarDias()

            if(!response['perfil']){
                $('.perfil-participantes-ver-ficha').addClass('none')
            }

            for(let refeicao in response['refeicoes']){
                $(`#${response['refeicoes'][refeicao]}`).prop('checked', true)
            }

            if(response['obs_refeicoes']){
                $('#observacoes_refeicoes').removeClass('none')
            }

            if(Object.keys(response['atividades_eco']).length !== 0){
                let atividades_eco = []
                $('.name').each(function (index, value){
                    for (let i in response['atividades_eco']){
                        if(value.textContent === response['atividades_eco'][i]){
                            value.parentElement.children[0].children[0].checked = true
                            atividades_eco.push(response['atividades_eco'][i])
                        }
                    }
                })
                $('#atividades_peraltas_ficha').append(`<div id="lista_atividades_eco"><h5 class="titulo-secao">Ecoturismo</h5><p>${atividades_eco}</p><hr></div>`)
            }

            if(Object.keys(response['atividades_peraltas']).length !== 0){
                let atividades_peraltas = []
                $('.name').each(function (index, value){
                    for (let i in response['atividades_peraltas']){
                        if(value.textContent === response['atividades_peraltas'][i]){
                            value.parentElement.children[0].children[0].checked = true
                            atividades_peraltas.push(response['atividades_peraltas'][i])
                        }
                    }
                })
                $('#atividades_peraltas_ficha').append(`<div id="lista_atividades_peraltas"><h5 class="titulo-secao">Acampamento</h5><p>${atividades_peraltas}</p><hr></div>`)
            }

            if(Object.keys(response['atividades_ceu']).length !== 0){
                let atividades_ceu = []
                $('.name').each(function (index, value){
                    for (let i in response['atividades_ceu']){
                        if(value.textContent === response['atividades_ceu'][i]){
                            value.parentElement.children[0].children[0].checked = true
                            atividades_ceu.push(response['atividades_ceu'][i])
                        }
                    }
                })
                $('#ceu').append(`<div id="lista_atividades_ceu"><h5 class="titulo-secao">Atividades no CEU</h5><p>${atividades_ceu}</p><hr></div>`)
            }
            console.log(response)
            if(Object.keys(response['locacoes_ceu']).length !== 0){
                let locacoes_ceu = []
                $('.name').each(function (index, value){
                    for (let i in response['locacoes_ceu']){
                        if(value.textContent === response['locacoes_ceu'][i]){
                            value.parentElement.children[0].children[0].checked = true
                            locacoes_ceu.push(response['locacoes_ceu'][i])
                        }
                    }
                })
                $('#ceu').append(`<div id="lista_locacoes_ceu"><h5 class="titulo-secao">Locacoes no CEU</h5><p>${locacoes_ceu}</p><hr></div>`)
            }

        }
    })
}

function edita_ficha(){
    $('#form_ficha, #form_adicionais, #form_app, #salvar, #excluir').prop('disabled', false)
    $('.ver-conteudo-ficha').addClass('conteudo-ficha')
    $('.conteudo-ficha').removeClass('ver-conteudo-ficha')

    $('.perfil-participantes-ver-ficha, .observacoes-ver-ficha, #ceu :first-child, #atividades_ceu_ver_ficha, #locacoes_ceu_ver_ficha').removeClass('none')
    $('.ceu, #atividades_peraltas_ver_ficha, #atividades_eco_ver_ficha, .peraltas :first-child, .peraltas').removeClass('none')
    $('#lista_locacoes_ceu, #lista_atividades_ceu, #lista_atividades_peraltas, #lista_atividades_eco').addClass('none')
}