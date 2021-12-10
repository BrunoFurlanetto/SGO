function equipe(selecao) {
    var valorSelecao = selecao.value;
    var professor = document.getElementById('pa1');
    let option = document.createElement('option');
    var adciona = true;
    var j = 2;

    if (j == professor.length){
        option.text = valorSelecao;
        professor.add(option)
    }else{
        for (i=2; i < professor.length; i++){
             if (valorSelecao == professor[i].value){
                adciona = false
            };
        };
        if (adciona){
            option.text = valorSelecao;
            professor.add(option);
        };
    };
};