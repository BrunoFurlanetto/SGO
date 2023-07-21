function alterar_aba(aba, sectionId) {
    const conteudos_abas = [
        'orcamentos_aprovacao',
        'log'
    ]
    $('.folder:not([ativo])').removeClass('ativo')
    $(aba).addClass('ativo')

    for (let conteudo of conteudos_abas) {
        if (conteudo === sectionId) {
            $(`#${conteudo}`).addClass('ativo')
        } else {
            $(`#${conteudo}`).removeClass('ativo')
        }
    }
}
