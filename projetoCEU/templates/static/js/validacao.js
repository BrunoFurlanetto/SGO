// -------------------- Validação da tabela de atividades do público -----------------------------
function validarTabelaPublico(){
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