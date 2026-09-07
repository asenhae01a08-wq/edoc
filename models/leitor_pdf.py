import pymupdf


# Realiza a extração do texto de arquivos PDF enviados pelo sistema.
# O conteúdo é lido diretamente da memória, sem precisar salvar
# o arquivo fisicamente no computador.
def extrair_texto_pdf(arquivo):

    # Lê os bytes do arquivo enviado pelo usuário.
    conteudo = arquivo.read()

    # Verifica se o arquivo possui conteúdo válido.
    if not conteudo:
        raise ValueError("O PDF está vazio.")

    # Abre o PDF utilizando os dados carregados em memória.
    # Essa abordagem evita a criação de arquivos temporários.
    documento = pymupdf.open(
        stream=conteudo,
        filetype="pdf"
    )

    texto_completo = []

    # Percorre todas as páginas do documento
    # e extrai o texto presente em cada uma.
    for pagina in documento:

        texto = pagina.get_text(
            "text",
            sort=True
        )

        texto_completo.append(texto)

    # Libera os recursos utilizados pelo documento PDF.
    documento.close()

    # Junta todo o texto extraído das páginas
    # em uma única variável para processamento.
    texto_final = "\n".join(
        texto_completo
    ).strip()

    # Verifica se houve uma extração válida.
    # Caso o PDF seja apenas uma imagem digitalizada,
    # o sistema informa que não conseguiu interpretar o conteúdo.
    if len(texto_final) < 30:

        raise ValueError(
            "Não foi possível extrair texto suficiente do PDF. "
            "O documento pode ser digitalizado como imagem."
        )

    return texto_final