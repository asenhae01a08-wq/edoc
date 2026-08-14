const boasVindas = document.getElementById("boasVindas");

if (boasVindas && boasVindas.dataset.nome) {
    boasVindas.textContent = `BEM-VINDO, ${boasVindas.dataset.nome.toUpperCase()}!`;
}
