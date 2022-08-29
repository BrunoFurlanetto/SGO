
/* Validação do professor selecionado nos select dentro das tabelas de atividades */
function validacao(selecao){
    let professor = selecao.value

    let coordenador = $('#coordenador').val()
    let professor_2 = $('#professor_2').val()
    let professor_3 = $('#professor_3').val()
    let professor_4 = $('#professor_4').val()
    let professor_5 = $('#professor_5').val()

    if(professor !== coordenador && professor !== professor_2 && professor !== professor_3 && professor !== professor_4 && professor !== professor_5){
        $('#alert').remove()
        $($(`#${selecao.id}`).parent().parent().parent().parent().parent()).prepend(`<td colspan="5" class="alert-danger" id="alert"><center>Professor não escalado</center></td>`)
        $(`#${selecao.id}`).val('')
    } else {
        $('#alert').remove()
    }


}
/* Verifica se o professor selecionado para a atividades está escalado */
function verificarProfessor(selecao){
    let valorSelecao = selecao.value

    if (!escala.includes(valorSelecao)){
        $(selecao).val('0')
        alert('Professor não escalado!')
    }

}
/* Remove professor já escalado no modal do cadastro de escala */
var removidos = []
function retirar(selecao) {
    var valorSelecao = selecao.value;
    var opcoes = $('.d')[0]
    var remover = true

    for (let i = (1 + removidos.length); i < 5; i++){
        for (let j = 1; j < opcoes.length + removidos.length; j++){
            if (valorSelecao == $(".d")[i][j].value){

                if (remover){
                    removidos.push(valorSelecao)
                    remover = false
                }

                $('.d')[i][j].remove()
                break
            }
        }
    }

}
/* Da o início a animação na ficha de avaliação */
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
