
function verifica_colegio(selecao){
    let dados_colegio = document.querySelector(".colegios");
    let dados_colegio_barra = document.querySelector(".colegios_barra");
    console.log('Foi')
    if (selecao.value == 'Colégio'){
        dados_colegio.classList.remove('none')
        dados_colegio_barra.classList.remove('none')
    } else {
        dados_colegio.classList.add('none')
        dados_colegio_barra.classList.add('none')
    }
}
