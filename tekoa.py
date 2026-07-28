import fitz
import re
import tempfile

def extrair_unidade(pdf):

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

    texto = texto.upper()

    # PROCURA O TRECHO "Nº DA UNIDADE"

    partes = texto.split(
        "Nº DA UNIDADE"
    )

    if len(partes) > 1:

        trecho = partes[1][:200]

        match = re.search(
            r"(\d{3}\s*[A-Z])",
            trecho
        )

        if match:

            unidade = match.group(1)

            unidade = re.sub(
                r"(\d{3})([A-Z])",
                r"\1 \2",
                unidade
            )

            return unidade.strip()

    return "NÃO ENCONTRADA"

def localizar_cliente(
    unidade,
    tabela
):

    candidatos = tabela[
        tabela["Unidade"]
        .astype(str)
        .str.upper()
        .str.strip()
        ==
        unidade.upper().strip()
    ]

    if len(candidatos) == 0:

        return "CLIENTE NÃO ENCONTRADO"

    cliente = str(
        candidatos.iloc[0]["Cliente"]
    )

    cliente = cliente.replace(
        "\n",
        " "
    )

    cliente = cliente.replace(
        "\r",
        " "
    )

    cliente = " ".join(
        cliente.split()
    )

    return cliente

def gerar_nome(
    unidade,
    cliente
):

    cliente = str(cliente)

    cliente = cliente.replace(
        "\n",
        " "
    )

    cliente = cliente.replace(
        "\r",
        " "
    )

    cliente = " ".join(
        cliente.split()
    )

    return (
        f"CRI BAUTEN (TEKOÁ) - "
        f"UNIDADE {unidade} - "
        f"{cliente} - "
        f"CONTRATO.pdf"
    )

    cliente = str(cliente)

    cliente = cliente.replace(
        "\n",
        " "
    )

    cliente = cliente.replace(
        "\r",
        " "
    )

    cliente = " ".join(
        cliente.split()
    )

    return (
        f"CRI BAUTEN (TEKOÁ) - "
        f"UNIDADE {unidade} - "
        f"{cliente} - "
        f"CONTRATO.pdf"
    )

def processar_tekoa(
    pdfs,
    tabela
):

    tabela = tabela[
        tabela["Unidade"]
        .astype(str)
        .str.strip()
        != ""
    ]

    nomes = []

    for pdf in pdfs:

        unidade = extrair_unidade(pdf)

        cliente = localizar_cliente(
            unidade,
            tabela
        )

        nome = gerar_nome(
            unidade,
            cliente
        )

        nomes.append(nome)

    return nomes