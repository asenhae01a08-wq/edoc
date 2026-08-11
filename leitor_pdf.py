from io import BytesIO

import pymupdf
import pdfplumber


def extrair_conteudo_pdf(arquivo):
    """Retorna texto e tabelas do PDF sem gravar o arquivo no disco."""
    conteudo = arquivo.read()

    if not conteudo:
        raise ValueError("O PDF está vazio.")

    documento = pymupdf.open(stream=conteudo, filetype="pdf")
    textos_paginas = []

    try:
        for pagina in documento:
            textos_paginas.append(pagina.get_text("text", sort=True))
    finally:
        documento.close()

    texto = "\n".join(textos_paginas).strip()

    if len(texto) < 30:
        raise ValueError(
            "Não foi possível extrair texto suficiente do PDF. "
            "Se o documento for somente imagem, será necessário ativar OCR."
        )

    tabelas = []

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
        "quantidade_paginas": len(textos_paginas),
    }
