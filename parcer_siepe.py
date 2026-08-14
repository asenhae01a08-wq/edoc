
import re
import unicodedata
from datetime import datetime, date


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


def _decimal(valor):
    valor = _limpar(valor)
    if not valor or valor == "-":
        return None
    valor = valor.replace("%", "").replace(" ", "").replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", valor)
    return float(m.group(0)) if m else None


def _inteiro(valor):
    n = _decimal(valor)
    return int(n) if n is not None else None


def _data_br(valor):
    valor = _limpar(valor)
    if not valor or valor == "-":
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, fmt).date()
        except ValueError:
            pass
    return None


MESES_PT = {
    "JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "MARÇO": 3, "ABRIL": 4,
    "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9,
    "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12,
}


def _data_extenso_pt(texto):
    texto = _limpar(texto)
    if not texto:
        return None
    m = re.search(r"(\d{1,2})\s+de\s+([A-Za-zÀ-ÿ]+)\s+de\s+(\d{4})", texto, re.I)
    if not m:
        return None
    mes = MESES_PT.get(_normalizar(m.group(2)))
    if not mes:
        return None
    try:
        return date(int(m.group(3)), mes, int(m.group(1)))
    except ValueError:
        return None


def _words(pagina):
    return pagina.get("palavras") or []


def _texto_area(palavras, x0=None, x1=None, y0=None, y1=None):
    itens = []
    for w in palavras:
        if x0 is not None and w["x0"] < x0:
            continue
        if x1 is not None and w["x0"] >= x1:
            continue
        if y0 is not None and w["y0"] < y0:
            continue
        if y1 is not None and w["y0"] >= y1:
            continue
        itens.append(w)
    itens.sort(key=lambda w: (w["y0"], w["x0"]))
    return _limpar(" ".join(w["texto"] for w in itens))


def _achar_rotulo(palavras, rotulo, x1=200):
    alvo = _normalizar(rotulo)
    # agrupa por linhas aproximadas
    ys = sorted({round(w["y0"], 1) for w in palavras if w["x0"] < x1})
    for y in ys:
        linha = [w for w in palavras if w["x0"] < x1 and abs(w["y0"] - y) <= 1.2]
        linha.sort(key=lambda w: w["x0"])
        txt = _normalizar(" ".join(w["texto"] for w in linha))
        if alvo in txt:
            return sum(w["y0"] for w in linha) / len(linha)
    return None


def _valor_rotulo(palavras, rotulo, x_valor=190, tolerancia_y=4):
    y = _achar_rotulo(palavras, rotulo, x1=x_valor)
    if y is None:
        return None
    vals = [
        w for w in palavras
        if w["x0"] >= x_valor and abs(w["y0"] - y) <= tolerancia_y
    ]
    vals.sort(key=lambda w: w["x0"])
    return _limpar(" ".join(w["texto"] for w in vals))


def _extrair_pagina1(pagina):
    palavras = _words(pagina)
    texto = pagina.get("texto", "")

    escola = _valor_rotulo(palavras, "Escola")
    nome = _valor_rotulo(palavras, "Nome do estudante")
    nome_mae = _valor_rotulo(palavras, "Filiação - mãe")
    nome_pai = _valor_rotulo(palavras, "Filiação - pai")
    data_nascimento = _valor_rotulo(palavras, "Data de nascimento")
    cidade_nascimento = _valor_rotulo(palavras, "Cidade de nascimento")
    uf_nascimento = _valor_rotulo(palavras, "UF")
    nacionalidade = _valor_rotulo(palavras, "Nacionalidade")
    rg = _valor_rotulo(palavras, "RG")
    orgao = _valor_rotulo(palavras, "Órgão expedidor")
    cpf = _valor_rotulo(palavras, "CPF")
    matricula = _valor_rotulo(palavras, "Matrícula")
    etapa = _valor_rotulo(palavras, "Etapa concluída")
    curso_documento = _valor_rotulo(palavras, "Curso")
    autorizacao_completa = _valor_rotulo(palavras, "Autorização de Funcionamento")

    y_end = _achar_rotulo(palavras, "Endereço")
    endereco_escola = None
    if y_end is not None:
        endereco_escola = _texto_area(
            palavras, x0=190, y0=y_end - 10, y1=y_end + 16
        )

    autorizacao = None
    data_doe = None
    if autorizacao_completa:
        m = re.search(
            r"(.+?)\s+D\.?O\.?E/?PE\s+de\s+(\d{2}/\d{2}/\d{4})",
            autorizacao_completa, re.I
        )
        if m:
            autorizacao = _limpar(m.group(1))
            data_doe = m.group(2)
        else:
            autorizacao = autorizacao_completa

    secretario_raw = _valor_rotulo(palavras, "Secretário")
    diretor_raw = _valor_rotulo(palavras, "Diretor")

    def resp(valor):
        if not valor:
            return {"nome": None, "matricula": None}
        m = re.search(r"(.+?),?\s+mat\.?\s*n[ºo°]?\s*(\d+)", valor, re.I)
        if m:
            return {"nome": _limpar(m.group(1).rstrip(",")), "matricula": m.group(2)}
        return {"nome": valor, "matricula": None}

    secretario = resp(secretario_raw)
    diretor = resp(diretor_raw)

    item1 = _texto_area(palavras, x0=190, y0=398, y1=455)
    item2 = _texto_area(palavras, x0=190, y0=458, y1=495)
    item3 = _texto_area(palavras, x0=190, y0=500, y1=523)

    sit_ed_fisica = None
    n = _normalizar(item3)
    if "NAO DISPENSADO" in n:
        sit_ed_fisica = "não dispensado(a)"
    elif "DISPENSADO" in n:
        sit_ed_fisica = "dispensado(a)"

    ensino_religioso = None
    if "OPTOU POR NAO VIVENCIAR" in _normalizar(item2):
        ensino_religioso = "não vivenciado"

    aluno = {
        "nome": nome,
        "matricula": matricula,
        "data_nascimento": _data_br(data_nascimento),
        "cpf": cpf,
        "rg": rg,
        "orgao_expedidor": orgao,
        "nacionalidade": nacionalidade,
        "nome_pai": nome_pai,
        "nome_mae": nome_mae,
        "serie": etapa,
        "curso": curso_documento,
        "cidade_nascimento": cidade_nascimento,
        "uf_nascimento": uf_nascimento,
        "id_turma": None,
        "email": None,
        "endereco": None,  # o endereço do PDF é da escola, não do aluno
    }

    escola_info = {
        "nome": escola,
        "endereco": endereco_escola,
        "autorizacao_funcionamento": autorizacao,
        "data_doe": data_doe,
        "telefone": None,
        "cadastro_escolar": None,
        "cidade": "CARUARU" if endereco_escola and "CARUARU" in _normalizar(endereco_escola) else None,
        "estado": "PE" if endereco_escola and re.search(r"\bPE\b", endereco_escola) else None,
        "secretario_nome": secretario["nome"],
        "secretario_matricula": secretario["matricula"],
        "diretor_nome": diretor["nome"],
        "diretor_matricula": diretor["matricula"],
    }

    complementares = {
        "item_1": item1,
        "item_2": item2,
        "item_3": item3,
        "ensino_religioso": ensino_religioso,
        "situacao_educacao_fisica": sit_ed_fisica,
    }
    return aluno, escola_info, complementares


def _tokens_faixa(linha, x0, x1):
    vals = [w for w in linha if w["x0"] >= x0 and w["x0"] < x1]
    vals.sort(key=lambda w: w["x0"])
    return [w["texto"] for w in vals]


def _linhas_por_y(palavras, y0=None, y1=None, tolerancia=1.3):
    selecionadas = [w for w in palavras if (y0 is None or w["y0"] >= y0) and (y1 is None or w["y0"] < y1)]
    ys = []
    for w in sorted(selecionadas, key=lambda w: w["y0"]):
        if not ys or abs(w["y0"] - ys[-1]) > tolerancia:
            ys.append(w["y0"])
    linhas = []
    for y in ys:
        linha = [w for w in selecionadas if abs(w["y0"] - y) <= tolerancia]
        linha.sort(key=lambda w: w["x0"])
        linhas.append((y, linha))
    return linhas


def _extrair_pagina2(pagina):
    palavras = _words(pagina)

    # Indicadores anuais
    indicadores = [
        {"serie": "1º Ano", "ano_letivo": None, "carga_horaria_total": None,
         "carga_horaria_relogio": None, "frequencia_percentual": None},
        {"serie": "2º Ano", "ano_letivo": None, "carga_horaria_total": None,
         "carga_horaria_relogio": None, "frequencia_percentual": None},
        {"serie": "3º Ano", "ano_letivo": None, "carga_horaria_total": None,
         "carga_horaria_relogio": None, "frequencia_percentual": None},
    ]

    linhas = _linhas_por_y(palavras, 370, 440)
    for y, linha in linhas:
        txt = _normalizar(" ".join(w["texto"] for w in linha))
        if "CARGA HORARIA TOTAL" in txt:
            vals = [
                _texto_area(linha, x0=200, x1=340),
                _texto_area(linha, x0=340, x1=470),
                _texto_area(linha, x0=470, x1=600),
            ]
            for i, v in enumerate(vals):
                indicadores[i]["carga_horaria_total"] = _inteiro(v)
        elif "CARGA HORARIA EM HORAS/RELOGIO" in txt:
            vals = [
                _texto_area(linha, x0=200, x1=340),
                _texto_area(linha, x0=340, x1=470),
                _texto_area(linha, x0=470, x1=600),
            ]
            for i, v in enumerate(vals):
                indicadores[i]["carga_horaria_relogio"] = None if v == "-" else v

    # Frequência está em uma linha separada
    for y, linha in _linhas_por_y(palavras, 415, 432):
        if any("%" in w["texto"] for w in linha):
            vals = [
                _texto_area(linha, x0=200, x1=340),
                _texto_area(linha, x0=340, x1=470),
                _texto_area(linha, x0=470, x1=600),
            ]
            for i, v in enumerate(vals):
                indicadores[i]["frequencia_percentual"] = _decimal(v)

    # Resultado/estabelecimento por ano
    anchors = []
    for y, linha in _linhas_por_y(palavras, 480, 665):
        left = _texto_area(linha, x0=40, x1=180)
        if not left:
            continue

        m_com_ano = re.match(r"(20\d{2})\s*-\s*([123][ºo°]\s*Ano)", left, re.I)
        if m_com_ano:
            anchors.append((y, int(m_com_ano.group(1)), m_com_ano.group(2)))
            continue

        m_sem_ano = re.match(r"([123][ºo°]\s*Ano)", left, re.I)
        if m_sem_ano:
            anchors.append((y, None, m_sem_ano.group(1)))

    for idx, (y, ano, serie) in enumerate(anchors[:3]):
        # No PDF oficial o nome da escola ocupa várias linhas acima e abaixo
        # da linha que contém "2024 - 1º Ano" / "2025 - 2º Ano".
        # Uma janela fixa ao redor do ano preserva o nome completo sem
        # misturar o registro seguinte.
        if ano is not None:
            start = y - 40
            end = y + 42
        else:
            start = y - 8
            end = y + 12

        faixa = [w for w in palavras if start <= w["y0"] < end]
        estabelecimento = _texto_area(faixa, x0=190, x1=280)
        cidade_estado = _texto_area(faixa, x0=280, x1=340)
        resultado = _texto_area(faixa, x0=340, x1=500)

        def limpar_traco_final(valor):
            if not valor:
                return valor
            valor = re.sub(r"\s+-\s*$", "", valor).strip()
            return None if valor == "-" else valor

        indicadores[idx].update({
            "ano_letivo": ano,
            "serie": serie,
            "estabelecimento": limpar_traco_final(estabelecimento),
            "cidade_estado": limpar_traco_final(cidade_estado),
            "resultado": limpar_traco_final(resultado),
        })

    # Disciplinas
    disciplinas_linhas = []
    for y, linha in _linhas_por_y(palavras, 170, 355):
        nome = _texto_area(linha, x0=40, x1=200)
        if not nome or "COMPONENTE CURRICULAR" in _normalizar(nome):
            continue
        if not any(re.search(r"\d|^-?$", w["texto"]) for w in linha if w["x0"] >= 200):
            continue

        campos = {
            "nome": nome,
            "1_nota": _texto_area(linha, x0=200, x1=300),
            "1_ch": _texto_area(linha, x0=300, x1=370),
            "2_nota": _texto_area(linha, x0=370, x1=440),
            "2_ch": _texto_area(linha, x0=440, x1=475),
            "3_nota": _texto_area(linha, x0=475, x1=540),
            "3_ch": _texto_area(linha, x0=540, x1=620),
            "ch_total": _texto_area(linha, x0=620, x1=700),
        }
        disciplinas_linhas.append(campos)

    base_comum = []
    for d in disciplinas_linhas:
        for i in range(3):
            nota = _decimal(d[f"{i+1}_nota"])
            ch = _inteiro(d[f"{i+1}_ch"])
            if nota is None and ch is None:
                continue
            resumo = indicadores[i]
            base_comum.append({
                "nome": d["nome"],
                "nota": nota,
                "ano_letivo": resumo.get("ano_letivo"),
                "serie": resumo.get("serie"),
                "resultado": resumo.get("resultado"),
                "frequencia_percentual": resumo.get("frequencia_percentual"),
                "carga_horaria_horas_aula": ch,
                "carga_horaria_relogio": None,
                "carga_horaria_total_anual": resumo.get("carga_horaria_total"),
                "carga_horaria_total_componente": _inteiro(d["ch_total"]),
            })

    # totais gerais do quadro indicador
    totais = {}
    for y, linha in _linhas_por_y(palavras, 370, 435):
        txt = _normalizar(" ".join(w["texto"] for w in linha))
        if "CARGA HORARIA TOTAL" in txt:
            totais["carga_horaria_total"] = _inteiro(_texto_area(linha, x0=600, x1=700))
        elif "CARGA HORARIA EM HORAS/RELOGIO" in txt:
            totais["carga_horaria_relogio"] = _texto_area(linha, x0=600, x1=700)

    return base_comum, indicadores, totais


def _extrair_meta_direita_p3(palavras):
    # O quadro lateral da página 3 começa o valor de "Itinerários"
    # acima da própria palavra "Itinerários"; por isso usamos as
    # coordenadas oficiais do layout em vez de depender só de linhas.
    return {
        "estabelecimento": _texto_area(palavras, x0=960, y0=86, y1=101),
        "cidade": _texto_area(palavras, x0=960, y0=101, y1=116),
        "estado": _texto_area(palavras, x0=960, y0=116, y1=130),
        "itinerarios": _texto_area(palavras, x0=960, y0=130, y1=170),
        "trilhas": _texto_area(palavras, x0=960, y0=170, y1=212),
        "observacoes": _texto_area(palavras, x0=960, y0=212, y1=235),
    }


def _extrair_itinerario_pagina(pagina, numero):
    palavras = _words(pagina)
    if numero == 3:
        y_min, y_max = 175, 580
        x_tipo = (40, 180)
        x_unidade = (180, 410)
        x_ano = (410, 455)
        x_periodo = (455, 550)
        x_chnota = (550, 648)
        x_freq = (648, 715)
        x_result = (715, 830)
    else:
        y_min, y_max = 95, 330
        x_tipo = (40, 210)
        x_unidade = (210, 480)
        x_ano = (480, 525)
        x_periodo = (525, 620)
        x_ch = (620, 690)
        x_nota = (690, 725)
        x_freq = (725, 785)
        x_result = (785, 880)

    anchors = []
    for w in palavras:
        if y_min <= w["y0"] < y_max and x_ano[0] <= w["x0"] < x_ano[1]:
            if re.fullmatch(r"[123][ºo°]", w["texto"], re.I):
                anchors.append(w["y0"])
    # remove duplicados próximos
    ys = []
    for y in sorted(anchors):
        if not ys or abs(y - ys[-1]) > 2:
            ys.append(y)

    registros = []
    for i, y in enumerate(ys):
        start = y_min if i == 0 else (ys[i-1] + y) / 2
        end = y_max if i == len(ys)-1 else (y + ys[i+1]) / 2
        faixa = [w for w in palavras if start <= w["y0"] < end]

        tipo = _texto_area(faixa, x0=x_tipo[0], x1=x_tipo[1])
        nome = _texto_area(faixa, x0=x_unidade[0], x1=x_unidade[1])
        ano = _texto_area(faixa, x0=x_ano[0], x1=x_ano[1])
        periodo = _texto_area(faixa, x0=x_periodo[0], x1=x_periodo[1])

        if numero == 3:
            zona = [w for w in faixa if x_chnota[0] <= w["x0"] < x_chnota[1]]
            zona.sort(key=lambda w: w["x0"])
            tokens = [w["texto"] for w in zona]
            ch_txt = tokens[0] if tokens else None
            nota_txt = tokens[1] if len(tokens) > 1 else None
        else:
            ch_txt = _texto_area(faixa, x0=x_ch[0], x1=x_ch[1])
            nota_txt = _texto_area(faixa, x0=x_nota[0], x1=x_nota[1])

        frequencia_txt = _texto_area(faixa, x0=x_freq[0], x1=x_freq[1])
        resultado = _texto_area(faixa, x0=x_result[0], x1=x_result[1])

        if not nome or not periodo:
            continue
        registros.append({
            "nome": nome,
            "abreviacao": None,
            "tipo": tipo,
            "ano": ano,
            "nota": _decimal(nota_txt),
            "resultado_final": resultado,
            "periodo_letivo": periodo,
            "frequencia": _decimal(frequencia_txt),
            "carga_horaria": _inteiro(ch_txt),
            "carga_horaria_horas_aula": _inteiro(ch_txt),
            "carga_horaria_relogio": None,
        })
    return registros


def _extrair_resultado_curso(pagina):
    palavras = _words(pagina)

    def valor_proximo(rotulo, ytol=12):
        y = _achar_rotulo(palavras, rotulo, x1=210)
        if y is None:
            return None
        vals = [w for w in palavras if 210 <= w["x0"] < 500 and abs(w["y0"] - y) <= ytol]
        vals.sort(key=lambda w:(w["y0"],w["x0"]))
        txt = _limpar(" ".join(w["texto"] for w in vals))
        return None if txt == "-" else txt

    fgb = valor_proximo("Carga Horária da Formação Geral", 15)
    itiner = valor_proximo("Carga Horária dos Itinerários", 15)
    total = valor_proximo("Carga Horária TOTAL", 4)
    data_conclusao_txt = valor_proximo("Data da Conclusão do Curso", 4)
    resultado_final = valor_proximo("Resultado Final", 4)
    data_local = valor_proximo("Data/Local", 4)

    data_emissao = _data_extenso_pt(data_local)
    cidade = None
    uf = None
    if data_local:
        m = re.match(r"(.+?)\s*-\s*([A-Z]{2}),", data_local)
        if m:
            cidade = _limpar(m.group(1))
            uf = m.group(2)

    return {
        "carga_horaria_formacao_geral_relogio": fgb,
        "carga_horaria_itinerarios_relogio": itiner,
        "carga_horaria_total_relogio": total,
        "data_conclusao": _data_br(data_conclusao_txt),
        "resultado_final": resultado_final,
        "data_local": data_local,
        "cidade_emissao": cidade,
        "uf_emissao": uf,
        "data_emissao": data_emissao,
    }


def extrair_dados_siepe(texto, tabelas=None, paginas=None):
    paginas = paginas or []
    if len(paginas) < 4:
        raise ValueError(
            "O histórico oficial esperado possui 4 páginas. "
            "Não foi possível identificar todas as páginas do documento."
        )

    aluno, escola, complementares = _extrair_pagina1(paginas[0])
    base_comum, resumo_base, totais_base = _extrair_pagina2(paginas[1])
    itinerario_2024 = _extrair_itinerario_pagina(paginas[2], 3)
    itinerario_2025 = _extrair_itinerario_pagina(paginas[3], 4)
    meta_2024 = _extrair_meta_direita_p3(_words(paginas[2]))
    resultado_curso = _extrair_resultado_curso(paginas[3])

    historico = {
        "id_historico_escolar": f"EDOC-{aluno.get('matricula')}" if aluno.get("matricula") else None,
        "resultado_final": resultado_curso.get("resultado_final"),
        "data_conclusao": resultado_curso.get("data_conclusao"),
    }

    itinerario = itinerario_2024 + itinerario_2025

    extras = {
        "escola": escola,
        "aluno_oficial": {
            "cidade_nascimento": aluno.get("cidade_nascimento"),
            "uf_nascimento": aluno.get("uf_nascimento"),
            "etapa_concluida": aluno.get("serie"),
            "curso_documento": aluno.get("curso"),
        },
        "informacoes_complementares": complementares,
        "resumo_base_comum": resumo_base,
        "totais_base_comum": totais_base,
        "itinerario_metadados": {
            "2024": meta_2024,
        },
        "itinerario": itinerario,
        "resultado_curso": resultado_curso,
    }

    return {
        "aluno": aluno,
        "escola": escola,
        "historico": historico,
        "base_comum": base_comum,
        "itinerario": itinerario,
        "extras": extras,
    }

# ============================================================
# CAMADA ADAPTATIVA EDOC
# ============================================================
# O parser original acima é mantido como fallback para o layout
# oficial maior. A partir daqui, as funções públicas são
# redefinidas para também reconhecer o PDF compacto de 4 páginas
# usado no eDOC.
# ============================================================

PARSER_VERSION = "EDOC-2026-08-14-UNIFICADO-V1"

_extrair_pagina1_legado = _extrair_pagina1
_extrair_pagina2_legado = _extrair_pagina2
_extrair_meta_direita_p3_legado = _extrair_meta_direita_p3
_extrair_itinerario_pagina_legado = _extrair_itinerario_pagina
_extrair_resultado_curso_legado = _extrair_resultado_curso


def _nota_validada(valor, contexto=""):
    nota = _decimal(valor)

    if nota is None:
        return None

    if nota < 0 or nota > 10:
        detalhe = f" em {contexto}" if contexto else ""
        raise ValueError(
            f"Nota fora da faixa de 0 a 10{detalhe}: {nota}. "
            "O PDF não corresponde ao layout esperado ou uma coluna "
            "foi interpretada incorretamente."
        )

    return round(nota, 2)


def _percentual_validado(valor, contexto=""):
    percentual = _decimal(valor)

    if percentual is None:
        return None

    if percentual < 0 or percentual > 100:
        detalhe = f" em {contexto}" if contexto else ""
        raise ValueError(
            f"Percentual fora da faixa de 0 a 100{detalhe}: {percentual}."
        )

    return round(percentual, 2)


def _layout_compacto(pagina):
    largura = float(pagina.get("largura") or 0)
    return 0 < largura < 1000


def _extrair_turma_da_etapa(etapa):
    etapa = _limpar(etapa)

    if not etapa:
        return None

    m = re.search(r"\(([^()]+)\)", etapa)

    if m:
        turma = _limpar(m.group(1))
        if turma and (
            "TDS" in _normalizar(turma)
            or "MKT" in _normalizar(turma)
        ):
            return turma

    m = re.search(
        r"\b([123])\s*[ºo°]?\s*(TDS|MKT)\s*([AB])\b",
        etapa,
        re.I,
    )

    if m:
        return f"{m.group(1)}º {m.group(2).upper()} {m.group(3).upper()}"

    return None


def _extrair_serie_da_etapa(etapa):
    etapa = _limpar(etapa)

    if not etapa:
        return None

    m = re.search(r"\b([123])\s*[ºo°]?\s*ANO\b", etapa, re.I)

    if m:
        return f"{m.group(1)}º Ano"

    return etapa[:20]


def _cidade_uf_do_endereco(endereco):
    endereco = _limpar(endereco)

    if not endereco:
        return None, None

    # Ex.: "... - Caruaru, PE - CEP: ..."
    m = re.search(
        r"-\s*([^,-]+?)\s*,\s*([A-Z]{2})\b",
        endereco,
        re.I,
    )

    if m:
        return _limpar(m.group(1)), m.group(2).upper()

    return None, None


def _extrair_pagina1_compacta(pagina):
    palavras = _words(pagina)
    x_valor = 170

    def valor(rotulo, tolerancia=4):
        return _valor_rotulo(
            palavras,
            rotulo,
            x_valor=x_valor,
            tolerancia_y=tolerancia,
        )

    escola = valor("Escola")
    nome = valor("Nome do estudante")
    nome_mae = valor("Filiação - mãe")
    nome_pai = valor("Filiação - pai")
    data_nascimento = valor("Data de nascimento")
    cidade_nascimento = valor("Cidade de nascimento")
    uf_nascimento = valor("UF")
    nacionalidade = valor("Nacionalidade")
    rg = valor("RG")
    orgao = valor("Órgão expedidor")
    cpf = valor("CPF")
    matricula = valor("Matrícula")
    etapa_completa = valor("Etapa concluída")
    curso_documento = valor("Curso")
    autorizacao_completa = valor("Autorização de Funcionamento")

    # Fallback por texto: útil quando o PDF desloca poucos pontos.
    texto = pagina.get("texto", "")

    if not matricula:
        m = re.search(
            r"Matr[ií]cula\s*[:\-]?\s*(\d{5,15})",
            texto,
            re.I,
        )
        matricula = m.group(1) if m else None

    y_endereco = _achar_rotulo(
        palavras,
        "Endereço",
        x1=x_valor,
    )

    endereco_escola = None
    if y_endereco is not None:
        endereco_escola = _texto_area(
            palavras,
            x0=x_valor,
            y0=y_endereco - 10,
            y1=y_endereco + 18,
        )

    autorizacao = None
    data_doe = None

    if autorizacao_completa:
        m = re.search(
            r"(.+?)\s+D\.?O\.?E/?PE\s+de\s+(\d{2}/\d{2}/\d{4})",
            autorizacao_completa,
            re.I,
        )

        if m:
            autorizacao = _limpar(m.group(1))
            data_doe = m.group(2)
        else:
            autorizacao = autorizacao_completa

    def responsavel(rotulo):
        bruto = valor(rotulo)

        if not bruto:
            return {
                "nome": None,
                "matricula": None,
            }

        m = re.search(
            r"(.+?),?\s+mat\.?\s*n[ºo°]?\s*(\d+)",
            bruto,
            re.I,
        )

        if m:
            return {
                "nome": _limpar(m.group(1).rstrip(",")),
                "matricula": m.group(2),
            }

        return {
            "nome": bruto,
            "matricula": None,
        }

    secretario = responsavel("Secretário")
    diretor = responsavel("Diretor")

    item1 = _texto_area(
        palavras,
        x0=x_valor,
        y0=385,
        y1=440,
    )
    item2 = _texto_area(
        palavras,
        x0=x_valor,
        y0=440,
        y1=485,
    )
    item3 = _texto_area(
        palavras,
        x0=x_valor,
        y0=485,
        y1=520,
    )

    ensino_religioso = None
    if "OPTOU POR NAO VIVENCIAR" in _normalizar(item2):
        ensino_religioso = "não vivenciado"

    situacao_ed_fisica = None
    normal_item3 = _normalizar(item3)

    if "NAO DISPENSADO" in normal_item3:
        situacao_ed_fisica = "não dispensado(a)"
    elif "DISPENSADO" in normal_item3:
        situacao_ed_fisica = "dispensado(a)"

    turma = _extrair_turma_da_etapa(etapa_completa)
    serie = _extrair_serie_da_etapa(etapa_completa)

    cidade_escola, uf_escola = _cidade_uf_do_endereco(
        endereco_escola
    )

    aluno = {
        "nome": nome,
        "matricula": matricula,
        "data_nascimento": _data_br(data_nascimento),
        "cpf": cpf,
        "rg": rg,
        "orgao_expedidor": orgao,
        "nacionalidade": nacionalidade,
        "nome_pai": nome_pai,
        "nome_mae": nome_mae,
        "serie": serie,
        "curso": curso_documento,
        "cidade_nascimento": cidade_nascimento,
        "uf_nascimento": uf_nascimento,
        "id_turma": turma,
        "email": None,
        "endereco": None,
    }

    escola_info = {
        "nome": escola,
        "endereco": endereco_escola,
        "autorizacao_funcionamento": autorizacao,
        "data_doe": data_doe,
        "telefone": None,
        "cadastro_escolar": None,
        "cidade": cidade_escola,
        "estado": uf_escola,
        "secretario_nome": secretario["nome"],
        "secretario_matricula": secretario["matricula"],
        "diretor_nome": diretor["nome"],
        "diretor_matricula": diretor["matricula"],
    }

    complementares = {
        "item_1": item1,
        "item_2": item2,
        "item_3": item3,
        "ensino_religioso": ensino_religioso,
        "situacao_educacao_fisica": situacao_ed_fisica,
        "etapa_concluida_original": etapa_completa,
    }

    return aluno, escola_info, complementares


def _extrair_pagina1(pagina):
    if _layout_compacto(pagina):
        return _extrair_pagina1_compacta(pagina)

    aluno, escola, complementares = _extrair_pagina1_legado(
        pagina
    )

    # Mesmo no layout legado, normaliza o que vai para colunas curtas.
    etapa_original = aluno.get("serie")
    aluno["id_turma"] = (
        aluno.get("id_turma")
        or _extrair_turma_da_etapa(etapa_original)
    )
    aluno["serie"] = _extrair_serie_da_etapa(etapa_original)

    if complementares is not None:
        complementares.setdefault(
            "etapa_concluida_original",
            etapa_original,
        )

    return aluno, escola, complementares


def _extrair_pagina2_compacta(pagina):
    palavras = _words(pagina)

    indicadores = [
        {
            "serie": "1º Ano",
            "ano_letivo": None,
            "carga_horaria_total": None,
            "carga_horaria_relogio": None,
            "frequencia_percentual": None,
        },
        {
            "serie": "2º Ano",
            "ano_letivo": None,
            "carga_horaria_total": None,
            "carga_horaria_relogio": None,
            "frequencia_percentual": None,
        },
        {
            "serie": "3º Ano",
            "ano_letivo": None,
            "carga_horaria_total": None,
            "carga_horaria_relogio": None,
            "frequencia_percentual": None,
        },
    ]

    faixas_anos = [
        (110, 195),
        (195, 280),
        (280, 365),
    ]

    # Indicadores anuais.
    for _, linha in _linhas_por_y(
        palavras,
        220,
        275,
    ):
        texto_linha = _normalizar(
            " ".join(w["texto"] for w in linha)
        )

        if "CARGA HORARIA TOTAL" in texto_linha:
            for indice, (x0, x1) in enumerate(
                faixas_anos
            ):
                indicadores[indice][
                    "carga_horaria_total"
                ] = _inteiro(
                    _texto_area(
                        linha,
                        x0=x0,
                        x1=x1,
                    )
                )

        elif (
            "CARGA HORARIA EM HORAS/RELOGIO"
            in texto_linha
        ):
            for indice, (x0, x1) in enumerate(
                faixas_anos
            ):
                valor = _texto_area(
                    linha,
                    x0=x0,
                    x1=x1,
                )

                indicadores[indice][
                    "carga_horaria_relogio"
                ] = (
                    None
                    if valor == "-"
                    else valor
                )

        elif any("%" in w["texto"] for w in linha):
            for indice, (x0, x1) in enumerate(
                faixas_anos
            ):
                indicadores[indice][
                    "frequencia_percentual"
                ] = _percentual_validado(
                    _texto_area(
                        linha,
                        x0=x0,
                        x1=x1,
                    ),
                    f"frequência do {indice + 1}º ano",
                )

    # Histórico por ano.
    anchors = []

    for y, linha in _linhas_por_y(
        palavras,
        280,
        455,
    ):
        esquerda = _texto_area(
            linha,
            x0=15,
            x1=110,
        )

        if not esquerda:
            continue

        m = re.search(
            r"(20\d{2})\s*-\s*([123][ºo°]\s*Ano)",
            esquerda,
            re.I,
        )

        if m:
            anchors.append(
                (
                    y,
                    int(m.group(1)),
                    m.group(2),
                )
            )

    for indice, (
        y,
        ano,
        serie,
    ) in enumerate(anchors[:3]):
        faixa = [
            w
            for w in palavras
            if y - 28 <= w["y0"] < y + 28
        ]

        estabelecimento = _texto_area(
            faixa,
            x0=110,
            x1=165,
        )
        cidade_estado = _texto_area(
            faixa,
            x0=165,
            x1=205,
        )
        resultado = _texto_area(
            faixa,
            x0=205,
            x1=300,
        )

        indicadores[indice].update(
            {
                "ano_letivo": ano,
                "serie": serie,
                "estabelecimento": estabelecimento,
                "cidade_estado": cidade_estado,
                "resultado": resultado,
            }
        )

    # Formação Geral Básica.
    colunas = {
        "nome": (15, 110),
        "1_nota": (110, 180),
        "1_ch": (180, 220),
        "2_nota": (220, 265),
        "2_ch": (265, 310),
        "3_nota": (310, 350),
        "3_ch": (350, 390),
        "ch_total": (390, 445),
    }

    disciplinas = []

    for _, linha in _linhas_por_y(
        palavras,
        98,
        218,
    ):
        nome = _texto_area(
            linha,
            x0=colunas["nome"][0],
            x1=colunas["nome"][1],
        )

        if not nome:
            continue

        if "COMPONENTE CURRICULAR" in _normalizar(nome):
            continue

        # A linha de disciplina precisa possuir ao menos
        # um token numérico ou hífen depois da coluna do nome.
        if not any(
            (
                re.search(r"\d", w["texto"])
                or w["texto"] == "-"
            )
            for w in linha
            if w["x0"] >= 110
        ):
            continue

        registro = {
            "nome": nome,
        }

        for chave, (x0, x1) in colunas.items():
            if chave == "nome":
                continue

            registro[chave] = _texto_area(
                linha,
                x0=x0,
                x1=x1,
            )

        disciplinas.append(registro)

    base_comum = []

    for disciplina in disciplinas:
        for indice in range(3):
            nota = _nota_validada(
                disciplina[f"{indice + 1}_nota"],
                (
                    f"{disciplina['nome']} "
                    f"{indice + 1}º ano"
                ),
            )
            carga = _inteiro(
                disciplina[f"{indice + 1}_ch"]
            )

            if nota is None and carga is None:
                continue

            resumo = indicadores[indice]

            base_comum.append(
                {
                    "nome": disciplina["nome"],
                    "nota": nota,
                    "ano_letivo": resumo.get(
                        "ano_letivo"
                    ),
                    "serie": resumo.get("serie"),
                    "resultado": resumo.get(
                        "resultado"
                    ),
                    "frequencia_percentual":
                        resumo.get(
                            "frequencia_percentual"
                        ),
                    "carga_horaria_horas_aula":
                        carga,
                    "carga_horaria_relogio": None,
                    "carga_horaria_total_anual":
                        resumo.get(
                            "carga_horaria_total"
                        ),
                    "carga_horaria_total_componente":
                        _inteiro(
                            disciplina["ch_total"]
                        ),
                }
            )

    totais = {}

    for _, linha in _linhas_por_y(
        palavras,
        220,
        275,
    ):
        texto_linha = _normalizar(
            " ".join(w["texto"] for w in linha)
        )

        if "CARGA HORARIA TOTAL" in texto_linha:
            totais[
                "carga_horaria_total"
            ] = _inteiro(
                _texto_area(
                    linha,
                    x0=365,
                    x1=445,
                )
            )

        elif (
            "CARGA HORARIA EM HORAS/RELOGIO"
            in texto_linha
        ):
            totais[
                "carga_horaria_relogio"
            ] = _texto_area(
                linha,
                x0=365,
                x1=445,
            )

    return base_comum, indicadores, totais


def _extrair_pagina2(pagina):
    if _layout_compacto(pagina):
        return _extrair_pagina2_compacta(pagina)

    base, resumo, totais = _extrair_pagina2_legado(
        pagina
    )

    # Validação defensiva: impede que carga horária chegue
    # ao banco como se fosse nota.
    for item in base:
        item["nota"] = _nota_validada(
            item.get("nota"),
            item.get("nome") or "Formação Geral Básica",
        )

        item[
            "frequencia_percentual"
        ] = _percentual_validado(
            item.get("frequencia_percentual"),
            item.get("nome") or "Formação Geral Básica",
        )

    return base, resumo, totais


def _extrair_meta_direita_p3_compacta(palavras):
    return {
        "estabelecimento": _texto_area(
            palavras,
            x0=630,
            y0=55,
            y1=78,
        ),
        "cidade": _texto_area(
            palavras,
            x0=630,
            y0=72,
            y1=88,
        ),
        "estado": _texto_area(
            palavras,
            x0=630,
            y0=84,
            y1=100,
        ),
        "itinerarios": _texto_area(
            palavras,
            x0=630,
            y0=95,
            y1=124,
        ),
        "trilhas": _texto_area(
            palavras,
            x0=630,
            y0=123,
            y1=151,
        ),
        "observacoes": _texto_area(
            palavras,
            x0=630,
            y0=150,
            y1=172,
        ),
    }


def _extrair_meta_direita_p3(palavras):
    if not palavras:
        return _extrair_meta_direita_p3_legado(
            palavras
        )

    largura_aproximada = max(
        w.get("x1", 0)
        for w in palavras
    )

    if largura_aproximada < 900:
        return _extrair_meta_direita_p3_compacta(
            palavras
        )

    return _extrair_meta_direita_p3_legado(
        palavras
    )


def _extrair_itinerario_compacto(
    pagina,
    numero,
):
    palavras = _words(pagina)

    if numero == 3:
        x_tipo = (15, 110)
        x_unidade = (110, 265)
        x_ano = (265, 295)
        x_periodo = (295, 370)
        x_ch = (370, 405)
        x_nota = (405, 424)
        x_frequencia = (424, 470)
        x_resultado = (470, 550)
        y_min = 125
        y_max = 405
        ano_esperado = "1"

    else:
        x_tipo = (15, 145)
        x_unidade = (145, 340)
        x_ano = (340, 375)
        x_periodo = (375, 455)
        x_ch = (455, 500)
        x_nota = (500, 550)
        x_frequencia = (550, 568)
        x_resultado = (568, 680)
        y_min = 65
        y_max = 245
        ano_esperado = "2"

    anchors = []

    for palavra in palavras:
        if not (
            y_min
            <= palavra["y0"]
            < y_max
        ):
            continue

        if not (
            x_ano[0]
            <= palavra["x0"]
            < x_ano[1]
        ):
            continue

        if re.fullmatch(
            rf"{ano_esperado}[ºo°]",
            palavra["texto"],
            re.I,
        ):
            anchors.append(
                palavra["y0"]
            )

    ys = []

    for y in sorted(anchors):
        if (
            not ys
            or abs(y - ys[-1]) > 2
        ):
            ys.append(y)

    registros = []

    for indice, y in enumerate(ys):
        inicio = (
            y_min
            if indice == 0
            else (
                ys[indice - 1] + y
            ) / 2
        )

        fim = (
            y_max
            if indice == len(ys) - 1
            else (
                y + ys[indice + 1]
            ) / 2
        )

        faixa = [
            w
            for w in palavras
            if inicio <= w["y0"] < fim
        ]

        tipo = _texto_area(
            faixa,
            x0=x_tipo[0],
            x1=x_tipo[1],
        )
        nome = _texto_area(
            faixa,
            x0=x_unidade[0],
            x1=x_unidade[1],
        )
        ano = _texto_area(
            faixa,
            x0=x_ano[0],
            x1=x_ano[1],
        )
        periodo = _texto_area(
            faixa,
            x0=x_periodo[0],
            x1=x_periodo[1],
        )
        ch_txt = _texto_area(
            faixa,
            x0=x_ch[0],
            x1=x_ch[1],
        )
        nota_txt = _texto_area(
            faixa,
            x0=x_nota[0],
            x1=x_nota[1],
        )
        frequencia_txt = _texto_area(
            faixa,
            x0=x_frequencia[0],
            x1=x_frequencia[1],
        )
        resultado = _texto_area(
            faixa,
            x0=x_resultado[0],
            x1=x_resultado[1],
        )

        if not nome or not periodo:
            continue

        nota = _nota_validada(
            nota_txt,
            nome,
        )
        frequencia = _percentual_validado(
            frequencia_txt,
            nome,
        )
        carga = _inteiro(ch_txt)

        registros.append(
            {
                "nome": nome,
                "abreviacao": None,
                "tipo": tipo,
                "ano": ano,
                "nota": nota,
                "resultado_final": resultado,
                "periodo_letivo": periodo,
                "frequencia": frequencia,
                "carga_horaria": carga,
                "carga_horaria_horas_aula": carga,
                "carga_horaria_relogio": None,
            }
        )

    return registros


def _extrair_itinerario_pagina(
    pagina,
    numero,
):
    if _layout_compacto(pagina):
        return _extrair_itinerario_compacto(
            pagina,
            numero,
        )

    registros = _extrair_itinerario_pagina_legado(
        pagina,
        numero,
    )

    for item in registros:
        item["nota"] = _nota_validada(
            item.get("nota"),
            item.get("nome") or "Itinerário Formativo",
        )
        item["frequencia"] = _percentual_validado(
            item.get("frequencia"),
            item.get("nome") or "Itinerário Formativo",
        )

    return registros


def _extrair_resultado_curso_compacto(pagina):
    palavras = _words(pagina)

    def valor_proximo(
        rotulo,
        tolerancia=12,
    ):
        y = _achar_rotulo(
            palavras,
            rotulo,
            x1=145,
        )

        if y is None:
            return None

        valores = [
            w
            for w in palavras
            if (
                140 <= w["x0"] < 360
                and abs(w["y0"] - y)
                <= tolerancia
            )
        ]

        valores.sort(
            key=lambda w: (
                w["y0"],
                w["x0"],
            )
        )

        texto = _limpar(
            " ".join(
                w["texto"]
                for w in valores
            )
        )

        return (
            None
            if texto == "-"
            else texto
        )

    fgb = valor_proximo(
        "Carga Horária da Formação Geral",
        15,
    )
    itinerarios = valor_proximo(
        "Carga Horária dos Itinerários",
        15,
    )
    total = valor_proximo(
        "Carga Horária TOTAL",
        5,
    )
    conclusao_texto = valor_proximo(
        "Data da Conclusão do Curso",
        5,
    )
    resultado = valor_proximo(
        "Resultado Final",
        5,
    )
    data_local = valor_proximo(
        "Data/Local",
        5,
    )

    data_conclusao = _data_br(
        conclusao_texto
    )

    ano_conclusao = None

    if (
        data_conclusao is None
        and conclusao_texto
        and re.fullmatch(
            r"\d{4}",
            conclusao_texto,
        )
    ):
        ano_conclusao = int(
            conclusao_texto
        )

    data_emissao = _data_extenso_pt(
        data_local
    )

    cidade = None
    uf = None

    if data_local:
        m = re.match(
            r"(.+?)\s*-\s*([A-Z]{2}),",
            data_local,
            re.I,
        )

        if m:
            cidade = _limpar(
                m.group(1)
            )
            uf = m.group(2).upper()

    return {
        "carga_horaria_formacao_geral_relogio":
            fgb,
        "carga_horaria_itinerarios_relogio":
            itinerarios,
        "carga_horaria_total_relogio":
            total,
        "data_conclusao":
            data_conclusao,
        "data_conclusao_texto":
            conclusao_texto,
        "ano_conclusao":
            ano_conclusao,
        "resultado_final":
            resultado,
        "data_local":
            data_local,
        "cidade_emissao":
            cidade,
        "uf_emissao":
            uf,
        "data_emissao":
            data_emissao,
    }


def _extrair_resultado_curso(pagina):
    if _layout_compacto(pagina):
        return _extrair_resultado_curso_compacto(
            pagina
        )

    return _extrair_resultado_curso_legado(
        pagina
    )


def _validar_dados_extraidos(dados):
    aluno = dados.get("aluno") or {}

    if not aluno.get("matricula"):
        raise ValueError(
            "O PDF foi lido, mas a matrícula não foi encontrada."
        )

    matricula = str(
        aluno["matricula"]
    ).strip()

    if not re.fullmatch(
        r"\d{5,15}",
        matricula,
    ):
        raise ValueError(
            f"Matrícula extraída inválida: {matricula!r}."
        )

    for item in dados.get(
        "base_comum",
        [],
    ):
        _nota_validada(
            item.get("nota"),
            item.get("nome") or "Formação Geral Básica",
        )
        _percentual_validado(
            item.get("frequencia_percentual"),
            item.get("nome") or "Formação Geral Básica",
        )

    for item in dados.get(
        "itinerario",
        [],
    ):
        _nota_validada(
            item.get("nota"),
            item.get("nome") or "Itinerário Formativo",
        )
        _percentual_validado(
            item.get("frequencia"),
            item.get("nome") or "Itinerário Formativo",
        )

    return dados


def extrair_dados_siepe(
    texto,
    tabelas=None,
    paginas=None,
):
    paginas = paginas or []

    if len(paginas) < 4:
        raise ValueError(
            "O histórico escolar esperado possui 4 páginas. "
            "Não foi possível identificar todas as páginas do documento."
        )

    aluno, escola, complementares = _extrair_pagina1(
        paginas[0]
    )

    base_comum, resumo_base, totais_base = _extrair_pagina2(
        paginas[1]
    )

    itinerario_2024 = _extrair_itinerario_pagina(
        paginas[2],
        3,
    )

    itinerario_2025 = _extrair_itinerario_pagina(
        paginas[3],
        4,
    )

    meta_2024 = _extrair_meta_direita_p3(
        _words(paginas[2])
    )

    resultado_curso = _extrair_resultado_curso(
        paginas[3]
    )

    etapa_original = (
        (complementares or {}).get(
            "etapa_concluida_original"
        )
        or aluno.get("serie")
    )

    historico = {
        "id_historico_escolar": (
            f"EDOC-{aluno.get('matricula')}"
            if aluno.get("matricula")
            else None
        ),
        "resultado_final":
            resultado_curso.get(
                "resultado_final"
            ),
        "data_conclusao":
            resultado_curso.get(
                "data_conclusao"
            ),
    }

    itinerario = (
        itinerario_2024
        + itinerario_2025
    )

    extras = {
        "parser_version":
            PARSER_VERSION,
        "escola":
            escola,
        "aluno_oficial": {
            "cidade_nascimento":
                aluno.get(
                    "cidade_nascimento"
                ),
            "uf_nascimento":
                aluno.get(
                    "uf_nascimento"
                ),
            "etapa_concluida":
                _extrair_serie_da_etapa(
                    etapa_original
                ),
            "etapa_concluida_original":
                etapa_original,
            "curso_documento":
                aluno.get("curso"),
            "turma_documento":
                aluno.get("id_turma"),
        },
        "informacoes_complementares":
            complementares,
        "resumo_base_comum":
            resumo_base,
        "totais_base_comum":
            totais_base,
        "itinerario_metadados": {
            "2024": meta_2024,
        },
        "itinerario":
            itinerario,
        "resultado_curso":
            resultado_curso,
    }

    dados = {
        "aluno": aluno,
        "escola": escola,
        "historico": historico,
        "base_comum": base_comum,
        "itinerario": itinerario,
        "extras": extras,
    }

    return _validar_dados_extraidos(
        dados
    )
