LEITOR_PDF_VERSION = "EDOC-2026-08-14-V1"

from io import BytesIO

import pymupdf
import pdfplumber


def extrair_conteudo_pdf(arquivo):
    """
    Lê o PDF oficial do histórico escolar.

    Retorna:
    - texto completo;
    - tabelas do pdfplumber (mantidas por compatibilidade);
    - páginas com texto e palavras posicionadas do PyMuPDF.

    As coordenadas das palavras são importantes porque o documento oficial
    usa tabelas visuais e algumas células não são separadas corretamente pelo
    pdfplumber.
    """
    conteudo = arquivo.read()

    if not conteudo:
        raise ValueError("O PDF está vazio.")

    documento = pymupdf.open(stream=conteudo, filetype="pdf")

    textos_paginas = []
    paginas = []

    try:
        for numero, pagina in enumerate(documento, start=1):
            texto_pagina = pagina.get_text("text", sort=True)
            textos_paginas.append(texto_pagina)

            palavras = []
            for palavra in pagina.get_text("words", sort=True):
                palavras.append(
                    {
                        "x0": float(palavra[0]),
                        "y0": float(palavra[1]),
                        "x1": float(palavra[2]),
                        "y1": float(palavra[3]),
                        "texto": palavra[4],
                    }
                )

            paginas.append(
                {
                    "numero": numero,
                    "texto": texto_pagina,
                    "largura": float(pagina.rect.width),
                    "altura": float(pagina.rect.height),
                    "palavras": palavras,
                }
            )
    finally:
        documento.close()

    texto = "\n".join(textos_paginas).strip()

    if len(texto) < 30:
        raise ValueError(
            "Não foi possível extrair texto suficiente do PDF. "
            "Se o documento for somente imagem, será necessário ativar OCR."
        )

    tabelas = []

    # Mantemos o pdfplumber porque ele ainda pode ser útil em outros
    # documentos, mas o parser do histórico oficial usa principalmente
    # as coordenadas do PyMuPDF.
    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for numero_pagina, pagina in enumerate(pdf.pages, start=1):
            for tabela in pagina.extract_tables() or []:
                tabelas.append(
                    {
                        "pagina": numero_pagina,
                        "linhas": tabela,
                    }
                )

    return {
        "texto": texto,
        "tabelas": tabelas,
        "paginas": paginas,
        "quantidade_paginas": len(paginas),
    }
