let hora_padrao_check_in, hora_padrao_check_out
let evento_corporativo

function carregar_scripts(editando) {
    if (editando === 'True') {
        $("#id_atividades_ceu, #id_locacoes_ceu, #id_atividades_eco, #id_atividades_peraltas").select2({
            disabled: 'readonly'
        })
        $('#id_opcionais_geral, #id_opcionais_formatura, #id_quais_atividades').select2({
            dropdownParent: $("#modal-adicionais .modal-content"),
            disabled: 'readonly'
        })
    } else {
        $("#id_atividades_ceu, #id_locacoes_ceu, #id_atividades_eco, #id_atividades_peraltas").select2()
        $('#id_opcionais_geral, #id_opcionais_formatura, #id_quais_atividades').select2({
            dropdownParent: $("#modal-adicionais .modal-content")
        })
    }
}

function encaminhamento() {
    localStorage.setItem("encaminhado", true)
}

function verQuantidades(produto) {
    const id_produto = produto.value
    if ($('#pre_resserva').val() === '') $('#id_check_in, #id_check_out').val('')
    $('#corpo-tabela-refeicao').empty()

    $.ajax({
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "POST",
        data: {'id_produto': id_produto},
        success: function (response) {
            hora_padrao_check_in = response['hora_check_in_padrao']
            hora_padrao_check_out = response['hora_check_out_padrao']

            if (response['so_ceu']) {
                $('.peraltas').addClass('none')
            } else {
                $('.peraltas').removeClass('none')
            }

            if (response['colegio']) {
                evento_corporativo = false
                $('.professores, #perfil_participantes, .lanches').removeClass('none')
                $('.corporativo, .coffees, #div_locacao_ceu').addClass('none')

                if (response['outro']) {
                    $('.outro-produto').removeClass('none')
                } else {
                    $('.outro-produto').addClass('none')
                }

                if (response['pernoite']) {
                    $('.alunos-pernoite, .professores-pernoite').removeClass('none')
                } else {
                    $('.alunos-pernoite, .professores-pernoite').addClass('none')
                }

                if (response['vt']) {
                    $('.alunos-pernoite, #perfil_participantes').addClass('none')
                }
            } else {
                evento_corporativo = true
                $('.corporativo, .coffees, #div_locacao_ceu').removeClass('none')
                $('#perfil_participantes, .professores, .alunos-pernoite, .lanches').addClass('none')
            }
        }
    })

}

function pegarDias(pre_reserva = false, editando=false) {
    let check_in = $('#id_check_in')
    let check_out = $('#id_check_out')

    if (pre_reserva) {
        check_in = $('#ModalCadastroPreReserva #id_check_in')
        check_out = $('#ModalCadastroPreReserva #id_check_out')
    }
    console.log(check_in.val(), check_out.val())

    if (check_out.val() !== '' && check_out.val() < check_in.val()) {
        check_out.val('')

        return
    }

    if (!editando) pegar_horario_padrao(check_in, check_out, pre_reserva)

    if (!pre_reserva && (check_in.val() !== '' && check_out.val() !== '')) {
        const data_1 = check_in.val().split('T')[0]
        const data_2 = check_out.val().split('T')[0]
        let intervalo = moment(data_2, "YYYY-MM-DD").diff(moment(data_1, "YYYY-MM-DD"))
        let dias = moment.duration(intervalo).asDays()
        $('#corpo-tabela-refeicao').empty()

        for (let i = 0; i <= dias; i++) {
            add_refeicao(moment(data_1).add(i, 'days').format('YYYY-MM-DD'))
        }
    }

    if (!pre_reserva && check_in.val() !== '') {
        $('#id_data_final_inscricao').val(moment(check_in.val()).subtract(15, 'days').format('YYYY-MM-DD'))
    }
}

function pegar_horario_padrao(check_in, check_out, pre_reserva) {
    $('#aviso_produto_n_selecionado').remove()
    let check_editar = $('#ModalCadastroPreReserva #check_editar_horarios').prop('checked')
    if (pre_reserva) check_editar = $('#editar_horarios').prop('checked')

    if (!check_editar) {
        if (hora_padrao_check_in === undefined) {
            if (pre_reserva){
                $('#ModalCadastroPreReserva .div-produtos').append('<div id="aviso_produto_n_selecionado" class="alert-warning mt-2"><p>Selecione o produto primeiro!</p></div>')
            } else {
                $('#sessao_periodo_viagem').append('<div id="aviso_produto_n_selecionado" class="alert-warning mt-2"><p>Selecione o produto primeiro!</p></div>')
            }
        } else if (hora_padrao_check_in === null) {
            return
        }

        check_in.val(`${check_in.val().split('T')[0]}T${hora_padrao_check_in}`)

        if (check_out.val() !== '') check_out.val(`${check_out.val().split('T')[0]}T${hora_padrao_check_out}`)
    }
}

function obs() {
    $('#observacoes_refeicoes').toggleClass('none')
}

function add_refeicao(data = null) {
    let i = document.querySelectorAll('.linha').length
    $('#corpo-tabela-refeicao').append(`<tr class="linha" id="linha_${i + 1}"></tr>`)
    let linha = document.querySelector(`#linha_${i + 1}`)

    $(linha).append(`<td><input type="date" class="data" name="data_refeicao_${i + 1}" style="width:  180px" value="${data}"></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input cafe" id="cafe_${i + 1}" name="cafe_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (evento_corporativo) $(linha).append(`<td><center><input type="checkbox" class="form-check-input coffee_m" id="coffee_m_${i + 1}" name="coffee_m_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input almoco" id="almoco_${i + 1}" name="almoco_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (!evento_corporativo) $(linha).append(`<td><center><input type="checkbox" class="form-check-input lanche_t" id="lanche_t_${i + 1}" name="lanche_t_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (evento_corporativo) $(linha).append(`<td><center><input type="checkbox" class="form-check-input coffee_t" id="coffee_t_${i + 1}" name="coffee_t_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input jantar" id="jantar_${i + 1}" name="jantar_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (!evento_corporativo) $(linha).append(`<td><center><input type="checkbox" class="form-check-input lanche_n" id="lanche_n_${i + 1}" name="lanche_n_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><button class="buton-x-ref" id="btn-ref_${i + 1}" type="button" onClick="remover_dia_refeicao(this)"><span><i class='bx bx-x'></i></span></button></center></td>`)
}

function remover_dia_refeicao(selecao) {
    $(`#linha_${selecao.id.split('_')[1]}`).remove()

    let n_linhas = document.querySelectorAll('.linha').length

    let linhas = document.querySelectorAll('.linha')
    let datas = document.querySelectorAll('.data')
    let cafes = document.querySelectorAll('.cafe')
    let coffes_m = document.querySelectorAll('.coffee_m')
    let almocos = document.querySelectorAll('.almoco')
    let lanches_t = document.querySelectorAll('.lanche_t')
    let coffees_t = document.querySelectorAll('.coffee_t')
    let jantares = document.querySelectorAll('.jantar')
    let lanches_n = document.querySelectorAll('.lanche_n')
    let butons = document.querySelectorAll('.buton-x-ref')

    for (let k = 0; k <= n_linhas; k++) {
        $(linhas[k]).attr('id', `linha_${k + 1}`)
        $(datas[k]).attr('id', `data_${k + 1}`).attr('name', `data_refeicao_${k + 1}`)
        $(cafes[k]).attr('id', `cafe_${k + 1}`).attr('name', `cafe_${k + 1}`)
        $(coffes_m[k]).attr('id', `coffee_m_${k + 1}`).attr('name', `coffee_m_${k + 1}`)
        $(almocos[k]).attr('id', `almoco_${k + 1}`).attr('name', `almoco_${k + 1}`)
        $(lanches_t[k]).attr('id', `lanche_t_${k + 1}`).attr('name', `lanche_t_${k + 1}`)
        $(coffees_t[k]).attr('id', `coffee_t_${k + 1}`).attr('name', `coffee_t_${k + 1}`)
        $(jantares[k]).attr('id', `jantar_${k + 1}`).attr('name', `jantar_${k + 1}`)
        $(lanches_n[k]).attr('id', `lanche_n_${k + 1}`).attr('name', `lanche_n_${k + 1}`)
        $(butons[k]).attr('id', `btn-ref_${k + 1}`).attr('name', `btn-ref_${k + 1}`)
    }
}

function pegarEndereco() {
    if ($('#id_transporte').prop('checked')) {
        $('#dados_transporte').removeClass('none')
        $('#id_transporte_fechado_internamente, #id_empresa_onibus, #id_horario_embarque, #id_endereco_embarque').prop('required', true)
    } else {
        $('#dados_transporte').addClass('none')
        $('#id_transporte_fechado_internamente, #id_empresa_onibus, #id_horario_embarque, #id_endereço_embarque').prop('required', false)
    }
}

function lista_segurados(editando = false) {
    if (!editando) {
        if ($('#id_seguro').prop('checked')) {
            $('#div_lista_segurads').removeClass('none')
        } else {
            $('#div_lista_segurads').addClass('none')
        }
    } else {
        if ($('#baixar_lista')) {
            $('#div_lista_segurads').addClass('none')
        }
    }
}

function quaisAtividades() {
    if ($('#id_biologo').prop('checked')) {
        $('#biologo').removeClass('none')
    } else {
        $('#biologo').addClass('none')
    }
}

function pegarIdInfosAdicionais(editando = false) {
    const id_informacoes_adicionais = $('#id_informacoes_adcionais').val()
    const lista_atividades_eco = $('#id_atividades_eco').val()
    const lista_atividades_biologo = $('#id_quais_atividades')

    for (let atividade of lista_atividades_biologo.children()) {
        if (!lista_atividades_eco.includes(atividade.value)){
            atividade.setAttribute('disabled', 'disabled')

            if (atividade.selected) {
                atividade.selected = false
                lista_atividades_biologo.trigger('change')
            }
        } else {
            atividade.removeAttribute('disabled')
        }
    }

    if (id_informacoes_adicionais !== '') {
        $('#infos').append(`<input type="hidden" name="id_infos_adicionais" value="${id_informacoes_adicionais}"/>`)
    }

    if (editando) {
        $('#id_opcionais_geral').prop('disabled', false)
        $('#id_opcionais_formatura').prop('disabled', false)
    }
}

function adcionar_novo_op_geral() {
    $('#adcionar_opcional_geral').removeClass('none')
    $('#nome_novo_op_geral').val('')
}

function salvar_novo_op_geral() {
    if ($('#nome_novo_op_geral').val() !== '') {
        $.ajax({
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: {'novo_op': 'geral', 'nome_op': $('#nome_novo_op_geral').val()},
            success: function (response) {
                if (response['salvo']) {
                    let data = {
                        id: response['id'],
                        text: $('#nome_novo_op_geral').val()
                    };

                    let newOption = new Option(data.text, data.id, true, true);
                    $('#id_opcionais_geral').append(newOption).trigger('change');

                    $('#adcionar_opcional_geral').addClass('none')
                }
            }
        })
    }
}

function adcionar_novo_op_formatura() {
    $('#adcionar_opcional_formatura').removeClass('none')
    $('#nome_novo_op_formatura').val('')
}

function salvar_novo_op_formatura() {
    if ($('#nome_novo_op_formatura').val() !== '') {
        $.ajax({
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: {'novo_op': 'formatura', 'nome_op': $('#nome_novo_op_formatura').val()},
            success: function (response) {
                if (response['salvo']) {
                    let data = {
                        id: response['id'],
                        text: $('#nome_novo_op_formatura').val()
                    };

                    let newOption = new Option(data.text, data.id, true, true);
                    $('#id_opcionais_formatura').append(newOption).trigger('change');

                    $('#adcionar_opcional_formatura').addClass('none')
                }
            }
        })
    }
}

jQuery('document').ready(function () {
    jQuery('#infos').submit(function () {
        const dados = new FormData(this);
        const lista = $('#id_lista_segurados').prop('files')[0]
        const url = $(this).attr('action');

        dados.append('lista_segurados', lista)
        dados.append('infos_adicionais', $('#id_informacoes_adcionais').val())

        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            contentType: false,
            processData: false,
            success: function (response) {
                $('#id_informacoes_adcionais').val(response['id'])
                $('#modal-adicionais').modal('hide')

                if ($('#id_informacoes_adcionais')) {
                    $('#info_adicionais_ok').prop('checked', true)
                }

                if (response['mensagem']) {
                    $('#corpo_site').prepend(response['mensagem'])
                }

            },
        });

        return false;
    });
});

function pegarIdCodigosApp() {

    if ($('#id_codigos_app').val() !== '') {
        $('#codigos_app').append(`<input type="hidden" name="id_codigo_app" value="${$('#id_codigos_app').val()}"/>`)
    }
}

$('document').ready(function () {
    jQuery('#codigos_app').submit(function () {
        let dados = jQuery(this).serialize();
        //aqui voce pega o conteudo do atributo action do form
        let url = $(this).attr('action');
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
                $('#id_codigos_app').val(response['id'])
                $('#modal_codigos_app').modal('hide')

                if ($('#id_codigos_app')) {
                    $('#codigos_app_ok').prop('checked', true)
                }
            }
        });

        return false;
    });
});

// Visualização Ficha de evento

/*function completar_visualizacao_ficha(id_ficha) {
    if ($('#id_observacoes').val() === '') {
        $('.observacoes-ver-ficha').addClass('none')
    }

    $('#info_adicionais_ok, #codigos_app_ok').prop('checked', true)

    $.ajax({
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "POST",
        data: {'id_ficha_de_evento': id_ficha},
        success: function (response) {
            $('#cliente').val(response['cliente'])
            $('#responsavel').val(response['responsavel'])

            $('#id_check_in').val(moment(response['check_in']).format('yyyy-MM-DDTHH:mm'))
            $('#id_check_out').val(moment(response['check_out']).format('yyyy-MM-DDTHH:mm'))
            pegarDias(true)

            if (!response['perfil']) {
                $('.perfil-participantes-ver-ficha').addClass('none')
            }

            for (let refeicao in response['refeicoes']) {
                $(`#${response['refeicoes'][refeicao]}`).prop('checked', true)
            }

            if (response['obs_refeicoes']) {
                $('#observacoes_refeicoes').removeClass('none')
            }

            if ($('.arquivo').children('a').prop('href')) {
                $('.arquivo, #material_apoio-clear_id, .arquivo label').addClass('none')
                $('#link_arquivo').append(`<a href="${$('.arquivo').children('a').prop('href')}">Material de apoio</a>`)
            } else {
                $('.arquivo, .material-apoio').addClass('none')
            }

        }
    })
}*/

function editar_ficha() {
    $('#form_ficha, #form_adicionais, #form_app, #salvar, #excluir, #id_atividades_ceu').prop('disabled', false)
    $('#id_locacoes_ceu, #id_quais_atividades, #id_atividades_eco, #id_atividades_peraltas').prop('disabled', false)
    $('.ver-conteudo-ficha').addClass('conteudo-ficha')
    $('.conteudo-ficha').removeClass('ver-conteudo-ficha')

    $('.perfil-participantes-ver-ficha, .observacoes-ver-ficha, #ceu :first-child, #atividades_ceu_ver_ficha, #locacoes_ceu_ver_ficha').removeClass('none')
    $('.ceu, .peraltas :first-child, .peraltas, #arquivo_atual_lista_editar, .material-apoio, .arquivo').removeClass('none')
    $('#lista_locacoes_ceu, #lista_atividades_ceu, #lista_atividades_peraltas, #lista_atividades_eco, #arquivo_atual_lista').addClass('none')

    lista_segurados()
}