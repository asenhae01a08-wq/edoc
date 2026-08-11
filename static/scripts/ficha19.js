(function () {
    const dados = window.dadosFichaEdoc;

    function setValor(elemento, valor) {
        if (!elemento || valor === null || valor === undefined || valor === "") {
            return;
        }

        if (["INPUT", "TEXTAREA", "SELECT"].includes(elemento.tagName)) {
            if (elemento.tagName === "SELECT") {
                const alvo = String(valor).trim().toLowerCase();
                const opcao = Array.from(elemento.options).find(function (item) {
                    return item.value.trim().toLowerCase() === alvo ||
                        item.textContent.trim().toLowerCase() === alvo;
                });
                if (opcao) {
                    elemento.value = opcao.value;
                }
            } else {
                elemento.value = valor;
            }
        } else {
            elemento.textContent = valor;
        }
    }

    function preencherTodos(seletor, valor) {
        document.querySelectorAll(seletor).forEach(function (elemento) {
            setValor(elemento, valor);
        });
    }

    function normalizar(texto) {
        return String(texto || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim()
            .toUpperCase();
    }

    function preencherDadosPessoais(aluno) {
        if (!aluno) {
            return;
        }

        setValor(document.getElementById("nomeAluno"), aluno.nome);
        setValor(document.getElementById("nomeMae"), aluno.nome_mae);
        setValor(document.getElementById("nomePai"), aluno.nome_pai);
        setValor(document.getElementById("dataNascimento"), aluno.data_nascimento);
        setValor(document.getElementById("nacionalidade"), aluno.nacionalidade);
        setValor(document.getElementById("rg"), aluno.rg);
        setValor(document.getElementById("orgaoExpedidor"), aluno.orgao_expedidor);
        setValor(document.getElementById("cpf"), aluno.cpf);

        preencherTodos(".sincronizar-nome", aluno.nome);
        preencherTodos(".sincronizar-matricula", aluno.matricula);

        const cidadeNascimento = document.getElementById("cidadeNascimento");
        const ufNascimento = document.getElementById("ufNascimento");

        if (aluno.naturalidade) {
            const partes = String(aluno.naturalidade).split(/[\/-]/);
            if (partes.length > 1) {
                setValor(cidadeNascimento, partes[0].trim());
                setValor(ufNascimento, partes[partes.length - 1].trim());
            } else {
                setValor(cidadeNascimento, aluno.naturalidade);
            }
        }
    }

    function preencherBaseComum(baseComum) {
        if (!Array.isArray(baseComum) || baseComum.length === 0) {
            return;
        }

        const anos = Array.from(
            new Set(
                baseComum
                    .map(function (item) { return item.ano_letivo; })
                    .filter(Boolean)
            )
        ).sort();

        if (anos[0]) setValor(document.getElementById("anoPrimeiro"), anos[0]);
        if (anos[1]) setValor(document.getElementById("anoSegundo"), anos[1]);
        if (anos[2]) setValor(document.getElementById("anoTerceiro"), anos[2]);

        const porComponente = {};

        baseComum.forEach(function (item) {
            const chave = normalizar(item.nome);
            if (!porComponente[chave]) {
                porComponente[chave] = {};
            }
            porComponente[chave][String(item.ano_letivo || "")] = item;
        });

        document.querySelectorAll("#tabelaFormacaoGeral tbody tr").forEach(function (linha) {
            const componenteElemento = linha.querySelector(".componente");
            if (!componenteElemento) {
                return;
            }

            const nomeComponente = componenteElemento.tagName === "INPUT"
                ? componenteElemento.value || componenteElemento.placeholder
                : componenteElemento.textContent;

            const registros = porComponente[normalizar(nomeComponente)];
            if (!registros) {
                return;
            }

            const inputs = Array.from(linha.querySelectorAll("input"));
            const deslocamento = componenteElemento.tagName === "INPUT" ? 1 : 0;

            anos.slice(0, 3).forEach(function (ano, indice) {
                const registro = registros[String(ano)];
                if (!registro) {
                    return;
                }

                const posNota = deslocamento + indice * 2;
                const posCh = posNota + 1;

                if (inputs[posNota]) {
                    inputs[posNota].value = registro.nota ?? "";
                }
                if (inputs[posCh]) {
                    inputs[posCh].value = registro.carga_horaria_horas_aula ?? "";
                }
            });
        });

        if (typeof calcularCargas === "function") {
            calcularCargas();
        }
    }

    function preencherItinerario(itinerario) {
        if (!Array.isArray(itinerario) || itinerario.length === 0) {
            return;
        }

        const linhas = Array.from(
            document.querySelectorAll(".tabela-itinerario tbody tr")
        );

        itinerario.forEach(function (item, indice) {
            const linha = linhas[indice];
            if (!linha) {
                return;
            }

            const campos = Array.from(linha.querySelectorAll("input, select"));
            if (campos.length < 8) {
                return;
            }

            setValor(campos[0], item.tipo);
            setValor(campos[1], item.nome);
            setValor(campos[2], item.ano || "");
            setValor(campos[3], item.periodo_letivo);
            setValor(campos[4], item.carga_horaria || item.carga_horaria_horas_aula);
            setValor(campos[5], item.nota);
            setValor(campos[6], item.frequencia);
            setValor(campos[7], item.resultado_final);
        });

        if (typeof calcularCargas === "function") {
            calcularCargas();
        }
    }

    if (dados) {
        preencherDadosPessoais(dados.aluno);
        preencherBaseComum(dados.base_comum);
        preencherItinerario(dados.itinerario);
    }
})();
