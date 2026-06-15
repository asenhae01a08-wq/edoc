document.getElementById("cpf").addEventListener("input", function () {

let cpf = this.value.replace(/\D/g, "");

cpf = cpf.replace(/^(\d{3})(\d)/, "$1.$2");
cpf = cpf.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
cpf = cpf.replace(/\.(\d{3})(\d)/, ".$1-$2");

this.value = cpf;

});

document.getElementById("formAluno").addEventListener("submit", function(event){

event.preventDefault();

let nome = document.getElementById("nome").value;
let matricula = document.getElementById("matricula").value;
let cpf = document.getElementById("cpf").value;
let email = document.getElementById("email").value;
let dataNascimento = document.getElementById("dataNascimento").value;

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
return;
}

alert("Aluno cadastrado com sucesso!");

console.log("Nome:", nome);
console.log("Matrícula:", matricula);
console.log("CPF:", cpf);
console.log("Email:", email);
console.log("Data de nascimento:", dataNascimento);

document.getElementById("formAluno").reset();

});