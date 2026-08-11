import re


def procurar(padroes, texto):

    for padrao in padroes:

        resultado = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if resultado:

            valor = resultado.group(1)

            return valor.strip()

    return None


def extrair_dados_siepe(texto):

    dados = {}


    # ==========================================
    # MATRÍCULA
    # ==========================================

    dados["matricula"] = procurar(
        [
            r"Matr[ií]cula\s*[:\-]?\s*(\d{5,15})",
            r"Mat\.\s*[:\-]?\s*(\d{5,15})"
        ],
        texto
    )


    # ==========================================
    # NOME
    # ==========================================

    dados["nome"] = procurar(
        [
            r"Nome(?:\s+do\s+Aluno)?\s*[:\-]\s*([^\n]+)",
            r"Estudante\s*[:\-]\s*([^\n]+)"
        ],
        texto
    )


    # ==========================================
    # CPF
    # ==========================================

    dados["cpf"] = procurar(
        [
            r"CPF\s*[:\-]?\s*(\d{3}\.?\d{3}\.?\d{3}[-\.]?\d{2})"
        ],
        texto
    )


    # ==========================================
    # RG
    # ==========================================

    dados["rg"] = procurar(
        [
            r"RG\s*[:\-]?\s*([0-9.\-]+)"
        ],
        texto
    )


    # ==========================================
    # DATA DE NASCIMENTO
    # ==========================================

    dados["data_nascimento"] = procurar(
        [
            r"Data\s+de\s+Nascimento\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})",
            r"Nascimento\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})"
        ],
        texto
    )


    # ==========================================
    # MÃE
    # ==========================================

    dados["nome_mae"] = procurar(
        [
            r"Nome\s+da\s+M[aã]e\s*[:\-]?\s*([^\n]+)",
            r"M[aã]e\s*[:\-]?\s*([^\n]+)"
        ],
        texto
    )


    # ==========================================
    # PAI
    # ==========================================

    dados["nome_pai"] = procurar(
        [
            r"Nome\s+do\s+Pai\s*[:\-]?\s*([^\n]+)",
            r"Pai\s*[:\-]?\s*([^\n]+)"
        ],
        texto
    )


    # ==========================================
    # NATURALIDADE
    # ==========================================

    dados["cidade_nascimento"] = procurar(
        [
            r"Naturalidade\s*[:\-]?\s*([^\n/]+)"
        ],
        texto
    )


    # ==========================================
    # UF
    # ==========================================

    dados["uf_nascimento"] = procurar(
        [
            r"Naturalidade\s*[:\-]?\s*[^\n/]+[/\-]\s*([A-Z]{2})"
        ],
        texto
    )


    # ==========================================
    # NACIONALIDADE
    # ==========================================

    dados["nacionalidade"] = procurar(
        [
            r"Nacionalidade\s*[:\-]?\s*([^\n]+)"
        ],
        texto
    )


    # Guarda também o texto bruto inicialmente.
    # Isso ajuda muito durante os testes.

    dados["texto_original"] = texto


    return dados