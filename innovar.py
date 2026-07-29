import fitz
import re
import tempfile


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
    """
    Procura padrões:

    Q23-I2-L012
    Q11-L012
    Q008-L003
    """

    match = re.search(
        r"(Q\d+(?:-[A-Z0-9]+)*-L\d+)",
        texto
    )

    if match:
        return match.group(1)

    return None


def localizar_cliente(
    quadra,
    lote,
    tabela
):

    candidatos = tabela[
        (
            tabela["Quadra"]
            .astype(str)
            .str.strip()
            ==
            str(quadra)
        )
        &
        (
            tabela["Lote"]
            .astype(str)
            .str.strip()
            ==
            str(lote)
        )
    ]

    if len(candidatos) == 0:

        return "CLIENTE NÃO ENCONTRADO"

    return str(
        candidatos.iloc[0]["Cliente"]
    ).strip()

def localizar_empreendimento(
    quadra,
    lote,
    tabela
):

    candidatos = tabela[
        (
            tabela["Quadra"]
            .astype(str)
            .str.strip()
            ==
            str(quadra)
        )
        &
        (
            tabela["Lote"]
            .astype(str)
            .str.strip()
            ==
            str(lote)
        )
    ]

    if len(candidatos) == 0:

        return "EMPREENDIMENTO NÃO ENCONTRADO"

    return str(
        candidatos.iloc[0]["Empreendimento"]
    ).strip()

def extrair_quadra_lote(texto):

    quadra_match = re.search(
        r"QUADRA\s*:?\s*(\d+)",
        texto,
        re.IGNORECASE
    )

    lote_match = re.search(
        r"LOTE\s*:?\s*(\d+)",
        texto,
        re.IGNORECASE
    )

    quadra = (
        quadra_match.group(1).zfill(2)
        if quadra_match
        else None
    )

    lote = (
        lote_match.group(1).zfill(3)
        if lote_match
        else None
    )

    return quadra, lote

def limpar_texto(texto):

    return (
        str(texto)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def gerar_nome(
    empreendimento,
    quadra,
    lote,
    cliente,
    tipo_documento
):

    empreendimento = limpar_texto(
        empreendimento
    )

    cliente = limpar_texto(
        cliente
    )

    return (
        f"CRI INNOVAR ({empreendimento}) - "
        f"QUADRA {quadra} "
        f"LOTE {lote} - "
        f"{cliente} - "
        f"{tipo_documento}.pdf"
    )

def processar_innovar(
    pdfs,
    tabela
):

    nomes = []

    for pdf in pdfs:

        texto = extrair_texto(pdf)

        print("=" * 50)
        print(texto[:5000])
        print("=" * 50)

        quadra, lote = extrair_quadra_lote(
            texto
        )

        print(
            "QUADRA ENCONTRADA:",
            quadra
        )

        print(
            "LOTE ENCONTRADO:",
            lote
        )

        if not quadra:
            quadra = "???"

        if not lote:
            lote = "???"

        cliente = localizar_cliente(
            quadra,
            lote,
            tabela
        )

        empreendimento = localizar_empreendimento(
            quadra,
            lote,
            tabela
        )

        tipo_documento = identificar_tipo_documento(
            texto
        )

        nome = gerar_nome(
            empreendimento,
            quadra,
            lote,
            cliente,
            tipo_documento
        )

        nomes.append(nome)

    return nomes