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

    cliente = candidatos.iloc[0]["Cliente"]

    return limpar_texto(
        cliente
    )


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

    st.write(tabela)

    nomes = []

    for pdf in pdfs:

        texto = extrair_texto(
            pdf
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