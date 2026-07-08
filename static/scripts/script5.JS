document.getElementById("cpf").addEventListener("input", function () {

let cpf = this.value.replace(/\D/g, "");

cpf = cpf.replace(/^(\d{3})(\d)/, "$1.$2");
cpf = cpf.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
cpf = cpf.replace(/\.(\d{3})(\d)/, ".$1-$2");

this.value = cpf;

});

document.getElementById("formAluno").addEventListener("submit", function(event){

let nome = document.getElementById("nome").value.trim;
let matricula = document.getElementById("matricula").value.trim;
let cpf = document.getElementById("cpf").value.trim;
let email = document.getElementById("email").value.trim;
let dataNascimento = document.getElementById("dataNascimento").value.trim;

if(
nome.trim() === "" ||
matricula.trim() === "" ||
cpf.trim() === "" ||
email.trim() === "" ||
dataNascimento.trim() === ""
){
alert("Preencha todos os campos!");
return;
}

if(cpf.length !== 14){
alert("Digite um CPF válido!");
event.preventDefault();
return;
}

});