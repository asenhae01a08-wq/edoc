document.getElementById("loginForm").addEventListener("submit", function(e){

e.preventDefault();

let email = document.getElementById("email").value;
let senha = document.getElementById("senha").value;

if(email === "" || senha === ""){
alert("Preencha todos os campos!");
return;
}

alert("Login realizado com sucesso!");

// Exemplo:
// window.location.href = "dashboard.html";

});