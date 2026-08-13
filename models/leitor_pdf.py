import pymupdf


def extrair_texto_pdf(arquivo):

    # Lê os bytes enviados pelo Flask
    conteudo = arquivo.read()

    if not conteudo:
        raise ValueError("O PDF está vazio.")

    # Abre o PDF diretamente da memória
    documento = pymupdf.open(
        stream=conteudo,
        filetype="pdf"
    )

    texto_completo = []

    for pagina in documento:

        texto = pagina.get_text(
            "text",
            sort=True
        )

        texto_completo.append(texto)

    documento.close()

    texto_final = "\n".join(
        texto_completo
    ).strip()

    if len(texto_final) < 30:

        raise ValueError(
            "Não foi possível extrair texto suficiente do PDF. "
            "O documento pode ser digitalizado como imagem."
        )

    return texto_final