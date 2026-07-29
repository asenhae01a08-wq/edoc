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

document.getElementById("loginForm").addEventListener("submit", function(e){

    e.preventDefault();

    let usuario = document.getElementById("usuario").value.trim();
    let senha = document.getElementById("senha").value;

    if(usuario === "" || senha === ""){
        alert("Preencha todos os campos!");
        return;
    }

    // LOGIN DE ALUNO
    if(/^\d{7}$/.test(usuario)){
     console.log("Login de aluno");


        // Aqui depois o Flask verifica:
        // matrícula = usuario
        // senha = matrícula invertida

    }

    // LOGIN DE PROFISSIONAL
    else if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(usuario)){

        console.log("Login de Profissional");

    }

    else{

        alert("Digite uma matrícula com 7 números ou um e-mail válido.");

    }

});
