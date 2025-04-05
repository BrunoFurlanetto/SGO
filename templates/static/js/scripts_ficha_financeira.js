let n_comissionados = $('.planos_pagamento .comissionado').length

$(document).ready(() => {
    $('.porcentagem').mask('00,00%', {reverse: true})
    $('#id_cnpj').mask("99.999.999/9999-99")
    $('#id_valor_a_vista').DinheiroMascara()
    $('#id_cargo').select2({dropdownParent: $("#cadastro_responsavel_operacional .modal-content")})
    mascara_telefone($('#id_fone'))
    mascara_telefone($('#id_whats'))

    $('#form_ficha_financeira').submit(function () {
        let comissaoValue = $('#id_comissao').val()
        let valor_a_vista = $('#id_valor_a_vista').val()

        if (comissaoValue != undefined) {
            if (comissaoValue != '') {
                comissaoValue = comissaoValue.replace('%', '')
                $('#id_comissao').val(parseFloat(comissaoValue))
            } else {
                $('#id_comissao').val(parseFloat('0.00'))
            }
        }

        valor_a_vista = valor_a_vista.replace('.', '').replace(',', '.')
        $('#id_valor_a_vista').val(parseFloat(valor_a_vista))
    });


    setInterval(() => {
        try {
            $('#modal_negado .modal-footer button').prop('disabled', $('#modal_negado #motivo_recusa').val().length < 10)
        } catch (e) {
        }
    }, 10)
})

function fechar_campos() {
    console.log('Foi')
    $('#form_ficha_financeira fieldset input, #form_ficha_financeira fieldset select, #form_ficha_financeira fieldset textarea').each((index, campo) => {
        if (campo.nodeName == 'INPUT' || campo.nodeName == 'TEXTAREA') {
            $(campo).prop('readonly', true)
        } else {
            $(campo).addClass('inalteravel')
        }
    })
}

function setar_comissao() {
    $("#modal_aprovado #comissao_colaborador").val(parseFloat($('#id_comissao').val().replace('%', '')))
}

function mascara_porcentagem(input) {
    $(input).mask('00,00%', {reverse: true})
}

function mascara_telefone(input) {
    $(input).mask('(00) 0 0000-00009');
    $(input).blur(function (event) {
        if ($(input).val().length == 16) { // Celular com 9 dígitos + 2 dígitos DDD e 4 da máscara
            $(input).mask('(00) 0 0000-0009');
        } else {
            $(input).mask('(00) 0000-0000');
        }
    });
}

$.fn.DinheiroMascara = function () {
    return $(this).maskMoney({
        prefix: 'R$ ',
        thousands: '.',
        decimal: ',',
        allowZero: true,
        affixesStay: false,
        allowNegative: true,
    })
}

function verificar_vencimentos(input) {
    const id_input = $(input).attr('id')
    const inicio_vencimento = moment($('#id_inicio_vencimento').val())
    const final_vencimento = moment($('#id_final_vencimento').val())
    const parcelas = parseInt($('#id_parcelas').val())
    $('.planos_pagamento .alert').addClass('none')

    if (id_input != 'id_final_vencimento') {
        $('#id_final_vencimento').val(inicio_vencimento.add(parcelas - 1, 'month').format('YYYY-MM-DD'))
    } else {
        if (final_vencimento.month() - inicio_vencimento.month() != parcelas - 1) {
            $('.planos_pagamento .alert').removeClass('none')
        }
    }
}

function verificar_metodo_pagamento() {
    const metodo_pagamento = $('#id_forma_pagamento option:selected').text()

    if (metodo_pagamento.includes('vista')) {
        $('#id_parcelas').val(1).attr('readonly', true)
        $('#id_final_vencimento').val(moment($('#id_inicio_vencimento').val()).format('YYYY-MM-DD')).attr('readonly', true)
    } else {
        if (metodo_pagamento.includes('ficha')) {
            $('#div_id_codigo_eficha').removeClass('none')
        } else {
            $('#div_id_codigo_eficha').addClass('none')
        }
        $('#id_parcelas, #id_final_vencimento').attr('readonly', false)

    }
}

function tornar_campos_obrigatorios() {
    if ($('#id_nf').prop('checked')) {
        $('.nota_fiscal input').prop('required', true)
    } else {
        $('.nota_fiscal input').prop('required', false)
    }
}

function iniciarArraste() {
    let divArrastavel = document.getElementById('mostrar_motivo_recusa');
    let offsetX = event.clientX - divArrastavel.getBoundingClientRect().left;
    let offsetY = event.clientY - divArrastavel.getBoundingClientRect().top;

    function moverDiv(event) {
        let x = event.clientX - offsetX;
        let y = event.clientY - offsetY;

        divArrastavel.style.left = x + 'px';
        divArrastavel.style.top = y + 'px';

        let isDireitaDoMeio = x > window.innerWidth / 2;
        atualizarBorderRadius(isDireitaDoMeio);
    }

    function pararArraste() {
        document.removeEventListener('mousemove', moverDiv);
        document.removeEventListener('mouseup', pararArraste);
        divArrastavel.style.cursor = 'grab';
    }

    document.addEventListener('mousemove', moverDiv);
    document.addEventListener('mouseup', pararArraste);
    divArrastavel.style.cursor = 'grabbing';
}

function atualizarBorderRadius(isDireitaDoMeio) {
    let divArrastavel = document.getElementById('mostrar_motivo_recusa');
    let icone = document.getElementById('icone_arrastavel')

    if (isDireitaDoMeio) {
        icone.style.transform = 'scaleX(1)'
        divArrastavel.style.borderRadius = '40% 40% 40% 10%';
    } else {
        icone.style.transform = 'scaleX(-1)'
        divArrastavel.style.borderRadius = '40% 40% 10% 40%';
    }
}

function adcionar_comissionado() {
    n_comissionados += 1

    $('.planos_pagamento').append(`
        <div class="comissionado">
            <hr style="width: 100%">
            <div class="div_btn_excluir_comissionado">           
                <button type="button" class="btn-close" onclick="excluir_comissionado(this)"></button>
            </div>
            <div style="width: 70%; margin-top: -30px">
                <label for="nome_comissionado_1">Nome</label>
                <input type="text" name="comissionado_${n_comissionados}" id="nome_comissionado_${n_comissionados}">
            </div>
            <div style="width: 27%; margin-top: -30px;">
                <label for="telefone_comissionado_${n_comissionados}">Telefone</label>
                <input type="text" name="comissionado_${n_comissionados}" id="telefone_comissionado_${n_comissionados}" onfocus="mascara_telefone(this)">
            </div>
            <div style="width: 50%">
                <label for="email_comissionado_${n_comissionados}">E-mail</label>
                <input type="text" name="comissionado_${n_comissionados}" id="email_comissionado_${n_comissionados}">
            </div>
            <div style="width: 20%">
                <label for="valor_comissionado_${n_comissionados}">Valor comissão</label>
                <input type="text" name="comissionado_${n_comissionados}" class="porcentagem" onfocus="mascara_porcentagem(this)" id="valor_comissionado_${n_comissionados}">
            </div>
        </div>
    `)
}

function remover_responsaveis(ids_responsaveis) {
    const responsaveis = $('#id_enviado_ac option, #id_responsavel_operacional option, #id_responsavel_financeiro option')

    for (let opt of responsaveis) {
        if (!ids_responsaveis.includes(parseInt(opt.value)) && opt.value != '') {
            opt.remove()
        }
    }
}

function buscar_dados_financeiro() {
    const id_responsavel = $('#id_responsavel_financeiro').val()

    if (id_responsavel == '') {
        $('#id_telefone_financeiro, #id_whats_financeiro, #id_email_financeiro').val('')
    } else {
        $.ajax({
            type: 'GET',
            url: '/ficha_financeira/buscar_dados_responsavel/',
            data: {'id_responsavel': id_responsavel},
            success: function (response) {
                $('#id_telefone_financeiro').val(response['telefone'])
                $('#id_whats_financeiro').val(response['whats'])
                $('#id_email_financeiro').val(response['email'])
            }
        })
    }
}

function salvar_novo_responsavel() {
    let form = $('#form_novo_responsavel');

    // Limpar mensagens anteriores
    $('#alert-erro, #alert-aviso, #alert-sucesso').addClass('none').empty();

    // Verificar se os campos required estão preenchidos
    let valido = true;
    form.find('[required]').each(function () {
        if (!$(this).val()) {
            valido = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });

    if (!valido) {
        $('#alert-aviso')
            .removeClass('none')
            .text('Por favor, preencha todos os campos obrigatórios.');
        return;
    }

    // Enviar via AJAX
    $.ajax({
        url: form.attr('action'),
        method: form.attr('method'),
        data: form.serialize(),
        success: function (response) {
            $('#form_novo_responsavel')[0].reset();

            const id = response['id']
            const nome = response['nome']
            const telefone = response['telefone']
            const whats = response['whats']
            const email = response['email']
            const nomeTelefone = `${nome} - ${telefone}`

            // Adicionar aos selects
            $('#id_enviado_ac').append(new Option(nomeTelefone, id));
            $('#id_responsavel_operacional').append(new Option(nomeTelefone, id));
            $('#id_responsavel_financeiro').append(new Option(nome, id));
            $('#id_telefone_financeiro').val(telefone)
            $('#id_whats_financeiro').val(whats)
            $('#id_email_financeiro').val(email)
            $('#cadastro_responsavel_operacional').modal('hide')
        },
        error: function (xhr, status, erro) {
            if (xhr.status === 400) {
                // Erros de validação
                let erros = xhr.responseJSON.erros;
                let mensagens = '<ul>';
                for (let campo in erros) {
                    mensagens += `<li><strong>${campo}:</strong> ${erros[campo].join(', ')}</li>`;
                }
                mensagens += '</ul>';
                $('#alert-erro')
                    .removeClass('none')
                    .html(mensagens);
            } else if (xhr.status === 500) {
                $('#alert-erro')
                    .removeClass('none')
                    .text(xhr.responseJSON.erros);
            } else {
                $('#alert-erro')
                    .removeClass('none')
                    .text('Erro inesperado: ' + erro);
            }
        }
    });
}


function excluir_comissionado(btn) {
    $(btn).parent().parent().remove()
}

function imprimir_ficha() {
    var style = document.getElementById('style').cloneNode(true)
    var ficha = document.getElementById('conteudo_ficha_financeira').cloneNode(true)
    var tabela_descritivo = document.getElementById('modal_descritivo_dia').cloneNode(true)
    var printWindow = window.open('', '_blank');

    ficha.style.pointerEvents = 'none'

    // Adiciona o conteúdo do formulário clonado acima da tabela
    printWindow.document.body.appendChild(style);
    printWindow.document.body.appendChild(ficha);
    printWindow.document.body.appendChild(tabela_descritivo)

    var checkReady = setInterval(function () {
        if (printWindow.document.readyState === "complete") {
            clearInterval(checkReady);
            printWindow.print();
            printWindow.document.close();
            printWindow.close();
        }
    }, 50);
}