import re
import unicodedata


PREFIXO = "CRI FGR (CJ)"


# =====================================================
# UTIL
# =====================================================

def normalizar(texto):

    texto = str(texto).upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        c
        for c in texto
        if not unicodedata.combining(c)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# =====================================================
# PLANILHA
# =====================================================

def localizar_cliente_planilha(
    texto,
    df
):

    texto = normalizar(texto)

    for _, row in df.iterrows():

        cliente = normalizar(
            row["Cliente"]
        )

        if cliente in texto:

            return row

    return None


# =====================================================
# TIPO
# =====================================================

def identificar_tipo(texto):

    texto = normalizar(texto)

    if "CESSAO DE DIREITOS" in texto:
        return "CESSAO"

    if "TERMO DE RESCISAO" in texto:
        return "DISTRATO"

    if "CANCELAMENTOS ADMINISTRATIVOS" in texto:
        return "DISTRATO"

    if (
        "INSTRUMENTO PARTICULAR DE CONTRATO"
        in texto
    ):
        return "CONTRATO"

    return None


# =====================================================
# UNIDADE
# =====================================================

def extrair_unidade(texto):

    texto = normalizar(texto)

    quadra = re.search(
        r"QUADRA[: ]+(\d+)",
        texto
    )

    lote = re.search(
        r"LOTE[: ]+(\d+)",
        texto
    )

    if not quadra or not lote:
        return None

    quadra = int(
        quadra.group(1)
    )

    lote = int(
        lote.group(1)
    )

    return f"{quadra:02d}-{lote:02d}"


# =====================================================
# CONTRATO
# =====================================================

def cliente_contrato(texto):

    texto = normalizar(texto)

    match = re.search(
        r"COMPRADOR\(A,ES\).*?([A-Z ]+?), BRASILEIRO",
        texto,
        re.S
    )

    if match:

        return match.group(1).strip()

    return None


# =====================================================
# CESSAO
# =====================================================

def cliente_cessao(texto):

    texto = normalizar(texto)

    partes = re.findall(
        r"([A-Z ]+?), BRASILEIRO\(A\)",
        texto
    )

    if len(partes) >= 2:

        return partes[1].strip()

    return None


# =====================================================
# DISTRATO FORMAL
# =====================================================

def cliente_distrato(texto):

    texto = normalizar(texto)

    match = re.search(
        r"COMO SEGUNDO\(A,S\).*?:\s*([A-Z ]+?),\s*BRASILEIRO",
        texto,
        re.S
    )

    if match:

        return match.group(1).strip()

    return None


# =====================================================
# MONTA NOME
# =====================================================

def montar_nome(
    unidade,
    cliente,
    tipo
):

    return (
        f"{PREFIXO} - "
        f"UNIDADE {unidade} - "
        f"{cliente} - "
        f"{tipo}.pdf"
    )


# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================

def processar_fgr_berlim(
    texto,
    df_unidades
):

    texto_norm = normalizar(
        texto
    )

    tipo_doc = identificar_tipo(
        texto_norm
    )

    if not tipo_doc:
        return None


    # ---------------------------------
    # CONTRATO
    # ---------------------------------

    if tipo_doc == "CONTRATO":

        cliente = cliente_contrato(
            texto
        )

        unidade = extrair_unidade(
            texto
        )

        if not cliente or not unidade:
            return None

        return montar_nome(
            unidade,
            cliente,
            "CONTRATO DE COMPRA E VENDA"
        )


    # ---------------------------------
    # CESSAO
    # ---------------------------------

    if tipo_doc == "CESSAO":

        cliente = cliente_cessao(
            texto
        )

        unidade = extrair_unidade(
            texto
        )

        if not cliente or not unidade:
            return None

        return montar_nome(
            unidade,
            cliente,
            "CESSAO DE DIREITOS"
        )


    # ---------------------------------
    # DISTRATO FORMAL
    # ---------------------------------

    if (
        "TERMO DE RESCISAO"
        in texto_norm
    ):

        cliente = cliente_distrato(
            texto
        )

        unidade = extrair_unidade(
            texto
        )

        if not cliente or not unidade:
            return None

        return montar_nome(
            unidade,
            cliente,
            "DISTRATO"
        )


    # ---------------------------------
    # DISTRATO ADMINISTRATIVO
    # ---------------------------------

    linha = localizar_cliente_planilha(
        texto,
        df_unidades
    )

    if linha is None:
        return None

    cliente = linha[
        "Cliente"
    ]

    unidade = linha[
        "Unidade"
    ]

    return montar_nome(
        unidade,
        cliente,
        "DISTRATO"
    )
