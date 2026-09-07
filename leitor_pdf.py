LEITOR_PDF_VERSION = "EDOC-2026-08-14-V1"

from io import BytesIO

import pymupdf
import pdfplumber


# Realiza a leitura dos documentos PDF do SIEPE.
# O método combina PyMuPDF e pdfplumber para extrair
# informações necessárias para geração da Ficha 19.
def extrair_conteudo_pdf(arquivo):

    """
    Lê o PDF oficial do histórico escolar.

    Retorna:
    - texto completo;
    - tabelas extraídas;
    - páginas com informações de posicionamento.

    As coordenadas das palavras são utilizadas para interpretar
    corretamente tabelas do documento oficial.
    """

    # Lê o arquivo enviado pelo usuário diretamente em memória,
    # evitando a necessidade de salvar arquivos temporários.
    conteudo = arquivo.read()

    # Valida se o arquivo recebido possui conteúdo.
    if not conteudo:
        raise ValueError("O PDF está vazio.")

    # Abre o documento PDF utilizando os bytes carregados.
    documento = pymupdf.open(
        stream=conteudo,
        filetype="pdf"
    )

    textos_paginas = []
    paginas = []

    try:

        # Percorre todas as páginas do documento,
        # extraindo texto e posição das palavras.
        for numero, pagina in enumerate(documento, start=1):

            # Extrai o texto da página.
            # sort=True tenta organizar o texto
            # seguindo a ordem visual do documento.
            texto_pagina = pagina.get_text(
                "text",
                sort=True
            )

            textos_paginas.append(texto_pagina)

            # Lista que armazenará cada palavra
            # juntamente com sua posição no PDF.
            palavras = []

            # Extrai as palavras individualmente.
            # O PyMuPDF retorna:
            #
            # 0 = posição X inicial
            # 1 = posição Y inicial
            # 2 = posição X final
            # 3 = posição Y final
            # 4 = texto
            #
            # Essas coordenadas são importantes para
            # interpretar tabelas do histórico escolar.
            for palavra in pagina.get_text(
                "words",
                sort=True
            ):

                palavras.append(
                    {
                        "x0": float(palavra[0]),
                        "y0": float(palavra[1]),
                        "x1": float(palavra[2]),
                        "y1": float(palavra[3]),
                        "texto": palavra[4],
                    }
                )

            # Guarda todas as informações importantes
            # daquela página.
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

        # Fecha o documento depois da leitura.
        # Isso libera os recursos utilizados pelo PyMuPDF.
        documento.close()

    # Junta o texto de todas as páginas em uma única string.
    texto = "\n".join(
        textos_paginas
    ).strip()

    # Verifica se foi possível extrair uma quantidade
    # mínima de texto.
    #
    # Caso o PDF seja somente uma imagem digitalizada,
    # o PyMuPDF não conseguirá extrair o texto normalmente.
    if len(texto) < 30:

        raise ValueError(
            "Não foi possível extrair texto suficiente do PDF. "
            "Se o documento for somente imagem, será necessário ativar OCR."
        )

    # Lista que armazenará as tabelas encontradas pelo pdfplumber.
    tabelas = []

    # Abre novamente o conteúdo em memória,
    # dessa vez utilizando o pdfplumber.
    #
    # O pdfplumber é utilizado principalmente
    # para tentar identificar tabelas.
    with pdfplumber.open(
        BytesIO(conteudo)
    ) as pdf:

        # Percorre todas as páginas.
        for numero_pagina, pagina in enumerate(
            pdf.pages,
            start=1
        ):

            # Tenta extrair todas as tabelas da página.
            for tabela in pagina.extract_tables() or []:

                # Guarda a página e suas linhas.
                tabelas.append(
                    {
                        "pagina": numero_pagina,
                        "linhas": tabela,
                    }
                )

    # Retorna todas as informações necessárias
    # para o parser do SIEPE.
    return {
        "texto": texto,
        "tabelas": tabelas,
        "paginas": paginas,
        "quantidade_paginas": len(paginas),
    }