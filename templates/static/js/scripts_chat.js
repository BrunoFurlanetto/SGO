let id_orcamento

function sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const chatContainer = document.getElementById("chatContainer");
    const messageText = messageInput.value.trim();

    if (messageText === "") return;

    // Criando a mensagem temporária no DOM
    const newMessage = document.createElement("div");
    newMessage.classList.add("mensagem", "remetente");

    const conteudoDiv = document.createElement("div");
    conteudoDiv.classList.add("conteudo");
    conteudoDiv.textContent = messageText;

    const infosDiv = document.createElement("div");
    infosDiv.classList.add("infos");

    const dataHoraDiv = document.createElement("div");
    dataHoraDiv.classList.add("data_hora");
    const now = new Date();
    dataHoraDiv.textContent = now.toLocaleDateString("pt-BR") + " " + now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

    const checkIcon = document.createElement("i");
    checkIcon.classList.add("bx", "bx-check");

    infosDiv.appendChild(dataHoraDiv);
    infosDiv.appendChild(checkIcon);
    newMessage.appendChild(conteudoDiv);
    newMessage.appendChild(infosDiv);
    chatContainer.appendChild(newMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Enviando a mensagem via AJAX
    $.ajax({
        type: "POST",
        url: "/mensagens/orcamento/salvar/",
        headers: { "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val() },
        data: {
            mensagem: messageText,
            id_orcamento: id_orcamento,
            id_destinatario: $('#chatModal #id_destinatario').val(),
        },
        success: function (response) {
            $('.responder-orcamento').prop('disabled', false)
        },
        error: function (xhr, status, error) {
            newMessage.remove(); // Remove a mensagem temporária
            alert("Erro ao enviar a mensagem: " + xhr.responseText);
        }
    });

    messageInput.value = ""; // Limpa o campo de entrada
}


function abrir_chat_orcamento(id_orcamento_vendo) {
    id_orcamento = id_orcamento_vendo

    $.ajax({
        type: "GET",
        url: "/mensagens/encontrar_chat/orcamento/",
        headers: { "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val() },
        data: { "id_orcamento": parseInt(id_orcamento) },
        success: function (response) {
            let chatContainer = $("#chatContainer");
            $('#chatModal #id_destinatario').val(response['ultimo_destinatario']['id'])
            $('#chatModalLabel #destinatario').text(response['ultimo_destinatario']['nome'])
            $('#chatModalLabel #cliente').text(response['cliente'])
            $('#div_gerente_responsavel #gerente_responsavel').val(response['gerente_responsavel'])
            chatContainer.empty(); // Limpa o chat antes de adicionar mensagens

            if ((!response['aprovado'] && !response['negado'])) {
                $('#reenviar_pedido').addClass('none')
            } else {
                $('#reenviar_pedido').removeClass('none')
            }

            if (response['aprovado'] ) {
                $('.botoes-resposta').addClass('none')
            } else {
                $('.botoes-resposta').removeClass('none')
            }

            response['mensagens'].forEach(mensagem => {
                let mensagemHtml = `
                    <div class="mensagem ${mensagem['responsavel']}">
                        <div class="conteudo">${mensagem['conteudo']}</div>
                        <div class="infos">
                            <div class="data_hora">${mensagem['remetente']} - ${mensagem['data_hora_envio']}</div>
                            ${mensagem['responsavel'] === "remetente" 
                                ? (mensagem['lida'] ? "<i class='bx bx-check-double'></i>" : "<i class='bx bx-check'></i>") 
                                : ""}
                        </div>
                    </div>
                `;
                chatContainer.append(mensagemHtml);
            });

            setTimeout(() => {
                chatContainer.scrollTop(chatContainer[0].scrollHeight)
            }, 100)
        },
        error: function (xhr, status, error) {
            console.error("Erro ao carregar chat:", error);
        }
    })

    $("#chatModal").modal("show")
}

function reenviar_pedido() {
    $.ajax({
        type: "POST",
        url: "/orcamento/reenio_pedido_gerencia/",
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {"id_orcamento": parseInt(id_orcamento)},
        success: function (response) {
            window.location.reload()
        },
        error: function (xhr, status, error) {
            alert(xhr.responseText)
        }
    })
}

function negar_orcamento() {
    $.ajax({
        type: "POST",
        url: "/orcamento/negar/",
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {"id_orcamento": parseInt(id_orcamento)},
        success: function (response) {
            window.location.href = '/dashboard/'
        },
        error: function (xhr, status, error) {
            alert(xhr.responseText)
        }
    })
}

function trocar_gerente() {
    console.log($('#gerente_responsavel').val())
    $.ajax({
        type: "POST",
        url: "/orcamento/trocar_gerente_responsavel/",
        headers: {"X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()},
        data: {
            "id_orcamento": parseInt(id_orcamento),
            'id_novo_gerente': parseInt($('#div_gerente_responsavel #gerente_responsavel').val())
        },
        success: function (response) {
            window.location.href = '/dashboard/'
        },
        error: function (xhr, status, error) {
            alert(xhr.responseText)
            window.location.href = '/dashboard/'
        }
    })
}