
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
let escalados = []
function verificarDuplicata(selecao) {
    let professor_escolhido = selecao.value;
    let div_mensagem = $('#mensagem_erro')

    if (!escalados.includes(professor_escolhido)){
        escalados.push(professor_escolhido)
        div_mensagem.empty()
    } else {
        if(div_mensagem.is(':empty')){
            div_mensagem.prepend(`<p class="alert-warning">Professor já escalado para essa data!</p>`)
        }

        selecao.value = ''
    }
}

/* Da o início a animação na ficha de avaliação */
function animacao(){
    let home_section = document.getElementById('corpo_site')
    let formulario = document.getElementsByClassName('conteudo-avaliacao')
    let conteudo_inicio = document.getElementsByClassName('conteudo-inicio')

    home_section.classList.add('animado')
    formulario[0].classList.remove('hide')

    setTimeout(() => {
    conteudo_inicio[0].classList.add('hide')
    },2010);
}
