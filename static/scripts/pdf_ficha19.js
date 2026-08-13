(function () {

    const dados =
        window.dadosFichaEdoc;


    if (!dados) {

        return;

    }


    // ==========================================================
    // PEGA ID DO ALUNO
    // ==========================================================

    function obterAlunoIdAtual() {

        const parametros =
            new URLSearchParams(
                window.location.search
            );


        const alunoId =
            parametros.get(
                "aluno_id"
            );


        if (
            alunoId &&
            /^\d+$/.test(alunoId)
        ) {

            return alunoId;

        }


        const rotaAntiga =
            window.location.pathname.match(
                /\/telagerar\/(\d+)/
            );


        if (rotaAntiga) {

            return rotaAntiga[1];

        }


        return null;

    }


    // ==========================================================
    // CARREGA BIBLIOTECA DE PDF
    // ==========================================================

    function carregarHtml2Pdf() {

        return new Promise(
            function (
                resolve,
                reject
            ) {

                if (
                    window.html2pdf
                ) {

                    resolve(
                        window.html2pdf
                    );

                    return;

                }


                const existente =
                    document.getElementById(
                        "bibliotecaHtml2Pdf"
                    );


                if (existente) {

                    existente.addEventListener(
                        "load",
                        function () {

                            resolve(
                                window.html2pdf
                            );

                        }
                    );


                    existente.addEventListener(
                        "error",
                        function () {

                            reject(
                                new Error(
                                    "Não foi possível carregar "
                                    + "a biblioteca de PDF."
                                )
                            );

                        }
                    );


                    return;

                }


                const script =
                    document.createElement(
                        "script"
                    );


                script.id =
                    "bibliotecaHtml2Pdf";


                script.src =
                    "https://cdnjs.cloudflare.com/ajax/libs/"
                    + "html2pdf.js/0.10.1/"
                    + "html2pdf.bundle.min.js";


                script.async = true;


                script.onload =
                    function () {

                        if (
                            window.html2pdf
                        ) {

                            resolve(
                                window.html2pdf
                            );

                        } else {

                            reject(
                                new Error(
                                    "Biblioteca de PDF "
                                    + "não carregada."
                                )
                            );

                        }

                    };


                script.onerror =
                    function () {

                        reject(
                            new Error(
                                "Não foi possível carregar "
                                + "a biblioteca de PDF. "
                                + "Verifique a internet."
                            )
                        );

                    };


                document.head.appendChild(
                    script
                );

            }
        );

    }


    // ==========================================================
    // SINCRONIZA OS VALORES DOS CAMPOS
    // ==========================================================

    function sincronizarValoresParaPdf(
        elementoRaiz
    ) {

        elementoRaiz
            .querySelectorAll(
                "input"
            )
            .forEach(
                function (campo) {

                    if (
                        campo.type ===
                        "checkbox" ||
                        campo.type ===
                        "radio"
                    ) {

                        if (
                            campo.checked
                        ) {

                            campo.setAttribute(
                                "checked",
                                "checked"
                            );

                        } else {

                            campo.removeAttribute(
                                "checked"
                            );

                        }


                        return;

                    }


                    campo.setAttribute(

                        "value",

                        campo.value || ""

                    );

                }
            );


        elementoRaiz
            .querySelectorAll(
                "textarea"
            )
            .forEach(
                function (campo) {

                    campo.textContent =
                        campo.value || "";

                }
            );


        elementoRaiz
            .querySelectorAll(
                "select"
            )
            .forEach(
                function (select) {

                    Array
                        .from(
                            select.options
                        )
                        .forEach(
                            function (
                                opcao
                            ) {

                                if (
                                    opcao.selected
                                ) {

                                    opcao
                                        .setAttribute(
                                            "selected",
                                            "selected"
                                        );

                                } else {

                                    opcao
                                        .removeAttribute(
                                            "selected"
                                        );

                                }

                            }
                        );

                }
            );

    }


    // ==========================================================
    // AJUSTE VISUAL TEMPORÁRIO PARA O PDF
    // ==========================================================

    function aplicarEstiloTemporarioPdf(
        formulario
    ) {

        const estado = {

            formularioStyle:
                formulario.getAttribute(
                    "style"
                ),

            folhas: []

        };


        const folhas =
            Array.from(
                formulario
                    .querySelectorAll(
                        ".folha"
                    )
            );


        formulario.style.margin =
            "0";

        formulario.style.padding =
            "0";

        formulario.style.background =
            "#ffffff";


        folhas.forEach(
            function (
                folha,
                indice
            ) {

                estado.folhas.push({

                    elemento:
                        folha,

                    style:
                        folha.getAttribute(
                            "style"
                        )

                });


                folha.style.margin =
                    "0 auto";

                folha.style.boxShadow =
                    "none";

                folha.style.pageBreakInside =
                    "avoid";

                folha.style.breakInside =
                    "avoid";


                if (
                    indice <
                    folhas.length - 1
                ) {

                    folha.style
                        .pageBreakAfter =
                        "always";

                    folha.style
                        .breakAfter =
                        "page";

                } else {

                    folha.style
                        .pageBreakAfter =
                        "auto";

                    folha.style
                        .breakAfter =
                        "auto";

                }

            }
        );


        return estado;

    }


    // ==========================================================
    // RESTAURA VISUAL DA TELA
    // ==========================================================

    function restaurarEstiloDepoisPdf(
        formulario,
        estado
    ) {

        if (
            estado.formularioStyle
            === null
        ) {

            formulario
                .removeAttribute(
                    "style"
                );

        } else {

            formulario
                .setAttribute(

                    "style",

                    estado
                        .formularioStyle

                );

        }


        estado.folhas.forEach(
            function (item) {

                if (
                    item.style === null
                ) {

                    item.elemento
                        .removeAttribute(
                            "style"
                        );

                } else {

                    item.elemento
                        .setAttribute(

                            "style",

                            item.style

                        );

                }

            }
        );

    }


    // ==========================================================
    // NOME DO PDF
    // ==========================================================

    function nomePdfAtual() {

        const matricula =
            String(

                (
                    dados.aluno ||
                    {}
                ).matricula ||

                "aluno"

            )
                .replace(
                    /[^0-9A-Za-z_-]/g,
                    ""
                )
                .trim();


        return (
            "ficha19_" +
            (
                matricula ||
                "aluno"
            ) +
            ".pdf"
        );

    }


    // ==========================================================
    // GERA, SALVA E BAIXA
    // ==========================================================

    async function salvarEBaixarPdf(
        botao,
        alunoId
    ) {

        const textoOriginal =
            botao.innerHTML;


        let formulario =
            null;


        let estadoVisual =
            null;


        try {

            botao.disabled =
                true;


            botao.innerHTML =
                '<i class="fa-solid '
                + 'fa-spinner '
                + 'fa-spin"></i> '
                + 'Gerando PDF...';


            await carregarHtml2Pdf();


            formulario =
                document.getElementById(
                    "formFicha19"
                );


            if (
                !formulario
            ) {

                throw new Error(
                    "A área da Ficha 19 "
                    + "não foi encontrada."
                );

            }


            sincronizarValoresParaPdf(
                formulario
            );


            estadoVisual =
                aplicarEstiloTemporarioPdf(
                    formulario
                );


            const opcoes = {

                margin:
                    0,

                filename:
                    nomePdfAtual(),

                image: {

                    type:
                        "jpeg",

                    quality:
                        1

                },

                html2canvas: {

                    scale:
                        2,

                    useCORS:
                        true,

                    allowTaint:
                        false,

                    logging:
                        false,

                    scrollX:
                        0,

                    scrollY:
                        0,

                    backgroundColor:
                        "#ffffff"

                },

                jsPDF: {

                    unit:
                        "mm",

                    format:
                        "a4",

                    orientation:
                        "portrait"

                },

                pagebreak: {

                    mode: [

                        "css",

                        "legacy"

                    ]

                }

            };


            const blobPdf =
                await window
                    .html2pdf()
                    .set(
                        opcoes
                    )
                    .from(
                        formulario
                    )
                    .toPdf()
                    .outputPdf(
                        "blob"
                    );


            const formularioEnvio =
                new FormData();


            formularioEnvio.append(

                "arquivo_pdf",

                blobPdf,

                nomePdfAtual()

            );


            const resposta =
                await fetch(

                    "/ficha19/salvar-pdf/"
                    + alunoId,

                    {

                        method:
                            "POST",

                        body:
                            formularioEnvio

                    }

                );


            let resultado =
                null;


            try {

                resultado =
                    await resposta.json();

            } catch (
            erroJson
            ) {

                throw new Error(
                    "O servidor retornou "
                    + "uma resposta inválida."
                );

            }


            if (
                !resposta.ok ||
                !resultado.sucesso
            ) {

                throw new Error(

                    resultado.mensagem ||

                    "Não foi possível "
                    + "salvar o PDF."

                );

            }


            // ==========================================
            // DOWNLOAD
            // ==========================================

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                resultado.download_url;


            link.style.display =
                "none";


            document.body.appendChild(
                link
            );


            link.click();


            link.remove();


        } catch (erro) {

            console.error(

                "Erro ao gerar/salvar PDF:",

                erro

            );


            alert(

                "Não foi possível gerar "
                + "o PDF: "
                + erro.message

            );


        } finally {

            if (
                formulario &&
                estadoVisual
            ) {

                restaurarEstiloDepoisPdf(

                    formulario,

                    estadoVisual

                );

            }


            botao.disabled =
                false;


            botao.innerHTML =
                textoOriginal;

        }

    }


    // ==========================================================
    // CRIA BOTÃO AUTOMATICAMENTE
    // ==========================================================

    function criarBotaoSalvarPdf() {

        const alunoId =
            obterAlunoIdAtual();


        if (
            !alunoId
        ) {

            return;

        }


        const areaAcoes =
            document.querySelector(
                ".acoes-edoc"
            );


        if (
            !areaAcoes
        ) {

            return;

        }


        if (
            document.getElementById(
                "botaoSalvarBaixarPdf"
            )
        ) {

            return;

        }


        const botao =
            document.createElement(
                "button"
            );


        botao.type =
            "button";


        botao.id =
            "botaoSalvarBaixarPdf";


        botao.className =
            "botao-edoc "
            + "botao-imprimir";


        botao.innerHTML =
            '<i class="fa-solid '
            + 'fa-download"></i> '
            + 'Salvar e baixar PDF';


        botao.addEventListener(

            "click",

            function () {

                salvarEBaixarPdf(

                    botao,

                    alunoId

                );

            }

        );


        areaAcoes.appendChild(
            botao
        );

    }


    criarBotaoSalvarPdf();

})();