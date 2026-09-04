(function () {
    "use strict";

    const LIMITE_ARQUIVOS = 200;

    const input =
        document.getElementById("arquivoSiepe");

    const nomeArquivo =
        document.getElementById("nomeArquivo");

    if (!input) {
        return;
    }

    const form =
        input.closest("form");

    if (!form) {
        return;
    }

    // Garante seleção múltipla
    input.multiple = true;

    const botaoEnviar =
        form.querySelector('button[type="submit"]');

    // =========================================================
    // ESTILO DO PAINEL DE IMPORTAÇÃO
    // =========================================================

    const estilo =
        document.createElement("style");

    estilo.textContent = `
        .edoc-lote-painel {
            background: #ffffff;
            border: 1px solid #cfd5dc;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            display: none;
            margin: 0 auto 15px;
            max-width: 210mm;
            padding: 12px;
        }

        .edoc-lote-painel.ativo {
            display: block;
        }

        .edoc-lote-topo {
            align-items: center;
            display: flex;
            gap: 12px;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .edoc-lote-topo strong {
            color: #17365d;
            font-size: 13px;
        }

        .edoc-lote-resumo {
            color: #555555;
            font-size: 12px;
        }

        .edoc-lote-barra {
            background: #e8edf2;
            border-radius: 999px;
            height: 9px;
            overflow: hidden;
            width: 100%;
        }

        .edoc-lote-progresso {
            background: #1e5f9e;
            height: 100%;
            transition: width 0.2s ease;
            width: 0%;
        }

        .edoc-lote-atual {
            color: #555555;
            font-size: 11px;
            margin-top: 7px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .edoc-lote-lista {
            border-top: 1px solid #e5e8ec;
            list-style: none;
            margin-top: 10px;
            max-height: 250px;
            overflow-y: auto;
            padding: 8px 0 0;
        }

        .edoc-lote-item {
            align-items: flex-start;
            display: flex;
            font-size: 11px;
            gap: 7px;
            line-height: 1.4;
            padding: 4px 0;
        }

        .edoc-lote-item.sucesso {
            color: #1f6a3e;
        }

        .edoc-lote-item.erro {
            color: #a52a2a;
        }

        .edoc-lote-item a {
            color: inherit;
            font-weight: bold;
        }

        @media print {
            .edoc-lote-painel {
                display: none !important;
            }
        }
    `;

    document.head.appendChild(estilo);

    // =========================================================
    // CRIA PAINEL DE PROGRESSO
    // =========================================================

    const painel =
        document.createElement("section");

    painel.className =
        "edoc-lote-painel";

    painel.innerHTML = `
        <div class="edoc-lote-topo">

            <strong id="edocLoteTitulo">
                Importação em lote
            </strong>

            <span
                class="edoc-lote-resumo"
                id="edocLoteResumo"
            ></span>

        </div>

        <div class="edoc-lote-barra">

            <div
                class="edoc-lote-progresso"
                id="edocLoteProgresso"
            ></div>

        </div>

        <div
            class="edoc-lote-atual"
            id="edocLoteAtual"
        ></div>

        <ul
            class="edoc-lote-lista"
            id="edocLoteLista"
        ></ul>
    `;

    const barra =
        document.querySelector(".barra-edoc");

    if (barra) {

        barra.insertAdjacentElement(
            "afterend",
            painel
        );

    } else {

        form.insertAdjacentElement(
            "afterend",
            painel
        );

    }

    const titulo =
        painel.querySelector(
            "#edocLoteTitulo"
        );

    const resumo =
        painel.querySelector(
            "#edocLoteResumo"
        );

    const progresso =
        painel.querySelector(
            "#edocLoteProgresso"
        );

    const atual =
        painel.querySelector(
            "#edocLoteAtual"
        );

    const lista =
        painel.querySelector(
            "#edocLoteLista"
        );

    // =========================================================
    // ARQUIVOS
    // =========================================================

    function arquivosSelecionados() {

        return Array.from(
            input.files || []
        );

    }

    function arquivoEhValido(
        arquivo
    ) {

        if (
            !arquivo ||
            !arquivo.name
        ) {

            return false;

        }

        const nome =
            arquivo.name
                .toLowerCase();

        return (
            nome.endsWith(".pdf") ||
            nome.endsWith(".xlsx")
        );

    }

    function validarSelecao(
        arquivos,
        mostrarAlerta = true
    ) {

        if (!arquivos.length) {

            return false;

        }

        // -----------------------------------------------------
        // LIMITE DE ARQUIVOS
        // -----------------------------------------------------

        if (
            arquivos.length >
            LIMITE_ARQUIVOS
        ) {

            if (mostrarAlerta) {

                alert(
                    "Selecione no máximo " +
                    LIMITE_ARQUIVOS +
                    " arquivos por vez."
                );

            }

            return false;

        }

        // -----------------------------------------------------
        // VALIDA PDF / XLSX
        // -----------------------------------------------------

        const invalidos =
            arquivos.filter(
                function (arquivo) {

                    return !arquivoEhValido(
                        arquivo
                    );

                }
            );

        if (invalidos.length) {

            if (mostrarAlerta) {

                alert(
                    "Todos os arquivos devem estar no formato PDF ou XLSX."
                );

            }

            return false;

        }

        return true;

    }

    // =========================================================
    // NOME DOS ARQUIVOS SELECIONADOS
    // =========================================================

    function atualizarNomeSelecao() {

        const arquivos =
            arquivosSelecionados();

        if (!arquivos.length) {

            if (nomeArquivo) {

                nomeArquivo.textContent =
                    "Nenhum arquivo selecionado";

            }

            return;

        }

        if (
            !validarSelecao(
                arquivos,
                true
            )
        ) {

            input.value = "";

            if (nomeArquivo) {

                nomeArquivo.textContent =
                    "Nenhum arquivo selecionado";

            }

            return;

        }

        if (!nomeArquivo) {

            return;

        }

        if (
            arquivos.length === 1
        ) {

            nomeArquivo.textContent =
                arquivos[0].name;

            return;

        }

        nomeArquivo.textContent =
            arquivos.length +
            " arquivos selecionados";

    }

    input.addEventListener(
        "change",
        atualizarNomeSelecao
    );

    // =========================================================
    // PAINEL DE RESULTADOS
    // =========================================================

    function limparResultados() {

        lista.innerHTML = "";

        progresso.style.width =
            "0%";

        atual.textContent = "";

        resumo.textContent = "";

    }

    function adicionarResultado(
        resultado
    ) {

        const item =
            document.createElement(
                "li"
            );

        item.className =
            "edoc-lote-item " +
            (
                resultado.sucesso
                    ? "sucesso"
                    : "erro"
            );

        const icone =
            document.createElement(
                "span"
            );

        icone.textContent =
            resultado.sucesso
                ? "✓"
                : "✕";

        item.appendChild(
            icone
        );

        const texto =
            document.createElement(
                "span"
            );

        // -----------------------------------------------------
        // SUCESSO
        // -----------------------------------------------------

        if (resultado.sucesso) {

            const nome =
                resultado.nome ||
                "Aluno";

            const matricula =
                resultado.matricula
                    ? " — " +
                      resultado.matricula
                    : "";

            texto.appendChild(
                document.createTextNode(
                    resultado.arquivo +
                    ": " +
                    nome +
                    matricula +
                    " "
                )
            );

            if (
                resultado.url_ficha
            ) {

                const link =
                    document.createElement(
                        "a"
                    );

                link.href =
                    resultado.url_ficha;

                link.textContent =
                    "Abrir ficha";

                link.target =
                    "_blank";

                link.rel =
                    "noopener noreferrer";

                texto.appendChild(
                    link
                );

            }

        }

        // -----------------------------------------------------
        // ERRO
        // -----------------------------------------------------

        else {

            texto.textContent =
                resultado.arquivo +
                ": " +
                (
                    resultado.erro ||
                    "Erro desconhecido."
                );

        }

        item.appendChild(
            texto
        );

        lista.appendChild(
            item
        );

        lista.scrollTop =
            lista.scrollHeight;

    }

    // =========================================================
    // ENVIA UM ARQUIVO POR VEZ
    // =========================================================

    async function enviarArquivo(
        arquivo
    ) {

        const dados =
            new FormData();

        dados.append(
            "arquivoSiepe",
            arquivo,
            arquivo.name
        );

        const resposta =
            await fetch(
                form.action,
                {
                    method:
                        "POST",

                    body:
                        dados,

                    credentials:
                        "same-origin",

                    headers: {

                        "X-EDOC-BATCH":
                            "1",

                        "Accept":
                            "application/json"

                    }
                }
            );

        // -----------------------------------------------------
        // SESSÃO EXPIRADA
        // -----------------------------------------------------

        if (
            resposta.redirected &&
            resposta.url.includes(
                "/login"
            )
        ) {

            const erro =
                new Error(
                    "Sua sessão expirou. " +
                    "Faça login novamente."
                );

            erro.codigo =
                "SESSAO_EXPIRADA";

            throw erro;

        }

        // -----------------------------------------------------
        // TIPO DA RESPOSTA
        // -----------------------------------------------------

        const tipo =
            resposta.headers.get(
                "content-type"
            ) || "";

        if (
            !tipo.includes(
                "application/json"
            )
        ) {

            if (
                resposta.status === 413
            ) {

                throw new Error(
                    "O arquivo ultrapassa o limite de 15 MB."
                );

            }

            throw new Error(
                "O servidor não retornou uma resposta válida para este arquivo."
            );

        }

        const retorno =
            await resposta.json();

        // -----------------------------------------------------
        // ERRO DO BACK-END
        // -----------------------------------------------------

        if (
            !resposta.ok ||
            !retorno.sucesso
        ) {

            throw new Error(
                retorno.erro ||
                retorno.mensagem ||
                "Não foi possível importar o arquivo."
            );

        }

        return retorno;

    }

    // =========================================================
    // SUBMIT
    // =========================================================

    form.addEventListener(
        "submit",
        async function (evento) {

            const arquivos =
                arquivosSelecionados();

            // =================================================
            // UM ÚNICO ARQUIVO
            //
            // Deixa o formulário seguir normalmente.
            // O Flask cuida de PDF ou XLSX.
            // =================================================

            if (
                arquivos.length <= 1
            ) {

                return;

            }

            // =================================================
            // LOTE
            // =================================================

            evento.preventDefault();

            if (
                !validarSelecao(
                    arquivos,
                    true
                )
            ) {

                return;

            }

            limparResultados();

            painel.classList.add(
                "ativo"
            );

            titulo.textContent =
                "Importando " +
                arquivos.length +
                " arquivos";

            let sucessos = 0;

            let erros = 0;

            let interrompido =
                false;

            // -------------------------------------------------
            // DESABILITA BOTÃO
            // -------------------------------------------------

            if (botaoEnviar) {

                botaoEnviar.disabled =
                    true;

                botaoEnviar.dataset
                    .textoOriginal =
                        botaoEnviar
                            .innerHTML;

                botaoEnviar.innerHTML =
                    '<i class="fa-solid ' +
                    'fa-spinner fa-spin"></i> ' +
                    "Importando...";

            }

            input.disabled =
                true;

            // -------------------------------------------------
            // ENVIA UM POR VEZ
            // -------------------------------------------------

            for (
                let indice = 0;
                indice < arquivos.length;
                indice++
            ) {

                const arquivo =
                    arquivos[indice];

                atual.textContent =
                    "Processando " +
                    (indice + 1) +
                    " de " +
                    arquivos.length +
                    ": " +
                    arquivo.name;

                try {

                    const retorno =
                        await enviarArquivo(
                            arquivo
                        );

                    sucessos++;

                    adicionarResultado(
                        {
                            ...retorno,

                            sucesso:
                                true,

                            arquivo:
                                arquivo.name
                        }
                    );

                } catch (erro) {

                    erros++;

                    adicionarResultado(
                        {
                            sucesso:
                                false,

                            arquivo:
                                arquivo.name,

                            erro:
                                erro.message
                        }
                    );

                    if (
                        erro.codigo ===
                        "SESSAO_EXPIRADA"
                    ) {

                        interrompido =
                            true;

                    }

                }

                // ---------------------------------------------
                // PROGRESSO
                // ---------------------------------------------

                const processados =
                    indice + 1;

                progresso.style.width =
                    (
                        processados /
                        arquivos.length *
                        100
                    ) +
                    "%";

                resumo.textContent =
                    sucessos +
                    " sucesso(s) · " +
                    erros +
                    " erro(s)";

                if (
                    interrompido
                ) {

                    break;

                }

            }

            // =================================================
            // FINAL
            // =================================================

            if (
                interrompido
            ) {

                titulo.textContent =
                    "Importação interrompida";

                atual.textContent =
                    "Faça login novamente e " +
                    "reenvie os arquivos que " +
                    "não foram processados.";

            } else {

                titulo.textContent =
                    "Importação finalizada";

                atual.textContent =
                    sucessos +
                    " de " +
                    arquivos.length +
                    " arquivo(s) importado(s) " +
                    "com sucesso.";

            }

            // -------------------------------------------------
            // REATIVA INPUT
            // -------------------------------------------------

            input.disabled =
                false;

            // -------------------------------------------------
            // REATIVA BOTÃO
            // -------------------------------------------------

            if (botaoEnviar) {

                botaoEnviar.disabled =
                    false;

                botaoEnviar.innerHTML =
                    botaoEnviar.dataset
                        .textoOriginal ||
                    (
                        '<i class="fa-solid ' +
                        'fa-wand-magic-sparkles"></i> ' +
                        'Ler arquivo e gerar ficha'
                    );

            }

        }
    );

})();