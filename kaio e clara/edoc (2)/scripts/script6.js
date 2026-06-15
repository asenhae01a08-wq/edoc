const pesquisa = document.getElementById("pesquisa");

pesquisa.addEventListener("keyup", () => {

const valor = pesquisa.value.toLowerCase();

const documentos = document.querySelectorAll(".documento");

documentos.forEach(item => {

const nome = item.querySelector("h3")
.textContent
.toLowerCase()

item.style.display =
nome.includes(valor) ? "flex" : "nenhum";

});

});