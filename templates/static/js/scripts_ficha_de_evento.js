let hora_padrao_check_in, hora_padrao_check_out, dias_produto, dados_produto_corporativo
let carregado = false
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
        $('#id_tipo_de_pagamento').select2({
            dropdownParent: $("#modal_codigos_app .modal-content"),
            disabled: 'readonly'
        })
    } else {
        $("#id_atividades_ceu, #id_locacoes_ceu, #id_atividades_eco, #id_atividades_peraltas").select2()
        $('#id_opcionais_geral, #id_opcionais_formatura, #id_quais_atividades').select2({
            dropdownParent: $("#modal-adicionais .modal-content")
        })
        $('#id_tipo_de_pagamento').select2({
            dropdownParent: $("#modal_codigos_app .modal-content")
        })
    }
}

function verificar_codigos_eficha() {
    $('.container_loading').removeClass('none')
    $('#modal_codigos_app .modal-body .alert').remove()

    const codigos_eficha = $('#id_eficha').val().split(',').map((codigo) => {
        return codigo.replaceAll(/^\s+|\s+$/g, '')
    })

    $.ajax({
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "GET",
        data: {'codigos_eficha': codigos_eficha},
        success: function (response) {
            if (response['salvar']) {
                if (response['totais']) {
                    $('#id_qtd_confirmada').val(response['totais']['total_confirmado'])
                    $('#id_qtd_eficha').val(response['totais']['total_eficha'])

                    if (response['totais']['total_eficha'] != 0) {

                        $('#div_eficha').removeClass('none')
                    }

                    if ($('#div_produto_corporativo').hasClass('none')) {
                        $('#id_qtd_meninos').val(response['totais']['total_pagantes_masculino'])
                        $('#id_qtd_meninas').val(response['totais']['total_pagantes_feminino'])
                        $('#id_qtd_profs_homens').val(response['totais']['total_professores_masculino'])
                        $('#id_qtd_profs_mulheres').val(response['totais']['total_professores_feminino'])
                    } else {
                        $('#id_qtd_homens').val(response['totais']['total_pagantes_masculino'])
                        $('#id_qtd_mulheres').val(response['totais']['total_pagantes_feminino'])
                    }
                }

                $('#btn_submit').trigger('click')
            } else {
                $('#modal_codigos_app .modal-body').prepend(`<div class="alert alert-danger">${response['mensagem']}</div>`)
            }
        }
    }).then(() => {
        $('.container_loading').addClass('none')
    })
}

function pegar_cnpj() {
    if ($('#id_cliente').val() !== '') {
        $.ajax({
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "GET",
            data: {'id_cliente': $('#id_cliente').val()},
            success: function (response) {
                $('#cnpj_cliente').val(response)
            }
        })
    }
}

function encaminhamento() {
    localStorage.setItem("encaminhado", true)
}

function atividades_a_definir() {
    if ($('#check_a_definir').prop('checked')) {
        $('#atividades_ceu_a_definir').removeClass('none')
    } else {
        $('#atividades_ceu_a_definir').addClass('none')
    }
}

function verQuantidades(produto, pre_reserva = false, editando = false) {
    const id_produto = produto.value
    if ($('#pre_resserva').val() === '') $('#id_check_in, #id_check_out').val('')

    $.ajax({
        url: '',
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        type: "POST",
        data: {'id_produto': id_produto},
        success: function (response) {
            hora_padrao_check_in = response['hora_check_in_padrao']
            hora_padrao_check_out = response['hora_check_out_padrao']

            if (carregado) $('#id_check_in, #id_check_out').val('')

            carregado = true
            dias_produto = response['n_dias']

            if (response['so_ceu']) {
                $('.peraltas').addClass('none')
            } else {
                $('.peraltas').removeClass('none')
            }

            if (response['colegio']) {
                evento_corporativo = false
                $('.professores, #perfil_participantes, .lanches').removeClass('none')
                $('.corporativo, .produtos-corporativos, .coffees, #div_locacao_ceu').addClass('none')
                $('#id_produto_corporativo').prop('required', false)

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
                dados_produto_corporativo = response['dados_produtos_corporativo']
                $('.corporativo, .coffees, #div_locacao_ceu, .produtos-corporativos').removeClass('none')
                $('#perfil_participantes, .professores, .alunos-pernoite, .lanches').addClass('none')
                $('#id_produto_corporativo').prop('required', true)
            }
        }
    }).done(() => {
        if (evento_corporativo && $('#id_produto_corporativo').val() !== '') {
            corporativo(document.getElementById('id_produto_corporativo'))
        } else {
            pegarDias(editando)
        }
    })

}

function pegarDias(editando = false) {
    let check_in = $('#sessao_periodo_viagem #id_check_in')
    let check_out = $('#sessao_periodo_viagem #id_check_out')
    let editar_refeicao = true
    const datas_tabela = $('#corpo-tabela-refeicao .data')

    if (datas_tabela.length > 0) {
        if (moment(datas_tabela[0].value).format('YYYY-MM-DD') !== moment(check_in.val()).format('YYYY-MM-DD') || moment(datas_tabela[datas_tabela.length - 1].value).format('YYYY-MM-DD') !== moment(check_out.val()).format('YYYY-MM-DD')) {
            let data = datas_tabela[0].value
            let intervalo = moment(data, "YYYY-MM-DD").diff(moment(check_in.val(), "YYYY-MM-DD"))
            let dias = moment.duration(intervalo).asDays()

            if ($('#corpo-tabela-refeicao .alert').length === 0) $('#corpo-tabela-refeicao').append('<tr class="alert alert-primary" style="text-align: center"><td colspan="7" style="padding: 0">Dias adicionados</td></tr>')

            for (let i = 1; i < dias + 1; i++) {
                add_refeicao(moment(check_in.val()).format('YYYY-MM-DD'))
                data = moment(check_in.val()).add(i, 'days')
            }

            data = datas_tabela[datas_tabela.length - 1].value
            intervalo = moment(check_out.val(), "YYYY-MM-DD").diff(moment(data, "YYYY-MM-DD"))
            dias = moment.duration(intervalo).asDays()

            for (let i = 1; i < dias + 1; i++) {
                add_refeicao(moment(data).add(i, 'days').format('YYYY-MM-DD'))
            }

        }

        editar_refeicao = false
    }

    if (check_out.val() !== '' && check_out.val() < check_in.val()) {
        check_out.val('')

        return
    }

    if (!editando) pegar_horario_padrao(check_in, check_out)

    if (check_in.val() !== '' && check_out.val() !== '') {
        const data_1 = check_in.val().split('T')[0]
        const data_2 = check_out.val().split('T')[0]
        let intervalo = moment(data_2, "YYYY-MM-DD").diff(moment(data_1, "YYYY-MM-DD"))
        let dias = moment.duration(intervalo).asDays()
    }

    if (editar_refeicao) tabela_refeicoes()

    if (!editando && check_in.val() !== '') {
        $('#id_data_final_inscricao').val(moment(check_in.val()).subtract(15, 'days').format('YYYY-MM-DD'))
    }
}

function liberar_ida_e_volta() {
    if ($('#id_lanche_bordo').prop('checked')) {
        $('.ida_e_volta').removeClass('none')
    } else {
        $('.ida_e_volta').addClass('none')
    }
}

async function tabela_refeicoes() {
    const data_1 = $('#sessao_periodo_viagem #id_check_in').val().split('T')[0]
    const data_2 = $('#sessao_periodo_viagem #id_check_out').val().split('T')[0]
    const intervalo = moment(data_2, "YYYY-MM-DD").diff(moment(data_1, "YYYY-MM-DD"))
    const dias = moment.duration(intervalo).asDays()
    $('#corpo-tabela-refeicao').empty()

    for (let i = 0; i <= dias; i++) {
        add_refeicao(moment(data_1).add(i, 'days').format('YYYY-MM-DD'))
    }
}

function corporativo(selecao) {
    const id_produto = selecao.value
    let check_in = $('#id_check_in')
    let check_out = $('#id_check_out')

    if (dados_produto_corporativo) {
        hora_padrao_check_in = dados_produto_corporativo[id_produto]['check_in_padrao']
        hora_padrao_check_out = dados_produto_corporativo[id_produto]['check_out_padrao']
    }

    pegar_horario_padrao(check_in, check_out)
}

function pegar_horario_padrao(check_in, check_out) {
    $('#aviso_produto_n_selecionado').remove()
    let check_editar = $('#check_editar_horarios').prop('checked')

    if (!check_editar) {
        if (hora_padrao_check_in === undefined) {
            $('#sessao_periodo_viagem').append('<div id="aviso_produto_n_selecionado" class="alert-warning mt-2"><p>Selecione o produto primeiro!</p></div>')
        } else if (hora_padrao_check_in === null) {
            return
        }

        check_in.val(`${check_in.val().split('T')[0]}T${hora_padrao_check_in}`)

        if (dias_produto !== null) {
            check_out.val(`${moment(check_in.val()).add(dias_produto, 'days').format('YYYY-MM-DD')}T${hora_padrao_check_out}`)
        } else {
            check_out.val(`${check_out.val().split('T')[0]}T${hora_padrao_check_out}`)
        }
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
    if (!evento_corporativo) $(linha).append(`<td class="lanches"><center><input type="checkbox" class="form-check-input lanche_m" id="lanche_m_${i + 1}" name="lanche_m_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (evento_corporativo) $(linha).append(`<td class="coffees"><center><input type="checkbox" class="form-check-input coffee_m" id="coffee_m_${i + 1}" name="coffee_m_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input almoco" id="almoco_${i + 1}" name="almoco_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (!evento_corporativo) $(linha).append(`<td class="lanches"><center><input type="checkbox" class="form-check-input lanche_t" id="lanche_t_${i + 1}" name="lanche_t_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (evento_corporativo) $(linha).append(`<td class="coffees"><center><input type="checkbox" class="form-check-input coffee_t" id="coffee_t_${i + 1}" name="coffee_t_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    $(linha).append(`<td><center><input type="checkbox" class="form-check-input jantar" id="jantar_${i + 1}" name="jantar_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
    if (!evento_corporativo) $(linha).append(`<td class="lanches"><center><input type="checkbox" class="form-check-input lanche_n" id="lanche_n_${i + 1}" name="lanche_n_${i + 1}" style="width: 5px; height: 5px"></center></td>`)
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
        $('#id_transporte_fechado_internamente, #id_empresa_onibus, #id_horario_embarque, #id_endereco_embarque').prop('required', false)
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
        if (!lista_atividades_eco.includes(atividade.value)) {
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

$('document').ready(function () {
    $("#id_tipo_de_pagamento").on("select2:select", function (e) {
        const opcao = e.params.data;
        $.ajax({
            url: '',
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "GET",
            data: {'tipo_pagamento': opcao['id']},
            success: function (response) {
                console.log(response)
                if (response['avulso']) {
                    $('#div_avulso').toggleClass('none')
                    $('#id_qtd_offline').val(0)
                }
            }
        })
    })

    $('#id_locacoes_ceu').on('select2:select', function (e) {
        $('.dados_locacoes_').removeClass('none')
        const infos_locacao = `
            <div class="row" id="espaco_${e.params.data.id}">
                <div style="width: 40%">
                    <label>Espaço</label>
                    <input type="text" name=espaco readonly required value="${e.params.data.text}">
                    <input type="hidden" id="id_espaco" name="id_espaco" value="${e.params.data.id}">
                </div>
                <div style="width: 20%">
                    <label>Intervalo</label>
                    <select name="intervalo" id="id_intervalo" required>
                        <option></option>
                        <option value="4">4 horas</option>
                        <option value="8">8 horas</option>
                    </select>
                </div>
                <div style="width: 30%">
                    <label>Formato da sala</label>
                    <select name="formato_sala" id="id_formato_sala" required></select>
                </div>
            </div>
        `
        $('#dados_locacoes').append(infos_locacao)

        if (e.params.data.text == 'Auditório') {
            $(`#espaco_${e.params.data.id} #id_formato_sala`).append('<option value="auditorio">Auditório</option>')
        } else if (e.params.data.text == 'Outro') {
            $(`#espaco_${e.params.data.id} #id_formato_sala`).append('<option value="livre">Formato livre</option>')
        } else {
            $(`#espaco_${e.params.data.id} #id_formato_sala`).append(`
                <option></option>
                <option value="auditorio">Auditório</option>
                <option value="u">Formato U</option>
                <option value="redondo">Formato redondo</option>
                <option value="escolar">Formato escolar</option>
                <option value="coquetel">Coquetel</option>
                <option value="livre">Formato livre</option>
            `)
        }
    })

    $('#id_locacoes_ceu').on('select2:unselect', function (e) {
        $(`#espaco_${e.params.data.id}`).remove()
    })
})

jQuery('document').ready(function () {
    jQuery('#infos').submit(function () {
        const dados = new FormData(this);
        const url = $(this).attr('action');
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
        if ($('#id_cliente_sem_app').val() == '') $('#id_cliente_sem_app').val($('#id_cliente').val())
        let dados = jQuery(this).serialize()
        //aqui voce pega o conteudo do atributo action do form
        let url = $(this).attr('action');
        $.ajax({
            url: url,
            headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
            type: "POST",
            data: dados,
            success: function (response) {
                console.log(response)
                $('#id_codigos_app').val(response['id'])
                $('#modal_codigos_app').modal('hide')

                if ($('#id_codigos_app')) {
                    $('#codigos_app_ok').prop('checked', true)
                }
            }
        }).catch((error) => console.error(error))

        return false;
    });
});

function editar_ficha() {
    $('#form_ficha, #form_adicionais, #salvar, #form_app, #excluir, #id_atividades_ceu').prop('disabled', false)
    $('#id_locacoes_ceu, #id_quais_atividades, #id_atividades_eco, #id_atividades_peraltas').prop('disabled', false)
    $('#id_tipo_de_pagamento, #id_opcionais_geral, #id_opcionais_formatura').prop('disabled', false)

    $('#id_cliente_pj').prop('readonly', true)

    $('.ver-conteudo-ficha').addClass('conteudo-ficha')
    $('.conteudo-ficha').removeClass('ver-conteudo-ficha')

    $('.perfil-participantes-ver-ficha, .observacoes-ver-ficha, #ceu :first-child, #atividades_ceu_ver_ficha, #locacoes_ceu_ver_ficha').removeClass('none')
    $('.ceu, .peraltas :first-child, .peraltas, #arquivo_atual_lista_editar, .material-apoio, .arquivo').removeClass('none')
    $('#lista_locacoes_ceu, #lista_atividades_ceu, #lista_atividades_peraltas, #lista_atividades_eco, #arquivo_atual_lista').addClass('none')

    lista_segurados()
}

$('#salvar').on('click', function (e) {
    $('#refeicoes_grupo .alert, .peraltas .alert').remove()
    const linhas_tabela_refeicao = $('.linha')
    const atividades_selecionadas = [
        $('#id_atividades_ceu').val(),
        $('#id_atividades_peraltas').val(),
        $('#id_locacoes_ceu').val(),
    ].flat()
    const atividades_ceu = $('#id_atividades_ceu').val()
    const atividades_a_definir = $('#id_atividades_ceu_a_definir').val()

    // Verificação das refeições
    for (let linha of linhas_tabela_refeicao) {
        let refeicoes = $(`#${linha.id} input[type=checkbox]`)
        let lista_refeicoes = []

        refeicoes.map((index, refeicao) => {
            lista_refeicoes.push(refeicao.checked)
        })

        if (!lista_refeicoes.includes(true)) {
            e.preventDefault()
            $('html, body').animate({scrollTop: 1000}, 50)
            $('#refeicoes_grupo').append('<div class="alert alert-warning">Todos os dias devem ter ao menos uma refeição cadastrada!</div>')

            return
        }
    }

    // Verificação das atividades
    if (!$('#check_a_definir').prop('checked') && !($('#id_atividades_ceu_a_definir').val() != '' && $('#id_atividades_ceu_a_definir').val() > '0')) {
        if (atividades_selecionadas.length === 0) {
            e.preventDefault()
            $('html, body').animate({scrollTop: 1200}, 50)
            $('.peraltas').append('<div class="alert alert-warning mt-2">É necessário ter pelo menos uma atividade selecionada ou setada como "A definir"!</div>')

            return
        }
    }

    if (atividades_ceu.length === 0 && !$('#check_a_definir').prop('checked')) {
        e.preventDefault()
        $('html, body').animate({scrollTop: 1200}, 50)
        $('.ceu').prepend('<div class="alert alert-warning mt-2">É necessário ter pelo menos uma atividade selecionada ou setada como "A definir"! Em caso de não haver atividade, selecionar "Sem atividade"</div>')
    }
})
