$(document).ready(function () {
    // Atualiza quando a página carrega
    atualizarObservacoes();
    $('select.campo-avaliacao').change(atualizarObservacoes);
});

document.addEventListener('DOMContentLoaded', function () {
    // Adiciona novos destaques
    document.getElementById('add-destaque').addEventListener('click', function () {
        const totalFormsInput = document.getElementById('id_destaques-TOTAL_FORMS')
        const container = document.getElementById('destaque-container')
        const existingForms = container.getElementsByClassName('destaque-item')
        const monitorOptions = document.querySelectorAll('#id_destaques-0-monitor option').length - 1 // Descontar opção vazia


        // Verificação 1: Não exceder número de monitores
        if (existingForms.length >= monitorOptions) {
            alert(`Você só pode adicionar no máximo ${monitorOptions} destaques`)
            return
        }

        // Verificação 2: Garantir que há template para clonar
        if (existingForms.length === 0) {
            console.error('Nenhum form encontrado para clonar!');
            return
        }

        // Clona o último form
        const newForm = existingForms[existingForms.length - 1].cloneNode(true)
        const newIndex = parseInt(totalFormsInput.value)

        // Garante que o novo item terá o botão de remoção
        const removeBtnHtml = `
                <button type="button" class="bg-transparent border-0 fs-3 remove-item">
                    <i class='bx bx-user-x bx-flip-horizontal'></i>
                </button>`

        // Insere o botão na última célula
        const lastTd = newForm.querySelector('td:last-child');
        if (lastTd) lastTd.innerHTML = removeBtnHtml

        // Atualiza todos os IDs/names/números de posição
        newForm.innerHTML = newForm.innerHTML
            .replace(/destaques-(\d+)-/g, `destaques-${newIndex}-`)
            .replace(/(\d+)º<\/span>/, `${newIndex + 1}º</span>`) // +1 porque começa em 0

        // Atualização manual para garantir
        newForm.querySelectorAll('[id^="id_destaques-"], [name^="destaques-"]').forEach(el => {
            el.id = el.id.replace(/destaques-(\d+)-/, `destaques-${newIndex}-`)
            el.name = el.name.replace(/destaques-(\d+)-/, `destaques-${newIndex}-`)
        })

        // Atualiza o número da posição no span
        const posicaoSpan = newForm.querySelector('td:nth-child(2) span')
        if (posicaoSpan) posicaoSpan.textContent = `${newIndex + 1}º`

        // Limpa valores (exceto hidden)
        newForm.querySelectorAll('input:not([type="hidden"]), select').forEach(el => {
            if (el.tagName === 'SELECT') el.selectedIndex = 0
            else el.value = ''
        });

        newForm.style.opacity = '0';
        container.appendChild(newForm);
        fadeIn(newForm);

        container.appendChild(newForm)
        totalFormsInput.value = newIndex + 1
    });

    // Remove destaque - Nova versão
    document.addEventListener('click', function (e) {
        if (e.target.closest('.remove-item')) {
            const container = document.getElementById('destaque-container')
            const items = container.getElementsByClassName('destaque-item')
            const clickedItem = e.target.closest('.destaque-item')

            // Verifica se é o último item
            if (clickedItem !== items[items.length - 1]) {
                alert('Você só pode remover o último destaque adicionado!')
                return
            }

            // No código de remover:
            fadeOut(clickedItem).then(() => clickedItem.remove()).then(() => validateAllMonitors());

            // Atualiza o contador total de forms
            const totalFormsInput = document.getElementById('id_destaques-TOTAL_FORMS')
            totalFormsInput.value = parseInt(totalFormsInput.value) - 1

            // Atualiza os números de posição
            updatePositionNumbers()
        }
    });

    // Validação em tempo real de avaliações
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

function isMonitorAlreadySelected(selectElement) {
    const selectedMonitorId = selectElement.value;
    if (!selectedMonitorId) return false; // Ignora se nenhum monitor foi selecionado

    const container = document.getElementById('destaque-container');
    const allSelects = container.querySelectorAll('select[name$="-monitor"]');

    let count = 0;
    allSelects.forEach(select => {
        console.log(select.value, selectedMonitorId)
        if (select.value === selectedMonitorId) count++;
    });

    return count > 1;
}

function validateAllMonitors() {
    const container = document.getElementById('destaque-container');
    const allSelects = container.querySelectorAll('select[name$="-monitor"]');

    allSelects.forEach(select => {
        select.style.border = '';
        if (isMonitorAlreadySelected(select)) {
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
        console.log(obsField, exigeObs)
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