(function () {
    const dados = window.dadosFichaEdoc;

    if (!dados) {
        return;
    }

    const extras = dados.extras || {};
    const escola = extras.escola || {};
    const alunoOficial = extras.aluno_oficial || {};
    const complementares = extras.informacoes_complementares || {};
    const resumoBase = extras.resumo_base_comum || [];
    const totaisBase = extras.totais_base_comum || {};
    const resultadoCurso = extras.resultado_curso || {};
    const metaItinerario = extras.itinerario_metadados || {};

    function setValor(elemento, valor) {
        if (
            !elemento ||
            valor === null ||
            valor === undefined ||
            valor === ""
        ) {
            return;
        }

        if (elemento.tagName === "SELECT") {
            const alvo = normalizar(valor);

            const opcao = Array.from(elemento.options).find(
                function (item) {
                    return (
                        normalizar(item.value) === alvo ||
                        normalizar(item.textContent) === alvo
                    );
                }
            );

            if (opcao) {
                elemento.value = opcao.value;
            }

            return;
        }

        if (
            elemento.tagName === "INPUT" ||
            elemento.tagName === "TEXTAREA"
        ) {
            elemento.value = valor;
            return;
        }

        elemento.textContent = valor;
    }

    function preencherTodos(seletor, valor) {
        if (
            valor === null ||
            valor === undefined ||
            valor === ""
        ) {
            return;
        }

        document
            .querySelectorAll(seletor)
            .forEach(function (elemento) {
                setValor(elemento, valor);
            });
    }

    function normalizar(texto) {
        return String(texto || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function dataParaInput(valor) {
        if (!valor) {
            return "";
        }

        const texto = String(valor).trim();

        if (/^\d{4}-\d{2}-\d{2}$/.test(texto)) {
            return texto;
        }

        const br = texto.match(
            /^(\d{2})\/(\d{2})\/(\d{4})$/
        );

        if (br) {
            return (
                br[3] +
                "-" +
                br[2] +
                "-" +
                br[1]
            );
        }

        return texto;
    }

    function preencherAluno() {
        const aluno = dados.aluno || {};

        setValor(
            document.getElementById("nomeAluno"),
            aluno.nome
        );

        setValor(
            document.getElementById("nomeMae"),
            aluno.nome_mae
        );

        setValor(
            document.getElementById("nomePai"),
            aluno.nome_pai
        );

        setValor(
            document.getElementById("dataNascimento"),
            aluno.data_nascimento
        );

        setValor(
            document.getElementById("cidadeNascimento"),
            alunoOficial.cidade_nascimento
        );

        setValor(
            document.getElementById("ufNascimento"),
            alunoOficial.uf_nascimento
        );

        setValor(
            document.getElementById("nacionalidade"),
            aluno.nacionalidade
        );

        setValor(
            document.getElementById("rg"),
            aluno.rg
        );

        setValor(
            document.getElementById("orgaoExpedidor"),
            aluno.orgao_expedidor
        );

        setValor(
            document.getElementById("cpf"),
            aluno.cpf
        );

        setValor(
            document.getElementById("anoConcluido"),
            alunoOficial.etapa_concluida || aluno.serie
        );

        setValor(
            document.getElementById("modalidadeEnsino"),
            alunoOficial.curso_documento ||
            aluno.curso_nome
        );

        preencherTodos(
            ".sincronizar-nome",
            aluno.nome
        );

        preencherTodos(
            ".sincronizar-matricula",
            aluno.matricula
        );
    }

    function preencherEscola() {
        if (escola.nome) {
            setValor(
                document.querySelector(
                    ".nome-escola-oficial"
                ),
                escola.nome
            );
        }

        if (escola.endereco) {
            setValor(
                document.querySelector(
                    ".endereco-escola-oficial"
                ),
                escola.endereco
            );
        }

        setValor(
            document.getElementById(
                "telefoneEscola"
            ),
            escola.telefone
        );

        setValor(
            document.getElementById(
                "autorizacaoFuncionamento"
            ),
            escola.autorizacao_funcionamento
        );

        setValor(
            document.getElementById("dataDoe"),
            escola.data_doe
        );

        preencherTodos(
            ".sincronizar-cadastro",
            escola.cadastro_escolar
        );

        preencherTodos(
            ".sincronizar-secretario",
            escola.secretario_nome
        );

        preencherTodos(
            ".sincronizar-matricula-secretario",
            escola.secretario_matricula
        );

        preencherTodos(
            ".sincronizar-diretor",
            escola.diretor_nome
        );

        preencherTodos(
            ".sincronizar-matricula-diretor",
            escola.diretor_matricula
        );

        setValor(
            document.getElementById("nomeSecretario"),
            escola.secretario_nome
        );

        setValor(
            document.getElementById(
                "matriculaSecretario"
            ),
            escola.secretario_matricula
        );

        setValor(
            document.getElementById("nomeDiretor"),
            escola.diretor_nome
        );

        setValor(
            document.getElementById(
                "matriculaDiretor"
            ),
            escola.diretor_matricula
        );
    }

    function preencherComplementares() {
        setValor(
            document.getElementById(
                "situacaoEducacaoFisica"
            ),
            complementares.situacao_educacao_fisica
        );
    }

    function preencherBaseComum() {
        const baseComum =
            Array.isArray(dados.base_comum)
                ? dados.base_comum
                : [];

        const anos = resumoBase
            .map(function (item) {
                return item.ano_letivo;
            })
            .filter(Boolean);

        setValor(
            document.getElementById("anoPrimeiro"),
            anos[0]
        );

        setValor(
            document.getElementById("anoSegundo"),
            anos[1]
        );

        setValor(
            document.getElementById("anoTerceiro"),
            anos[2]
        );

        const porComponente = {};

        baseComum.forEach(function (item) {
            const chave = normalizar(item.nome);

            if (!porComponente[chave]) {
                porComponente[chave] = {};
            }

            porComponente[chave][
                String(item.ano_letivo || "")
            ] = item;
        });

        document
            .querySelectorAll(
                "#tabelaFormacaoGeral tbody tr"
            )
            .forEach(function (linha) {
                const componenteElemento =
                    linha.querySelector(".componente");

                if (!componenteElemento) {
                    return;
                }

                const nomeComponente =
                    componenteElemento.tagName === "INPUT"
                        ? (
                            componenteElemento.value ||
                            componenteElemento.placeholder
                        )
                        : componenteElemento.textContent;

                const registros =
                    porComponente[
                    normalizar(nomeComponente)
                    ];

                if (!registros) {
                    return;
                }

                const inputs = Array.from(
                    linha.querySelectorAll("input")
                );

                const deslocamento =
                    componenteElemento.tagName === "INPUT"
                        ? 1
                        : 0;

                let totalComponente = 0;

                anos
                    .slice(0, 3)
                    .forEach(function (ano, indice) {
                        const registro =
                            registros[String(ano)];

                        if (!registro) {
                            return;
                        }

                        const posNota =
                            deslocamento +
                            indice * 2;

                        const posCh = posNota + 1;

                        if (inputs[posNota]) {
                            inputs[posNota].value =
                                registro.nota ?? "";
                        }

                        if (inputs[posCh]) {
                            inputs[posCh].value =
                                registro
                                    .carga_horaria_horas_aula ??
                                "";
                        }

                        totalComponente +=
                            Number(
                                registro
                                    .carga_horaria_horas_aula ||
                                0
                            );
                    });

                const campoTotal =
                    linha.querySelector(
                        ".ch-total-linha"
                    );

                if (campoTotal) {
                    campoTotal.value =
                        totalComponente || "";
                }
            });

        preencherResumoBase();
    }

    function preencherResumoBase() {
        const tabela =
            document.getElementById(
                "tabelaFormacaoGeral"
            );

        if (!tabela) {
            return;
        }

        const linhasRodape =
            tabela.querySelectorAll("tfoot tr");

        if (linhasRodape.length >= 1) {
            const campos =
                linhasRodape[0]
                    .querySelectorAll("input");

            resumoBase
                .slice(0, 3)
                .forEach(function (item, indice) {
                    setValor(
                        campos[indice],
                        item.carga_horaria_total
                    );
                });

            setValor(
                campos[3],
                totaisBase.carga_horaria_total
            );
        }

        if (linhasRodape.length >= 2) {
            const campos =
                linhasRodape[1]
                    .querySelectorAll("input");

            resumoBase
                .slice(0, 3)
                .forEach(function (item, indice) {
                    setValor(
                        campos[indice],
                        item.carga_horaria_relogio
                    );
                });

            setValor(
                campos[3],
                totaisBase.carga_horaria_relogio
            );
        }

        if (linhasRodape.length >= 3) {
            const campos =
                linhasRodape[2]
                    .querySelectorAll("input");

            resumoBase
                .slice(0, 3)
                .forEach(function (item, indice) {
                    setValor(
                        campos[indice],
                        item.frequencia_percentual
                    );
                });
        }

        const resultados =
            document.querySelectorAll(
                ".resultados-anos .resultado-ano"
            );

        resumoBase
            .slice(0, 3)
            .forEach(function (item, indice) {
                const bloco = resultados[indice];

                if (!bloco) {
                    return;
                }

                const campos =
                    bloco.querySelectorAll(
                        "input, select"
                    );

                const cidadeEstado =
                    String(
                        item.cidade_estado || ""
                    ).split("/");

                setValor(
                    campos[0],
                    item.estabelecimento
                );

                setValor(
                    campos[1],
                    cidadeEstado[0]
                        ? cidadeEstado[0].trim()
                        : ""
                );

                setValor(
                    campos[2],
                    cidadeEstado[1]
                        ? cidadeEstado[1].trim()
                        : ""
                );

                setValor(
                    campos[3],
                    item.resultado
                );
            });
    }

    function criarLinhaItinerario(item) {
        const tr = document.createElement("tr");

        const valores = [
            item.tipo,
            item.nome,
            item.ano,
            item.periodo_letivo,
            item.carga_horaria ??
            item.carga_horaria_horas_aula,
            item.nota,
            item.frequencia,
            item.resultado_final
        ];

        valores.forEach(
            function (valor, indice) {
                const td =
                    document.createElement("td");

                const input =
                    document.createElement("input");

                if (
                    indice === 4 ||
                    indice === 5 ||
                    indice === 6
                ) {
                    input.type = "number";

                    if (indice === 5) {
                        input.step = "0.1";
                    }

                    if (indice === 6) {
                        input.step = "0.01";
                    }
                } else {
                    input.type = "text";
                }

                if (indice === 4) {
                    input.className =
                        "ch-itinerario";
                }

                if (
                    valor !== null &&
                    valor !== undefined
                ) {
                    input.value = valor;
                }

                td.appendChild(input);
                tr.appendChild(td);
            }
        );

        return tr;
    }

    function preencherCabecalhoBloco(
        bloco,
        meta
    ) {
        if (!bloco) {
            return;
        }

        const campos =
            bloco.querySelectorAll(
                ".dados-itinerario input"
            );

        setValor(
            campos[0],
            meta.estabelecimento ||
            escola.nome
        );

        setValor(
            campos[1],
            escola.cadastro_escolar
        );

        setValor(
            campos[2],
            meta.cidade ||
            escola.cidade
        );

        setValor(
            campos[3],
            meta.estado ||
            escola.estado
        );

        setValor(
            campos[4],
            meta.itinerarios
        );

        setValor(
            campos[5],
            meta.trilhas
        );
    }

    function preencherItinerario() {
        const itinerario =
            Array.isArray(extras.itinerario)
                ? extras.itinerario
                : (
                    Array.isArray(dados.itinerario)
                        ? dados.itinerario
                        : []
                );

        if (!itinerario.length) {
            return;
        }

        const grupos = {};

        itinerario.forEach(function (item) {
            const chave =
                String(
                    item.periodo_letivo || ""
                ).trim();

            if (!grupos[chave]) {
                grupos[chave] = [];
            }

            grupos[chave].push(item);
        });

        const blocos = Array.from(
            document.querySelectorAll(
                ".bloco-itinerario"
            )
        );

        const atribuicoes = [
            ["2024.1", blocos[0]],
            ["2024.2", blocos[1]],
            [null, blocos[2]],
            ["2025", blocos[3]]
        ];

        atribuicoes.forEach(
            function (atribuicao) {
                const periodo = atribuicao[0];
                const bloco = atribuicao[1];

                if (!bloco) {
                    return;
                }

                if (!periodo) {
                    bloco.style.display = "none";
                    return;
                }

                const itens =
                    grupos[periodo] || [];

                if (!itens.length) {
                    bloco.style.display = "none";
                    return;
                }

                bloco.style.display = "";

                preencherCabecalhoBloco(
                    bloco,
                    metaItinerario["2024"] || {}
                );

                const tbody =
                    bloco.querySelector(
                        ".tabela-itinerario tbody"
                    );

                if (!tbody) {
                    return;
                }

                tbody.innerHTML = "";

                itens.forEach(function (item) {
                    tbody.appendChild(
                        criarLinhaItinerario(item)
                    );
                });
            }
        );

        const tabelaAntiga =
            document.querySelector(
                ".tabela-historico-modelo"
            );

        if (tabelaAntiga) {
            tabelaAntiga.style.display = "none";
        }

        const topoHistorico =
            document.querySelector(
                ".topo-historico"
            );

        if (topoHistorico) {
            const campos =
                topoHistorico.querySelectorAll(
                    ".campo-topo"
                );

            const meta =
                metaItinerario["2024"] || {};

            function substituirTexto(
                elemento,
                rotulo,
                valor
            ) {
                if (!elemento || !valor) {
                    return;
                }

                elemento.innerHTML =
                    "<strong>" +
                    rotulo +
                    ":</strong> " +
                    valor;
            }

            substituirTexto(
                campos[0],
                "Estabelecimento de Ensino",
                meta.estabelecimento ||
                escola.nome
            );

            substituirTexto(
                campos[2],
                "Cidade",
                meta.cidade ||
                escola.cidade
            );

            substituirTexto(
                campos[3],
                "Estado",
                meta.estado ||
                escola.estado
            );

            substituirTexto(
                campos[4],
                "Itinerário",
                meta.itinerarios
            );
        }

        const observacoes =
            metaItinerario["2024"]
                ? metaItinerario["2024"].observacoes
                : null;

        setValor(
            document.getElementById(
                "observacoesItinerario"
            ),
            observacoes
        );
    }

    function preencherResultadoFinal() {
        setValor(
            document.getElementById(
                "resultadoCargaFormacao"
            ),
            resultadoCurso
                .carga_horaria_formacao_geral_relogio
        );

        setValor(
            document.getElementById(
                "resultadoCargaItinerarios"
            ),
            resultadoCurso
                .carga_horaria_itinerarios_relogio
        );

        setValor(
            document.getElementById(
                "resultadoCargaTotal"
            ),
            resultadoCurso
                .carga_horaria_total_relogio
        );

        const dataConclusao =
            document.getElementById(
                "dataConclusao"
            );

        if (
            dataConclusao &&
            resultadoCurso.data_conclusao
        ) {
            dataConclusao.value =
                dataParaInput(
                    resultadoCurso.data_conclusao
                );
        }

        setValor(
            document.getElementById(
                "resultadoFinal"
            ),
            resultadoCurso.resultado_final
        );

        const dataEmissao =
            document.getElementById(
                "dataEmissao"
            );

        if (
            dataEmissao &&
            resultadoCurso.data_emissao
        ) {
            dataEmissao.value =
                dataParaInput(
                    resultadoCurso.data_emissao
                );
        }

        setValor(
            document.querySelector(
                ".campo-local"
            ),
            resultadoCurso.cidade_emissao
        );

        setValor(
            document.querySelector(
                ".campo-estado"
            ),
            resultadoCurso.uf_emissao
        );
    }

    preencherAluno();
    preencherEscola();
    preencherComplementares();
    preencherBaseComum();
    preencherItinerario();
    preencherResultadoFinal();
})();