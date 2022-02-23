
let escala = [$('#coordenador').val(),
              $('#professor_2').val(),
              $('#professor_3').val(),
              $('#professor_4').val()];

function equipe(selecao) {
    let valorSelecao = selecao.value;

    if (!escala.includes(valorSelecao)){
        escala.push(valorSelecao)
        $('.d').append(`<option>` + valorSelecao + `</option>`)
    }
}
// -------------------- Validação da tabela de atividades do público -----------------------------
function validar(){
    $('#ativ1').prop('required', true);
    $('#prf1atv1').prop('required', true);
    $('#horaAtividade_1').prop('required', true);
    $('#ativ2').prop('required', true);
    $('#prf1atv2').prop('required', true);
    $('#horaAtividade_2').prop('required', true);

    if ($("#ativ3").val() != '' || $("#prf1atv3").val() != '' || $("#horaAtividade_3").val() != ''){
        $('#prf1atv3').prop('required', true);
        $('#horaAtividade_3').prop('required', true);
        $('#ativ3').prop('required', true)
    }

    if ($("#ativ4").val() != '' || $("#prf1atv4").val() != '' || $("#horaAtividade_4").val() != ''){
        $('#prf1atv4').prop('required', true);
        $('#horaAtividade_4').prop('required', true);
        $('#ativ4').prop('required', true);
    }

    if ($("#ativ5").val() != '' || $("#prf1atv5").val() != '' || $("#horaAtividade_5").val() != ''){
        $('#prf1atv5').prop('required', true);
        $('#horaAtividade_5').prop('required', true);
        $('#ativ5').prop('required', true)
    }
}
// -----------------------------------------------------------------------------------------------

function locacao(){
    var professorLoc_1 = document.getElementById('prf1loc1')
    var  locacao_1 = document.getElementById('id_locacao_1')
    var entrada_1 = document.getElementById('horaEntrada1')
    var saida_1 = document.getElementById('horaSaida1')

    var tabelaLocacao = document.getElementById('locacao')
    tabelaLocacao.classList.toggle('none')

    if ($('#checkLocacao').is(":checked")){
        professorLoc_1.required = true
        locacao_1.required = true
        entrada_1.required = true
        saida_1.required = true
    } else {
        professorLoc_1.required = false
        locacao_1.required = false
        entrada_1.required = false
        saida_1.required = false
    }

}

var professorAtiv_1 = document.getElementById('prf1atv1')
var  id_atividade_1 = document.getElementById('id_atividade_1')
var hora_atividade_1 = document.getElementById('id_hora_atividade_1')
var professorlocacao_1 = document.getElementById('prf1loc1')
var  id_locacao_1 = document.getElementById('id_locacao_1')
var entrada_1 = document.getElementById('id_entrada_1_locacao_1')
var saida_1 = document.getElementById('id_saida_1_locacao_1')

function verificarObrigatoriedade(){

    if ($('#checkAtividade').is(":checked")){
        professorAtiv_1.required = true
        id_atividade_1.required = true
        hora_atividade_1.required = true
        professorlocacao_1.required = false
        id_locacao_1.required = false
        entrada_1.required = false
        saida_1.required = false
    } else {
        professorAtiv_1.required = false
        id_atividade_1.required = false
        hora_atividade_1.required = false
        professorlocacao_1.required = true
        id_locacao_1.required = true
        entrada_1.required = true
        saida_1.required = true
    }

}

function atividade(){

    var tabelaAtividade = document.getElementById('tabelaAtividade')
    tabelaAtividade.classList.toggle('none')
    verificarObrigatoriedade()

}

function verificarProfessor(selecao){
    let valorSelecao = selecao.value

    if (!escala.includes(valorSelecao)){
        $(selecao).val('0')
        alert('Professor não escalado!')
    }

}

var removidos = []
function retirar(selecao) {
    var valorSelecao = selecao.value;
    var opcoes = $('.d')[0]
    var remover = true

    for (let i = (1 + removidos.length); i < 5; i++){
        for (let j = 1; j < opcoes.length + removidos.length; j++){
            if (valorSelecao == $('.d')[i][j].value){

                if (remover){
                    removidos.push(valorSelecao)
                    remover = false
                }

                $('.d')[i][j].remove()
                break
            };
        }
    }

};

function solicitar(selecao) {
    $.ajax({
        type: 'POST',
        url: '',
        data: {'instituicao': selecao.value},
        success: function(response){
            $('#informacoes').empty()

            var equipeTemp = [];
            var equipe = [];
            var atividadesTemp = [];
            var atividades = [];
            var dados = response.split('][');

            // Parte pra isolar os professores que atenderam o colégio
            var temp = dados[0].split(', ')
            for (var j in temp){
                equipeTemp.push(temp[j].slice(14, -1).trim())
            };
            for (j in equipeTemp){
                if (!equipe.includes(equipeTemp[j]) && equipeTemp[j] != ''){
                    equipe.push(equipeTemp[j])
                }
            }

            // Parte pra isolar as atividades realizadas pelo colégio
            temp = dados[1].split(', ')
            for (var j in temp){
                atividadesTemp.push(temp[j].slice(13, -1).trim())
            };
            for (j in atividadesTemp){
                if (!atividades.includes(atividadesTemp[j]) && atividadesTemp[j] != ''){
                    atividades.push(atividadesTemp[j])
                }
            }

            //Aqui vem a parte pra adcionar os dados no card HTML
            $('#informacoes').append('<label class="mb-1">' + 'Os professores que atenderam o colégio acima foram: ' + '</label>')
            $('#informacoes').append('<div id="equipe" class="row"></div>')

            for (j in equipe){
                $('#equipe').append(`<div id=professor_${j} class="col-3 mb-2"></div>`)
                $(`#professor_${j}`).append(`<input id=professor_${j}_resp type="text" class="form-control" readonly>`)
                $(`#professor_${j}_resp`).val(equipe[j])
            }

            $('#informacoes').append('<br>')
            $('#informacoes').append('<label class="mb-1">' + 'E as atividades realizadas foram: ' + '</label>')
            $('#informacoes').append('<div id="atividades" class="row"></div>')
            for (j in atividades){
                $('#atividades').append(`<div id=atividade_${j} class="col-4"></div>`)
                $(`#atividade_${j}`).append(`<input id=atividade_${j}_resp type="text" class="form-control" readonly>`)
                $(`#atividade_${j}_resp`).val(atividades[j])
            }

            $('#informacoes').append('<br>')
            $('#informacoes').append('<center id="center"></center>')
            $('#center').append('<h4>' + 'AVISOS' + '</h4>')
            $('#informacoes').append('<ul id="avisos"></ul>')
            $('#avisos').append('<li align="justify">' + 'Verifique os dados contidos acima, em caso de informações incorretas, conferir se todas as Ordens de Serviço foram cadastradas corretamente, em caso de erro de preenchimento, favor comunicar o administrativo!' + '</li>')
            $('#avisos').append('<li align="justify">' + 'Com os dados verificado clique em solicitar, assim será gerado um login e senha para ser enviado ao responsável do colégio para que assim faça o preenchimento da Ficha de Avaliação.' + '</li>')
            $('#informacoes').append(`<button id="salvar" class="btn btn-primary ml-5">Salvar</button>`)

        }
    });
};

//$(window).on('load',function(){
//$('#aviso').modal('show')
//})

function animacao(){
    var home_section = document.getElementsByClassName('home-section')
    var formulario = document.getElementsByClassName('conteudo-avaliacao')
    var conteudo_inicio = document.getElementsByClassName('conteudo-inicio')

    home_section[0].classList.add('animado')
    formulario[0].classList.remove('hide')

    setTimeout(() => {
    conteudo_inicio[0].classList.add('hide')
    },2010);

}
