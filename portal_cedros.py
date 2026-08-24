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
# EXTRAÇÃO DE TEXTO
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
        return "JARDINS DE MARANGUAPE"

    if (
        "PORTAL DO CEDRO" in texto
        or
        "PORTAL DA CEDRO" in texto
    ):
        return "PORTAL DO CEDRO"

    return None


# ======================================================
# TIPO DOCUMENTO
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

    # --------------------------------------------------
    # DISTRATO
    # lote n. 55 – quadra B
    # lote n. 34 – quadra N
    # --------------------------------------------------

    match = re.search(
        r"LOTE\s*N\.?\s*(\d+)\s*[–\-]\s*QUADRA\s*([A-Z])",
        texto,
        re.I
    )

    if match:

        lote = match.group(1)
        quadra = match.group(2)

        return quadra, lote

    # --------------------------------------------------
    # CONTRATO
    # Quadra: G
    # Lote(s): 31
    # --------------------------------------------------

    match_quadra = re.search(
        r"QUADRA\s*:[A-Z?\s*(])",
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
# BUSCA CLIENTE PLANILHA
# ======================================================

def buscar_cliente(
    df,
    empreendimento,
    quadra,
    lote
):

    if empreendimento is None:
        return None

    filtro = df[
        (
            df["EMPREENDIMENTO"]
            .astype(str)
            .str.upper()
            ==
            empreendimento
        )
        &
        (
            df["QUADRA"]
            .astype(str)
            .str.upper()
            ==
            str(quadra).upper()
        )
        &
        (
            df["LOTE"]
            .astype(str)
            .str.strip()
            ==
            str(lote).strip()
        )
    ]

    if len(filtro):

        return str(
            filtro.iloc[0]["CLIENTE"]
        ).strip()

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
# PROCESSADOR PRINCIPAL
# ======================================================

def processar_portal_cedros(
    arquivos_pdf,
    df_portal_cedros
):

    arquivos_renomeados = []

    ignorados = []

    for pdf in arquivos_pdf:

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

            cliente = buscar_cliente(
                df_portal_cedros,
                empreendimento,
                quadra,
                lote
            )

            print(
                f"EMPREENDIMENTO={empreendimento}"
            )

            print(
                f"TIPO={tipo}"
            )

            print(
                f"QUADRA={quadra}"
            )

            print(
                f"LOTE={lote}"
            )

            print(
                f"CLIENTE={cliente}"
            )

            if (
                empreendimento is None
                or quadra is None
                or lote is None
                or cliente is None
            ):

                ignorados.append(
                    f"DADOS NAO LOCALIZADOS - {pdf.name}"
                )

                continue

            novo_nome = gerar_nome(
                empreendimento,
                quadra,
                lote,
                cliente,
                tipo
            )

            arquivos_renomeados.append(
                (
                    pdf,
                    novo_nome
                )
            )

        except Exception as erro:

            ignorados.append(
                f"{pdf.name} - {erro}"
            )

    return (
        arquivos_renomeados,
        ignorados
    )
