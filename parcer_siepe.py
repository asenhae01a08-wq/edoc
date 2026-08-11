import re
import unicodedata
from datetime import datetime


def _limpar(valor):
    if valor is None:
        return None
    valor = re.sub(r"\s+", " ", str(valor)).strip()
    return valor or None


def _normalizar(valor):
    valor = _limpar(valor) or ""
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(c for c in valor if not unicodedata.combining(c))
    return valor.upper()


def _procurar(texto, padroes, flags=re.IGNORECASE | re.DOTALL):
    for padrao in padroes:
        resultado = re.search(padrao, texto, flags)
        if resultado:
            return _limpar(resultado.group(1))
    return None


def _decimal(valor):
    valor = _limpar(valor)
    if not valor:
        return None

    valor = valor.replace("%", "").replace(" ", "").replace(",", ".")
    resultado = re.search(r"-?\d+(?:\.\d+)?", valor)
    return float(resultado.group(0)) if resultado else None


def _inteiro(valor):
    numero = _decimal(valor)
    return int(numero) if numero is not None else None


def _data_mysql(valor):
    valor = _limpar(valor)
    if not valor:
        return None

    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, formato).date()
        except ValueError:
            pass
    return None


def _extrair_anos(texto):
    anos = []

    padroes = [
        r"1[ºo°]\s*ANO.{0,80}?Ano\s*:?\s*(20\d{2})",
        r"2[ºo°]\s*ANO.{0,80}?Ano\s*:?\s*(20\d{2})",
        r"3[ºo°]\s*ANO.{0,80}?Ano\s*:?\s*(20\d{2})",
    ]

    for padrao in padroes:
        resultado = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
        anos.append(int(resultado.group(1)) if resultado else None)

    if not any(anos):
        encontrados = []
        for ano in re.findall(r"\b20\d{2}\b", texto):
            ano_int = int(ano)
            if ano_int not in encontrados:
                encontrados.append(ano_int)
        for indice in range(min(3, len(encontrados))):
            anos[indice] = encontrados[indice]

    return anos


def _extrair_aluno(texto):
    texto_unico = re.sub(r"\s+", " ", texto)

    filiacao = re.search(
        r"Filho\(a\)\s+de\s+(.+?)\s+e\s+(.+?)\.\s*Nascido",
        texto_unico,
        re.IGNORECASE,
    )

    nome_mae = None
    nome_pai = None
    if filiacao:
        nome_mae = _limpar(filiacao.group(1))
        nome_pai = _limpar(filiacao.group(2))

    nome = _procurar(
        texto,
        [
            r"\bNome\s*:\s*([^\n]{3,120})",
            r"certificamos\s+que\s+(.+?)\s+Filho\(a\)\s+de",
            r"Estudante\s*:\s*([^\n]{3,120})",
        ],
    )

    matricula = _procurar(
        texto,
        [
            r"Matr[ií]cula\s*:\s*([A-Za-z0-9.\-]{5,30})",
            r"Matr[ií]cula\s+n?[ºo°]?\s*:?\s*([A-Za-z0-9.\-]{5,30})",
        ],
    )

    cpf = _procurar(
        texto,
        [r"CPF\s*:\s*(\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2})"],
    )

    rg = _procurar(
        texto,
        [r"RG\s*:\s*([A-Za-z0-9.\-/]+)"],
    )

    orgao = _procurar(
        texto,
        [
            r"[ÓO]rg[aã]o\s+Expedidor\s*:\s*([^\s,;]+)",
            r"RG\s*:\s*[A-Za-z0-9.\-/]+\s+[ÓO]rg[aã]o\s+Expedidor\s*:\s*([^\s,;]+)",
        ],
    )

    data_nascimento_texto = _procurar(
        texto,
        [
            r"Data\s+de\s+Nascimento\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Nascido\(a\)\s+em\s*(\d{2}/\d{2}/\d{4})",
            r"Nascimento\s*:?\s*(\d{2}/\d{2}/\d{4})",
        ],
    )

    if not nome_mae:
        nome_mae = _procurar(
            texto,
            [
                r"Filia[cç][aã]o\s*\(M[aã]e\)\s*:?\s*([^\n]+)",
                r"Nome\s+da\s+M[aã]e\s*:?\s*([^\n]+)",
                r"M[aã]e\s*:?\s*([^\n]+)",
            ],
        )

    if not nome_pai:
        nome_pai = _procurar(
            texto,
            [
                r"Filia[cç][aã]o\s*\(Pai\)\s*:?\s*([^\n]+)",
                r"Nome\s+do\s+Pai\s*:?\s*([^\n]+)",
                r"Pai\s*:?\s*([^\n]+)",
            ],
        )

    nacionalidade = _procurar(
        texto,
        [r"Nacionalidade\s*:?\s*([^\n.,;]+)"],
    )

    naturalidade = _procurar(
        texto,
        [r"Naturalidade\s*:?\s*([^\n/]+)"],
    )

    turma = _procurar(
        texto,
        [r"Turma\s*:?\s*([^\n]{2,30})"],
    )

    curso = _procurar(
        texto,
        [
            r"Curso\s*:?\s*([^\n]{3,120})",
            r"(T[eé]cnico\s+em\s+Desenvolvimento\s+de\s+Sistemas)",
            r"(T[eé]cnico\s+em\s+Marketing)",
        ],
    )

    serie = _procurar(
        texto,
        [
            r"S[eé]rie\s*:?\s*([^\n]{2,30})",
            r"Concluiu\s+o\(a\)\s+([^\n]{2,40})\s+do\s+ENSINO",
        ],
    )

    email = _procurar(
        texto,
        [r"E-?mail\s*:?\s*([\w.+'-]+@[\w.-]+\.[A-Za-z]{2,})"],
    )

    endereco = _procurar(
        texto,
        [r"Endere[cç]o\s*:?\s*([^\n]{5,255})"],
    )

    return {
        "nome": nome,
        "matricula": matricula,
        "data_nascimento": _data_mysql(data_nascimento_texto),
        "cpf": cpf,
        "rg": rg,
        "orgao_expedidor": orgao,
        "nacionalidade": nacionalidade,
        "nome_pai": nome_pai,
        "nome_mae": nome_mae,
        "endereco": endereco,
        "serie": serie,
        "email": email,
        "id_turma": turma,
        "curso": curso,
        "naturalidade": naturalidade,
    }


def _extrair_historico(texto, matricula):
    resultado_final = _procurar(
        texto,
        [
            r"Resultado\s+Final\s*:\s*(APROVADO(?:\(A\))?|REPROVADO(?:\(A\))?|CONCLU[IÍ]DO(?:\(A\))?|CURSANDO|PROGRESS[AÃ]O\s+PLENA)",
            r"Resultado\s+Final\s*:\s*([^\n]{2,30})",
        ],
    )

    if resultado_final:
        resultado_final = resultado_final.strip()[:30]

    data_conclusao_texto = _procurar(
        texto,
        [
            r"Data\s+de\s+Conclus[aã]o\s*:\s*(\d{2}/\d{2}/\d{4})",
            r"Conclus[aã]o\s*:\s*(\d{2}/\d{2}/\d{4})",
        ],
    )

    return {
        "id_historico_escolar": f"EDOC-{matricula}" if matricula else None,
        "resultado_final": resultado_final,
        "data_conclusao": _data_mysql(data_conclusao_texto),
    }


def _extrair_base_comum(tabelas, anos):
    registros = []

    palavras_ignorar = {
        "COMPONENTES CURRICULARES",
        "CARGA HORARIA TOTAL",
        "CARGA HORARIA EM HORAS/RELOGIO",
        "PERCENTUAL DE FREQUENCIA DO(A) ESTUDANTE",
    }

    for tabela_info in tabelas:
        linhas = tabela_info.get("linhas") or []
        texto_tabela = _normalizar(" ".join(str(c or "") for l in linhas for c in l))

        if "COMPONENTES CURRICULARES" not in texto_tabela:
            continue

        for linha in linhas:
            if not linha:
                continue

            celulas = [_limpar(c) for c in linha]
            if len(celulas) < 7:
                continue

            nome = celulas[0]
            nome_norm = _normalizar(nome)

            if not nome or any(p in nome_norm for p in palavras_ignorar):
                continue

            # Esperado no modelo: componente | nota/ch 1º | nota/ch 2º | nota/ch 3º | total
            valores = celulas + [None] * (8 - len(celulas))
            pares = [
                (anos[0] if len(anos) > 0 else None, valores[1], valores[2]),
                (anos[1] if len(anos) > 1 else None, valores[3], valores[4]),
                (anos[2] if len(anos) > 2 else None, valores[5], valores[6]),
            ]

            for ano, nota_txt, ch_txt in pares:
                nota = _decimal(nota_txt)
                ch = _inteiro(ch_txt)

                if nota is None and ch is None:
                    continue

                registros.append(
                    {
                        "nome": nome,
                        "nota": nota,
                        "ano_letivo": ano,
                        "resultado": None,
                        "frequencia_percentual": None,
                        "carga_horaria_horas_aula": ch,
                        "carga_horaria_relogio": None,
                        "carga_horaria_total_anual": ch,
                    }
                )

    return registros


def _extrair_itinerario(tabelas):
    registros = []

    for tabela_info in tabelas:
        linhas = tabela_info.get("linhas") or []
        texto_tabela = _normalizar(" ".join(str(c or "") for l in linhas for c in l))

        if "UNIDADES CURRICULARES" not in texto_tabela:
            continue
        if "PERIODO LETIVO" not in texto_tabela:
            continue
        if "RESULTADO" not in texto_tabela:
            continue

        for linha in linhas:
            if not linha:
                continue

            celulas = [_limpar(c) for c in linha]
            if len(celulas) < 8:
                continue

            tipo, nome, ano, periodo, ch, nota, frequencia, resultado = celulas[:8]

            nome_norm = _normalizar(nome)
            if not nome or "UNIDADES CURRICULARES" in nome_norm:
                continue

            if _normalizar(tipo) in {"TIPO", ""} and nome_norm in {"UNIDADES CURRICULARES", ""}:
                continue

            if not any([_decimal(nota), _inteiro(ch), _decimal(frequencia), resultado]):
                continue

            registros.append(
                {
                    "nome": nome,
                    "abreviacao": None,
                    "tipo": tipo,
                    "nota": _decimal(nota),
                    "resultado_final": resultado,
                    "periodo_letivo": periodo or ano,
                    "frequencia": _decimal(frequencia),
                    "carga_horaria": _inteiro(ch),
                    "carga_horaria_horas_aula": _inteiro(ch),
                    "carga_horaria_relogio": None,
                }
            )

    return registros


def extrair_dados_siepe(texto, tabelas=None):
    tabelas = tabelas or []

    aluno = _extrair_aluno(texto)
    anos = _extrair_anos(texto)

    return {
        "aluno": aluno,
        "historico": _extrair_historico(texto, aluno.get("matricula")),
        "base_comum": _extrair_base_comum(tabelas, anos),
        "itinerario": _extrair_itinerario(tabelas),
    }
