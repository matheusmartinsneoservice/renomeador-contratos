import fitz
import re
import tempfile
import unicodedata

def extrair_texto(pdf):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        temp.write(pdf.getvalue())

        caminho_pdf = temp.name

    doc = fitz.open(caminho_pdf)

    texto = ""

    for pagina in doc:
        texto += pagina.get_text()

    doc.close()

    return texto.upper()


def identificar_tipo_documento(texto):

    if "INSTRUMENTO PARTICULAR DE DISTRATO" in texto:
        return "DISTRATO"

    return "CONTRATO"


def extrair_unidade(texto):

    match = re.search(
        r"UNIDADE\s*(\d+)\s*,\s*APTO",
        texto
    )

    if match:
        return match.group(1).zfill(3)

    match = re.search(
        r"APTO:\s*UNIDADE\s*(\d+)",
        texto
    )

    if match:
        return match.group(1).zfill(3)

    return None

def extrair_tipo(texto):

    match = re.search(
        r"TIPO:\s*(APTO\s+(?:OURO|DIAMANTE))",
        texto
    )

    if match:
        return match.group(1).strip()

    match = re.search(
        r"UNIDADE\s*\d+\s*,\s*(APTO\s+(?:OURO|DIAMANTE))",
        texto
    )

    if match:
        return match.group(1).strip()

    return None

def extrair_letra(texto):

    match = re.search(
        r"FRAÇÃO\s+LETRA:\s*([A-Z])",
        texto
    )

    if match:
        return match.group(1)

    match = re.search(
        r"APTO\s+(?:OURO|DIAMANTE)\s*,\s*([A-Z])",
        texto
    )

    if match:
        return match.group(1)

    return None

def extrair_cliente_pdf(texto):

    # DISTRATO

    match = re.search(
        r"II\s*[-–]\s*([A-Z\sÇÃÕÁÉÍÓÚÂÊÔ]+?)\s*,\s*BRASIL",
        texto
    )

    if match:

        return limpar_texto(
            match.group(1)
        )

    # CONTRATO

    match = re.search(
        r"COMPRADOR\(A\)\s*1:\s*NOME:\s*([A-Z\sÇÃÕÁÉÍÓÚÂÊÔ]+)",
        texto
    )

    if match:

        return limpar_texto(
            match.group(1)
        )

    return None

def limpar_texto(texto):

    return (
        str(texto)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

def localizar_cliente(
    unidade,
    cliente_pdf,
    tabela
):

    candidatos = tabela[
        tabela["Unidade"]
        .astype(str)
        .str.zfill(3)
        ==
        str(unidade).zfill(3)
    ]

    if len(candidatos) == 0:

        return "CLIENTE NÃO ENCONTRADO"

    if len(candidatos) == 1:

        return limpar_texto(
            candidatos.iloc[0]["Cliente"]
        )

    cliente_pdf = limpar_texto(
        cliente_pdf or ""
    )

    for _, linha in candidatos.iterrows():

        cliente_tabela = limpar_texto(
            linha["Cliente"]
        )

        if cliente_pdf in cliente_tabela:

            return limpar_texto(
                linha["Cliente"]
            )

        if cliente_tabela in cliente_pdf:

            return limpar_texto(
                linha["Cliente"]
            )

    return "CLIENTE DUPLICADO - VALIDAR"

    candidatos = tabela[
        tabela["Unidade"]
        .astype(str)
        .str.zfill(3)
        ==
        str(unidade).zfill(3)
    ]

    if len(candidatos) == 0:

        return "CLIENTE NÃO ENCONTRADO"

    return str(
        candidatos.iloc[0]["Cliente"]
    ).strip()

def normalizar_texto(texto):

    texto = str(texto)

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        c
        for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return texto.upper().strip()

def formatar_tipo_nome(tipo):

    tipo = str(tipo).upper().strip()

    if tipo == "APTO OURO":
        return "APARTAMENTO OURO"

    if tipo == "APTO DIAMANTE":
        return "APARTAMENTO DIAMANTE"

    return tipo

def gerar_nome(
    unidade,
    tipo,
    letra,
    cliente,
    tipo_documento
):
    tipo = limpar_texto(tipo)
    letra = limpar_texto(letra)
    cliente = limpar_texto(cliente)

    tipo_nome = formatar_tipo_nome(
        tipo
    )

    return (
        f"CRI GRAN PARADISO (GP) - "
        f"UNIDADE {unidade} - "
        f"{tipo_nome} - "
        f"{letra} - "
        f"{cliente} - "
        f"{tipo_documento}.pdf"
    )

def processar_gran_paradiso(
    pdfs,
    tabela
):

    nomes = []

    for pdf in pdfs:

        texto = extrair_texto(pdf)

        cliente_pdf = extrair_cliente_pdf(
            texto
        )

        print("=" * 50)
        print("CLIENTE PDF =", cliente_pdf)
        print("=" * 50)

        unidade = extrair_unidade(texto)

        print("UNIDADE ENCONTRADA:", unidade)

        tipo = extrair_tipo(texto)

        letra = extrair_letra(texto)

        if not tipo:

            tipo = "TIPO NÃO ENCONTRADO"

        if not letra:

            letra = "?"

        if not unidade:

            unidade = "???"

        print(unidade)
        print(tipo)
        print(letra)

        cliente = localizar_cliente(
            unidade,
            cliente_pdf,
            tabela
        )

        tipo_documento = identificar_tipo_documento(
            texto
        )

        nome = gerar_nome(
            unidade,
            tipo,
            letra,
            cliente,
            tipo_documento
        )

        nomes.append(nome)

    return nomes
