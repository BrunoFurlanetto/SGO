
function atualizar_eventos(){
    setInterval(() => {
        $.ajax({
            type: 'GET',
            async: true,
            url: '',
            success: function (response) {
                if(response !== localStorage.getItem('tamanho')){
                    localStorage.setItem('tamanho', response)
                    document.location.reload()
                }
            }
        })
    }, 20000)
}
