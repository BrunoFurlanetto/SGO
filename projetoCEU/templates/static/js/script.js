let arrow = document.querySelectorAll(".arrow");
for (var i = 0; i < arrow.length; i++) {
    arrow[i].addEventListener("click", (e)=>{
    let arrowParent = e.target.parentElement.parentElement;//selecting main parent of arrow
    arrowParent.classList.toggle("showMenu");
    });
}

let arrow_2 = document.querySelectorAll(".arrow-2");
for (let j = 0; j < arrow_2.length; j++) {
    arrow_2[j].addEventListener("click", (e)=>{
    let arrow_2Parent = e.target.parentElement.parentElement;//selecting main parent of arrow
    arrow_2Parent.classList.toggle("showMenu-2");
    });
}

let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".bx-menu");
let sidebarBtn2 = document.querySelector(".bxs-calendar");
let itens = document.getElementsByClassName("item-sidebar");

sidebarBtn.addEventListener("click", ()=>{
    sidebar.classList.toggle("close");
    console.log(sidebar.classList)

    for (let i in itens){
        itens[i].classList.toggle('baixo')
    }

    if (sidebar.classList.contains('close')) {
        for (let i in itens) {
            itens[i].classList.add('cima')
        }
    } else {
        for (let i in itens) {
            itens[i].classList.add('cima')
        }
    }

});

sidebarBtn2.addEventListener("click", ()=>{
    sidebar.classList.toggle("close");

        for (let i in itens){
        itens[i].classList.toggle('baixo')
    }

});
