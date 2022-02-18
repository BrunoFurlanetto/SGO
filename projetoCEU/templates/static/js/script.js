let arrow = document.querySelectorAll(".arrow");
for (var i = 0; i < arrow.length; i++) {
    arrow[i].addEventListener("click", (e)=>{
    let arrowParent = e.target.parentElement.parentElement;//selecting main parent of arrow
    arrowParent.classList.toggle("showMenu");
    });
}

let arrow_2 = document.querySelectorAll(".arrow-2");
for (var j = 0; j < arrow_2.length; j++) {
    arrow_2[j].addEventListener("click", (e)=>{
    let arrow_2Parent = e.target.parentElement.parentElement;//selecting main parent of arrow
    arrow_2Parent.classList.toggle("showMenu-2");
    });
}

let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".bx-menu");
let itens = document.querySelector(".item-sidebar")
sidebarBtn.addEventListener("click", ()=>{
    sidebar.classList.toggle("close");
    itens.classlist.add('foi')
});
let sidebarBtn2 = document.querySelector(".bxs-calendar");
sidebarBtn2.addEventListener("click", ()=>{
    sidebar.classList.toggle("close");
});
