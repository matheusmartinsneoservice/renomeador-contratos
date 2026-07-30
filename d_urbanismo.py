import fitz
import re
import tempfile


EMPREENDIMENTOS_D_URBANISMO = [

    "BELO MONTE",

    "BOSQUE DO CATU",

    "BRISA DO PARACURU",

    "BRISAS DO ALTO",

    "BRISAS DO LAGO",

    "CAMINHOS DA SERRA",

    "COLINAS",

    "RIVIERA",

    "SERRA GRANDE",

    "VISTA DA SERRA"
]


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

    texto = extrair_texto(pdf)

    if "INSTRUMENTO PARTICULAR DE DISTRATO" in texto:

        return "DISTRATO"

    if "CONTRATO PARTICULAR DE CESS" in texto:

        return "CESSAO"

    if "PRIMEIRO ADITIVO" in texto:

        return "ADITIVO"

    return "CONTRATO"


def extrair_empreendimento(pdf):

    texto = extrair_texto(pdf)

    for empreendimento in EMPREENDIMENTOS_D_URBANISMO:

        if empreendimento in texto:

            return empreendimento

    return "EMPREENDIMENTO NÃO ENCONTRADO"


def extrair_unidade_contrato(texto):

    quadra = re.search(
        r"QUADRA\s*:?\s*\n*\s*([A-Z])",
        texto,
        re.IGNORECASE
    )

    lote = re.search(
        r"LOTE\(S\)\s*:?\s*\n*\s*(\d+)",
        texto,
        re.IGNORECASE
    )

    if quadra and lote:

        return (
            f"{quadra.group(1)}."
            f"{int(lote.group(1))}"
        )

    return None


def extrair_unidade_distrato(texto):

    match = re.search(
        r"LOTE(?:\s*N\.)?\s*(\d+)\s*[–-]\s*QUADRA\s*([A-Z])",
        texto
    )

    if match:

        return (
            f"{match.group(2)}."
            f"{int(match.group(1))}"
        )

    return None


def extrair_unidade_cessao(texto):

    match = re.search(
        r"LOTE\s*(\d+)\s*[–-]\s*QUADRA\s*([A-Z])",
        texto
    )

    if match:

        return (
            f"{match.group(2)}."
            f"{int(match.group(1))}"
        )

    return None


def extrair_unidade_aditivo(texto):

    match = re.search(
        r"([A-Z])\s*[–-]\s*LOTE\s*(\d+)",
        texto
    )

    if match:

        return (
            f"{match.group(1)}."
            f"{int(match.group(2))}"
        )

    return None


def extrair_unidade(pdf):

    texto = extrair_texto(pdf)

    tipo = identificar_tipo_documento(pdf)

    if tipo == "CONTRATO":

        unidade = extrair_unidade_contrato(
            texto
        )

        if unidade:

            return unidade

    elif tipo == "DISTRATO":

        unidade = extrair_unidade_distrato(
            texto
        )

        if unidade:

            return unidade

    elif tipo == "CESSAO":

        unidade = extrair_unidade_cessao(
            texto
        )

        if unidade:

            return unidade

    elif tipo == "ADITIVO":

        unidade = extrair_unidade_aditivo(
            texto
        )

        if unidade:

            return unidade

    return "UNIDADE NÃO ENCONTRADA"

def extrair_cliente_pdf(pdf):

    texto = extrair_texto(pdf)

    match = re.search(
        r"NOME\s*:\s*([A-Z\sÇÃÕÁÉÍÓÚÂÊÔ]+)",
        texto,
        re.IGNORECASE
    )

    if match:

        return " ".join(
            match.group(1).split()
        )

    return None

def localizar_cliente(
    empreendimento,
    unidade,
    cliente_pdf,
    tabela
):

    candidatos = tabela[
        (
            tabela["Empreendimento"]
            .astype(str)
            .str.upper()
            .str.strip()
            ==
            empreendimento.upper().strip()
        )
        &
        (
            tabela["Unidade"]
            .astype(str)
            .str.upper()
            .str.strip()
            ==
            unidade.upper().strip()
        )
    ]

    if len(candidatos) == 0:

        return "CLIENTE NÃO ENCONTRADO"

    if len(candidatos) == 1:

        return str(
            candidatos.iloc[0]["Cliente"]
        ).strip()

    cliente_pdf = str(
        cliente_pdf or ""
    ).upper()

    for _, linha in candidatos.iterrows():

        cliente_tabela = str(
            linha["Cliente"]
        ).upper()

        if cliente_pdf in cliente_tabela:

            return linha["Cliente"]

        if cliente_tabela in cliente_pdf:

            return linha["Cliente"]

    return "CLIENTE DUPLICADO - VALIDAR"

def gerar_nome(
    empreendimento,
    unidade,
    cliente,
    tipo
):

    return (
        f"CRI D URBANISMO "
        f"({empreendimento}) - "
        f"UNIDADE {unidade} - "
        f"{cliente} - "
        f"{tipo}.pdf"
    )


def processar_d_urbanismo(
    pdfs,
    tabela
):

    nomes = []

    for pdf in pdfs:

        tipo = identificar_tipo_documento(
            pdf
        )

        empreendimento = (
            extrair_empreendimento(
                pdf
            )
        )

        cliente_pdf = extrair_cliente_pdf(
            pdf
        )

        print(
            "CLIENTE PDF =",
            cliente_pdf
        )

        unidade = extrair_unidade(
            pdf
        )

        cliente = localizar_cliente(
            empreendimento,
            unidade,
            cliente_pdf,
            tabela
        )

        nome = gerar_nome(
            empreendimento,
            unidade,
            cliente,
            tipo
        )

        nomes.append(
            nome
        )

    return nomes
