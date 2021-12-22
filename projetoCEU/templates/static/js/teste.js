var escala = [];

function equipe(selecao) {
    var valorSelecao = selecao.value;

    if (!escala.includes(valorSelecao)){
        escala.push(valorSelecao)
        $('.custom-select-d').append('<option>' + valorSelecao + '</option>');
    };
};

