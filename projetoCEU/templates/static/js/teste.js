var escala = [];

function equipe(selecao) {
    var valorSelecao = selecao.value;

    if (!escala.includes(valorSelecao)){
        escala.push(valorSelecao)
        $('.custom-select-d').append('<option>' + valorSelecao + '</option>');
    };
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

$(window).on('load',function(){
$('#aviso').modal('show')
})
