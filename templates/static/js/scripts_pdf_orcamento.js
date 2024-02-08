const pdfContainer = document.getElementById('paginas_pdf_orcamento');
let scale = 1.0;


function imprimir() {
    let style = document.getElementById('estilo_impressao').cloneNode(true);
    let printWindow = window.open('', '_blank');
    printWindow.document.body.appendChild(style);
    let paginas = document.querySelectorAll('.pagina');

    paginas.forEach(function (pagina, index) {
        let divPagina = document.createElement('div');
        divPagina.style.pageBreakBefore = 'always';
        let conteudoPagina = pagina.cloneNode(true);
        divPagina.appendChild(conteudoPagina);
        printWindow.document.body.appendChild(divPagina);
    });

    let checkReady = setInterval(function () {
        if (printWindow.document.readyState === "complete") {
            clearInterval(checkReady);
            printWindow.print();
            printWindow.document.close();
            printWindow.close();
        }
    }, 50);
}

document.addEventListener('keydown', function (event) {
    if (event.key === 'p' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault()

        imprimir()
    }
});

document.addEventListener('wheel', (event) => {
    if (event.ctrlKey) {
        event.preventDefault();
        const direction = event.deltaY > 0 ? -0.1 : 0.1;
        scale += direction / 2;
        scale = Math.max(0.2, Math.min(scale, 1.0));

        updateScale();
    }
}, {passive: false});

function updateScale() {
    if (scale <= 1.0) {
        document.querySelectorAll('#paginas_pdf_orcamento').forEach(page => {
            page.style.transform = `scale(${scale})`
        });
    }
}

function createPDF() {
    const doc = new jsPDF()
    var specialElementHandlers = {
        '#getPDF': function (element, renderer) {
            return true;
        },
        '.controls': function (element, renderer) {
            return true;
        }
    };

    // All units are in the set measurement for the document
    // This can be changed to "pt" (points), "mm" (Default), "cm", "in"
    doc.fromHTML($('.pagina').get(0), 15, 15, {
        'width': 170,
        'elementHandlers': specialElementHandlers
    });
}