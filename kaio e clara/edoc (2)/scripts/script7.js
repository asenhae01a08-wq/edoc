function enviarEmail() {
let email = document.getElementById("email").value;
let msg = document.getElementById("mensagem");

if(email === ""){

msg.style.color = "#ffb6b6";
msg.innerHTML = "Digite um e-mail válido!";

retornar;
}

msg.style.color = "#b6ffb6";
msg.innerHTML =
"Instruções enviadas para: " + email;
}

function voltarLogin(){

alert("Redirecionando para a tela de login...");
}