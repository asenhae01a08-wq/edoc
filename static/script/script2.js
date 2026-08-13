const loginForm = document.getElementById("loginForm");
const identificacao = document.getElementById("identificacao");
const senha = document.getElementById("senha");
const toggleSenha = document.getElementById("toggleSenha");

if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
        const usuario = identificacao.value.trim();
        const valorSenha = senha.value;

        if (usuario === "" || valorSenha === "") {
            event.preventDefault();
            alert("Preencha todos os campos!");
            return;
        }

        const matriculaValida = /^\d{7}$/.test(usuario);
        const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(usuario);

        if (!matriculaValida && !emailValido) {
            event.preventDefault();
            alert("Digite uma matrícula com 7 números ou um e-mail válido.");
        }
    });
}

if (toggleSenha && senha) {
    toggleSenha.addEventListener("click", function () {
        const mostrar = senha.type === "password";
        senha.type = mostrar ? "text" : "password";

        const icone = toggleSenha.querySelector("i");
        if (icone) {
            icone.classList.toggle("fa-eye", !mostrar);
            icone.classList.toggle("fa-eye-slash", mostrar);
        }

        toggleSenha.setAttribute(
            "aria-label",
            mostrar ? "Esconder senha" : "Mostrar senha"
        );
    });
}
