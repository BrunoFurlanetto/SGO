$(document).ready(function () {
    // Atualiza quando a página carrega
    atualizarObservacoes();
    toggleOutrosMotivos();
    atualizarObservacaoVoltaProximoAno();
    $('#id_volta_proximo_ano').on('change', atualizarObservacaoVoltaProximoAno);
    $('#id_motivo_trazer_grupo').on('change', toggleOutrosMotivos)
    $('select.campo-avaliacao').change(atualizarObservacoes);
    $('select[multiple]').each(function () {
        $(this).select2({
            width: '100%',
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Configurações para ambos os tipos (destaque e desempenho)
    const config = {
        'destaque': {
            addButtonId: 'add-destaque',
            containerId: 'destaque-container',
            formPrefix: 'destaques',
            selectPrefix: 'destaque',
            itemClass: 'destaque-item'
        },
        'desempenho': {
            addButtonId: 'add-desempenho',
            containerId: 'desempenho-container',
            formPrefix: 'desempenho', // Ajuste conforme o nome no seu forms.py
            selectPrefix: 'desempenho',
            itemClass: 'desempenho-item'
        }
    };

    // Função genérica para adicionar itens
    function addItem(type) {
        const cfg = config[type];
        const totalFormsInput = document.getElementById(`id_${cfg.formPrefix}-TOTAL_FORMS`);
        const container = document.getElementById(cfg.containerId);
        const existingForms = container.getElementsByClassName(cfg.itemClass);
        const monitorOptions = document.querySelectorAll(`#id_${cfg.formPrefix}-0-monitor option`).length - 1;
        console.log(monitorOptions)
        // Verificação 1: Não exceder número de monitores
        if (existingForms.length >= monitorOptions) {
            alert(`Você só pode adicionar no máximo ${monitorOptions} ${type}s`);
            return;
        }

        // Verificação 2: Garantir que há template para clonar
        if (existingForms.length === 0) {
            console.error(`Nenhum form de ${type} encontrado para clonar!`);
            return;
        }

        // Clona o último form
        const newForm = existingForms[existingForms.length - 1].cloneNode(true);
        const newIndex = parseInt(totalFormsInput.value);

        // Insere o botão de remoção
        const removeBtnHtml = `
            <button type="button" class="bg-transparent border-0 fs-3 remove-item" data-type="${type}">
                <i class='bx bx-user-x bx-flip-horizontal'></i>
            </button>`;

        const lastTd = newForm.querySelector('td:last-child');
        if (lastTd) lastTd.innerHTML = removeBtnHtml;

        // Atualiza todos os IDs/names
        newForm.innerHTML = newForm.innerHTML
            .replace(new RegExp(`${cfg.formPrefix}-(\\d+)-`, 'g'), `${cfg.formPrefix}-${newIndex}-`)
            .replace(/(\d+)º<\/span>/, `${newIndex + 1}º</span>`);

        // Atualização manual para garantir
        newForm.querySelectorAll(`[id^="id_${cfg.formPrefix}-"], [name^="${cfg.formPrefix}-"]`).forEach(el => {
            el.id = el.id.replace(new RegExp(`${cfg.formPrefix}-(\\d+)-`), `${cfg.formPrefix}-${newIndex}-`);
            el.name = el.name.replace(new RegExp(`${cfg.formPrefix}-(\\d+)-`), `${cfg.formPrefix}-${newIndex}-`);
        });

        // Atualiza o número da posição
        const posicaoSpan = newForm.querySelector('td:nth-child(2) span');
        if (posicaoSpan) posicaoSpan.textContent = `${newIndex + 1}º`;

        // Limpa valores
        newForm.querySelectorAll('input:not([type="hidden"]), select').forEach(el => {
            if (el.tagName === 'SELECT') el.selectedIndex = 0;
            else el.value = '';
        });

        newForm.style.opacity = '0';
        container.appendChild(newForm);
        fadeIn(newForm);
        totalFormsInput.value = newIndex + 1;
    }

    // Função para remover itens
    function removeItem(item, type) {
        const cfg = config[type];
        const container = document.getElementById(cfg.containerId);
        const items = container.getElementsByClassName(cfg.itemClass);

        // Verifica se é o último item
        if (item !== items[items.length - 1]) {
            alert(`Você só pode remover o último ${type} adicionado!`);
            return;
        }

        fadeOut(item).then(() => item.remove()).then(() => validateAllMonitors(cfg.selectPrefix));

        // Atualiza o contador total de forms
        const totalFormsInput = document.getElementById(`id_${cfg.formPrefix}-TOTAL_FORMS`);
        totalFormsInput.value = parseInt(totalFormsInput.value) - 1;

        updatePositionNumbers(cfg);
    }

    // Atualiza números de posição
    function updatePositionNumbers(cfg) {
        const container = document.getElementById(cfg.containerId);
        const items = container.getElementsByClassName(cfg.itemClass);

        Array.from(items).forEach((item, index) => {
            const posicaoSpan = item.querySelector('td:nth-child(2) span');
            if (posicaoSpan) posicaoSpan.textContent = `${index + 1}º`;

            // Atualiza também o campo hidden da posição se existir
            const posicaoInput = item.querySelector('input[name$="-posicao"]');
            if (posicaoInput) posicaoInput.value = index + 1;
        });
    }

    // Event listeners para adicionar itens
    document.getElementById(config.destaque.addButtonId).addEventListener('click', () => addItem('destaque'));
    document.getElementById(config.desempenho.addButtonId).addEventListener('click', () => addItem('desempenho'));

    // Event listener para remover itens (delegação de eventos)
    document.addEventListener('click', function (e) {
        if (e.target.closest('.remove-item')) {
            const type = e.target.closest('.remove-item').dataset.type;
            const item = e.target.closest(`.${config[type].itemClass}`);
            removeItem(item, type);
        }
    });

    // Validação em tempo real de avaliações (mantido como estava)
    document.querySelectorAll('[id$="-avaliacao"]').forEach(select => {
        select.addEventListener('change', function () {
            const obsField = this.closest('.avaliacao-item').querySelector('[id$="-observacao"]');
            if (['1', '2'].includes(this.value)) {
                obsField.required = true;
                obsField.closest('.form-group')?.classList.add('required-field');
            } else {
                obsField.required = false;
                obsField.closest('.form-group')?.classList.remove('required-field');
            }
        });
    });
});

// Função para atualizar os números de posição
function updatePositionNumbers() {
    const container = document.getElementById('destaque-container');
    const items = container.getElementsByClassName('destaque-item');

    Array.from(items).forEach((item, index) => {
        const posicaoSpan = item.querySelector('td:nth-child(2) span');
        const posicaoHidden = item.querySelector('input[type="hidden"][name*="posicao"]');

        if (posicaoSpan) posicaoSpan.textContent = `${index + 1}º`;
        if (posicaoHidden) posicaoHidden.value = index + 1;
    });
}

function isMonitorAlreadySelected(selectElement, secao) {
    const selectedMonitorId = selectElement.value;
    if (!selectedMonitorId) return false; // Ignora se nenhum monitor foi selecionado

    const container = document.getElementById(`${secao}-container`);
    const allSelects = container.querySelectorAll('select[name$="-monitor"]');

    let count = 0;
    allSelects.forEach(select => {
        console.log(select.value, selectedMonitorId)
        if (select.value === selectedMonitorId) count++;
    });

    return count > 1;
}

function validateAllMonitors(secao) {
    let container = document.getElementById(`${secao}-container`);
    let allSelects = container.querySelectorAll('select[name$="-monitor"]');

    allSelects.forEach(select => {
        select.style.border = '';
        if (isMonitorAlreadySelected(select, secao)) {
            select.style.border = '2px solid red';
        }
    });
}

// Funções auxiliares
function fadeIn(element) {
    let opacity = 0;
    const timer = setInterval(() => {
        if (opacity >= 1) clearInterval(timer);
        element.style.opacity = opacity;
        opacity += 0.1;
    }, 30);
}

function fadeOut(element) {
    return new Promise(resolve => {
        let opacity = 1;
        const timer = setInterval(() => {
            if (opacity <= 0) {
                clearInterval(timer);
                resolve();
            }
            element.style.opacity = opacity;
            opacity -= 0.1;
        }, 30);
    });
}

document.querySelectorAll('.palavra-chave-input').forEach(input => {
    // Auto-foco no próximo campo quando atingir o maxlength
    input.addEventListener('input', function () {
        if (this.value.length === parseInt(this.maxLength)) {
            const nextIndex = parseInt(this.dataset.index) + 1;
            const nextInput = document.querySelector(`.palavra-chave-input[data-index="${nextIndex}"]`);
            if (nextInput) nextInput.focus();
        }
    });

    // Validação em tempo real
    input.addEventListener('blur', function () {
        this.value = this.value.trim();
    });
});

$('form').submit(function (e) {
    let formValido = true;

    $('tr[data-has-obs]').each(function () {
        const tr = $(this);
        const select = tr.find('select.campo-avaliacao');
        const obsField = tr.find('.campo-obs textarea');
        const resposta = select.val();

        if (['False', '2', '1'].includes(resposta) && !obsField.val().trim()) {
            tr.find('.obs-cell').addClass('obs-obrigatoria');
            obsField.addClass('is-invalid');
            formValido = false;
        }
    });

    if (!formValido) {
        e.preventDefault();
        $('.is-invalid').first().focus();
        alert('Por favor, preencha todas as observações obrigatórias!');
    }
});

function atualizarObservacoes() {
    $('tr[data-has-obs]').each(function () {
        const tr = $(this);
        const select = tr.find('select.campo-avaliacao');
        const obsField = tr.find('.campo-obs');
        const resposta = select.val();
        // Respostas que exigem observação: False, '2', '1'
        const exigeObs = ['False', '2', '1'].includes(resposta);

        // Atualiza a obrigatoriedade
        obsField.prop('required', exigeObs);

        // Atualiza o estilo
        if (exigeObs) {
            tr.find('.obs-cell').addClass('obs-obrigatoria');
            obsField.addClass('is-invalid');
        } else {
            tr.find('.obs-cell').removeClass('obs-obrigatoria');
            obsField.removeClass('is-invalid');
        }
    });
}

function atualizarObservacaoVoltaProximoAno() {
    const respostasQueExigemObs = ['nao', 'talvez'];

    const select = $('#id_volta_proximo_ano');
    const resposta = select.val()?.toLowerCase();

    const obsField = $('#id_volta_proximo_ano_obs');
    const obsCell = obsField.closest('.obs-cell');
    const exigeObs = respostasQueExigemObs.includes(resposta);

    // Atualiza obrigatoriedade
    obsField.prop('required', exigeObs);

    // Atualiza estilo visual
    if (exigeObs) {
        obsCell.addClass('obs-obrigatoria');
        obsField.addClass('is-invalid');
    } else {
        obsCell.removeClass('obs-obrigatoria');
        obsField.removeClass('is-invalid');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Lista de avaliações que exigem observação obrigatória
    const avaliacaoQueExigeObservacao = ['Ruim', 'Regular'];

    document.querySelectorAll('.avaliacao-select').forEach(function (avaliacaoSelect, index) {
        avaliacaoSelect.addEventListener('change', function () {
            const observacaoInput = document.querySelectorAll('.observacao-input')[index];
            if (avaliacaoQueExigeObservacao.includes(this.value)) {
                observacaoInput.setAttribute('required', 'required');
                observacaoInput.classList.add('is-invalid'); // opcional: para destacar visualmente
            } else {
                observacaoInput.removeAttribute('required');
                observacaoInput.classList.remove('is-invalid');
            }
        });
    });
});


function toggleOutrosMotivos() {
    const select = $('#id_motivo_trazer_grupo');
    const selectedOptions = select.find('option:selected');
    let hasOutro = false;

    selectedOptions.each(function () {
        const text = $(this).text().toLowerCase();
        if (text.includes('outro')) {
            hasOutro = true;
            return false; // quebra o loop
        }
    });

    const tr = select.closest('tr');
    const tdPergunta = tr.find('td.pergunta-cell').first();
    const tdObs = tr.find('td.pergunta-cell').eq(1);
    $('#id_outros_motivos').prop('required', hasOutro)

    if (hasOutro) {
        tdPergunta.attr('colspan', '1');
        tdObs.removeClass('none');
    } else {
        tdPergunta.attr('colspan', '2');
        tdObs.addClass('none');
    }
}

$('#id_telefone_avaliador').mask('(00) 0 0000-00009');

$('#id_telefone_avaliador').blur(function(event) {
    if ($(this).val().length === 16) {
        // Celular com 9 dígitos
        $(this).mask('(00) 0 0000-0009');
    } else {
        // Telefone fixo
        $(this).mask('(00) 0000-0000');
    }
});
