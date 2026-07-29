import fitz
import re
import tempfile


def extrair_texto(pdf):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        temp.write(
            pdf.getvalue()
        )

        caminho_pdf = temp.name

    doc = fitz.open(caminho_pdf)

    texto = ""

    for pagina in doc:

        texto += pagina.get_text()

    return texto.upper()


def identificar_tipo_documento(pdf):

    return "CONTRATO"


def extrair_quadra(texto):

    match = re.search(
        r"QUADRA\s*:?\s*(\d+)",
        texto
    )

    if match:

        return match.group(1).zfill(2)

    return None


def extrair_lote(texto):

    match = re.search(
        r"LOTE(?:\(S\))?\s*:?\s*(\d+)",
        texto
    )

    if match:

        return str(
            int(match.group(1))
        )

    return None

def extrair_cliente_pdf(texto):

    match = re.search(
        r"COMPRADOR\s*SRº?\(A\)\s*([A-Z\s]+?)\s*DE\s+NACIONALIDADE",
        texto,
        re.IGNORECASE
    )

    if match:

        return limpar_texto(
            match.group(1)
        )

    return None

def limpar_texto(texto):

    texto = str(texto)

    texto = texto.replace("\\n", " ")
    texto = texto.replace("\\r", " ")

    texto = texto.replace("\n", " ")
    texto = texto.replace("\r", " ")

    texto = texto.replace("\t", " ")

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()

def localizar_cliente(
    quadra,
    lote,
    cliente_pdf,
    tabela
):

    candidatos = tabela[
        (
            tabela["Quadra"]
            .astype(str)
            .str.zfill(2)
            ==
            str(quadra).zfill(2)
        )
        &
        (
            tabela["Lote"]
            .astype(str)
            .apply(
                lambda x: re.sub(
                    r"\D",
                    "",
                    str(x)
                )
            )
            ==
            str(lote)
        )
    ]

    if len(candidatos) == 0:

        return "CLIENTE NÃO ENCONTRADO"

    if len(candidatos) == 1:

        return limpar_texto(
            candidatos.iloc[0]["Cliente"]
        )

    cliente_pdf = limpar_texto(
        cliente_pdf or ""
    ).upper()

    for _, linha in candidatos.iterrows():

        cliente_tabela = limpar_texto(
            linha["Cliente"]
        ).upper()

        if cliente_pdf in cliente_tabela:

            return limpar_texto(
                linha["Cliente"]
            )

        if cliente_tabela in cliente_pdf:

            return limpar_texto(
                linha["Cliente"]
            )

    return "CLIENTE DUPLICADO - VALIDAR"

def gerar_nome(
    quadra,
    lote,
    cliente,
    tipo
):

    cliente = limpar_texto(
        cliente
    )

    return (
        f"CRI MARECHAL - "
        f"QUADRA {quadra} "
        f"LOTE {lote} - "
        f"{cliente} - "
        f"{tipo}.pdf"
    )


def processar_marechal(
    pdfs,
    tabela
):

    nomes = []

    for pdf in pdfs:

        texto = extrair_texto(
            pdf
        )

        cliente_pdf = extrair_cliente_pdf(
            texto
        )

        tipo = identificar_tipo_documento(
            pdf
        )

        quadra = extrair_quadra(
            texto
        )

        lote = extrair_lote(
            texto
        )

        if not quadra:

            quadra = "??"

        if not lote:

            lote = "??"

        cliente = localizar_cliente(
            quadra,
            lote,
            cliente_pdf,
            tabela
        )

        nome = gerar_nome(
            quadra,
            lote,
            cliente,
            tipo
        )

        nomes.append(
            nome
        )

    return nomes
