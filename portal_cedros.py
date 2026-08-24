import fitz
import re


# ======================================================
# NORMALIZAÇÃO
# ======================================================

def normalizar(texto):

    texto = texto.upper()

    mapa = {
        "Á": "A",
        "À": "A",
        "Ã": "A",
        "Â": "A",
        "É": "E",
        "Ê": "E",
        "Í": "I",
        "Ó": "O",
        "Ô": "O",
        "Õ": "O",
        "Ú": "U",
        "Ç": "C",
    }

    for antigo, novo in mapa.items():

        texto = texto.replace(
            antigo,
            novo
        )

    return texto


# ======================================================
# EXTRAÇÃO PDF
# ======================================================

def extrair_texto(pdf):

    pdf.seek(0)

    documento = fitz.open(
        stream=pdf.read(),
        filetype="pdf"
    )

    texto = ""

    for pagina in documento:

        texto += pagina.get_text()

    documento.close()

    return texto


# ======================================================
# EMPREENDIMENTO
# ======================================================

def identificar_empreendimento(texto):

    texto = normalizar(texto)

    if "JARDINS DE MARANGUAPE" in texto:

        return "Jardins de Maranguape"

    if (
        "PORTAL DO CEDRO" in texto
        or
        "PORTAL DA CEDRO" in texto
    ):

        return "Portal do Cedro"

    return None


# ======================================================
# TIPO
# ======================================================

def identificar_tipo(texto):

    texto = normalizar(texto)

    if "INSTRUMENTO PARTICULAR DE DISTRATO" in texto:

        return "DISTRATO"

    if "PROMESSA DE COMPRA E VENDA" in texto:

        return "CONTRATO"

    return "DESCONHECIDO"


# ======================================================
# QUADRA E LOTE
# ======================================================

def extrair_unidade(texto):

    texto = normalizar(texto)

    # ==================================
    # DISTRATO
    # lote n. 55 – quadra B
    # ==================================

    match = re.search(
        r"LOTE\s*N\.?\s*(\d+)\s*[–\-]\s*QUADRA\s*([A-Z])",
        texto,
        re.I
    )

    if match:

        lote = match.group(1)

        quadra = match.group(2)

        return quadra, lote

    # ==================================
    # CONTRATO
    # Quadra: G
    # Lote(s): 31
    # ==================================

    match_quadra = re.search(
        r"QUADRA\s*:?\s*([A-Z])",
        texto,
        re.I
    )

    match_lote = re.search(
        r"LOTE\(S\)\s*:?\s*(\d+)",
        texto,
        re.I
    )

    if match_quadra and match_lote:

        quadra = match_quadra.group(1)

        lote = match_lote.group(1)

        return quadra, lote

    return None, None


# ======================================================
# CLIENTE DA TABELA
# ======================================================

def buscar_cliente(
    tabela,
    empreendimento,
    quadra,
    lote
):

    quadra = str(quadra).strip()

    lote = str(int(lote))

    unidade = f"Lote{quadra}.{lote}"

    filtro = tabela[
        (
            tabela["Empreendimento"]
            .astype(str)
            .str.upper()
            .str.strip()
            ==
            empreendimento.upper()
        )
        &
        (
            tabela["Unidade"]
            .astype(str)
            .str.upper()
            .str.strip()
            ==
            unidade.upper()
        )
    ]

    if len(filtro) > 0:

        return (
            filtro.iloc[0]["Cliente"]
        )

    return None


# ======================================================
# NOME FINAL
# ======================================================

def gerar_nome(
    empreendimento,
    quadra,
    lote,
    cliente,
    tipo
):

    return (
        f"CRI PORTAL DOS CEDROS "
        f"({empreendimento}) - "
        f"LOTE {quadra} "
        f"UNIDADE {lote} - "
        f"{cliente} - "
        f"{tipo}.pdf"
    )


# ======================================================
# PROCESSAMENTO
# ======================================================

def processar_portal_cedros(
    pdfs,
    tabela
):

    nomes = []

    erros = []

    for pdf in pdfs:

        try:

            texto = extrair_texto(pdf)

            empreendimento = (
                identificar_empreendimento(
                    texto
                )
            )

            tipo = identificar_tipo(
                texto
            )

            quadra, lote = (
                extrair_unidade(
                    texto
                )
            )
        print("================================")
        print("PDF:", pdf.name)
        print("EMPREENDIMENTO:", empreendimento)
        print("TIPO:", tipo)
        print("QUADRA:", quadra)
        print("LOTE:", lote)
        
            cliente = buscar_cliente(
                tabela,
                empreendimento,
                quadra,
                lote
            )
        
        print("BUSCANDO CLIENTE")
        print("EMPREENDIMENTO:", empreendimento)
        print("UNIDADE:", unidade)
        print("RESULTADOS:", len(filtro))
        
            if (
                not empreendimento
                or not quadra
                or not lote
                or not cliente
            ):

                erros.append(
                    f"{pdf.name} - dados não encontrados"
                )

                continue

            nome = gerar_nome(
                empreendimento,
                quadra,
                lote,
                cliente,
                tipo
            )

            nomes.append(nome)

        except Exception as erro:

            erros.append(
                f"{pdf.name} - {erro}"
            )

    if erros:

        print(
            "ERROS PORTAL CEDROS:",
            erros
        )

    return nomes
