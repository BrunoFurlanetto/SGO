$(document).ready(() => {
    $('#fichas_evento').select2({
        width: '100%'
    })
})

function atualizar_participantes() {
    const n_adultos = parseInt($('#participantes #adultos').val())
    const n_criancas = parseInt($('#participantes #criancas').val())
    const n_monitoria = parseInt($('#participantes #monitoria').val())
    $('.total_monitores').val(n_monitoria)
    $('.total').val(n_adultos + n_criancas + n_monitoria)
}