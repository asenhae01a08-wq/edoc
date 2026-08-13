const campoCpf = document.getElementById("cpf");
const formAluno = document.getElementById("formAluno");

if (campoCpf) {
    campoCpf.addEventListener("input", function () {
        let cpf = this.value.replace(/\D/g, "").slice(0, 11);

        cpf = cpf.replace(/^(\d{3})(\d)/, "$1.$2");
        cpf = cpf.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
        cpf = cpf.replace(/\.(\d{3})(\d{1,2})$/, ".$1-$2");

        this.value = cpf;
    });
}

if (formAluno) {
    formAluno.addEventListener("submit", function (event) {
        const nome = document.getElementById("nome").value.trim();
        const matricula = document.getElementById("matricula").value.trim();
        const cpf = document.getElementById("cpf").value.trim();
        const email = document.getElementById("email").value.trim();
        const dataNascimento = document.getElementById("dataNascimento").value.trim();
        const turma = document.getElementById("turma").value.trim();

        if (!nome || !matricula || !cpf || !email || !dataNascimento || !turma) {
            event.preventDefault();
            alert("Preencha todos os campos!");
            return;
        }

        if (!/^\d{7}$/.test(matricula)) {
            event.preventDefault();
            alert("A matrícula deve possuir 7 números.");
            return;
        }

        if (cpf.length !== 14) {
            event.preventDefault();
            alert("Digite um CPF válido!");
        }
    });
}
