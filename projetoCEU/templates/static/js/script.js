function equipe(selecao) {
    var valorSelecao = selecao.value;
    var professor1 = document.getElementById('pa1');
    var professor2 = document.getElementById('pa2');
    var professor3 = document.getElementById('pa3');
    var professor4 = document.getElementById('pa4');
    let option = document.createElement('option');
    var adciona = true;
    var j = 2;

    if (j == professor1.length){
        for (i = 1; i < 5; i++){
            option.text = valorSelecao;
            professor1.add(option)
        }
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