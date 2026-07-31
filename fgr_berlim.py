import fitz
import re
import tempfile
import unicodedata


PREFIXO = "CRI FGR (CJ)"


# =====================================================
# TEXTO
# =====================================================

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

    doc.close()

    return texto.upper()


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
# IDENTIFICA DOCUMENTO
# =====================================================

def identificar_tipo_documento(texto):

    texto = normalizar(texto)

    # DISTRATOS

    if "TERMO DE RESCISAO" in texto:
        return "DISTRATO_FORMAL"

    if "CANCELAMENTOS ADMINISTRATIVOS" in texto:
        return "DISTRATO_ADMINISTRATIVO"

    # CONTRATO

    if (
        "CONTRATO DE COMPRA E VENDA DE IMOVEL" in texto
        or
        "INSTRUMENTO PARTICULAR DE CONTRATO" in texto
    ):
        return "CONTRATO"

    return "DESCONHECIDO"

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

    return (
        f"{int(quadra.group(1)):02d}"
        f"-"
        f"{int(lote.group(1)):02d}"
    )


# =====================================================
# CLIENTE CONTRATO
# =====================================================

def extrair_cliente_contrato(texto):

    texto = normalizar(texto)

    match = re.search(
        r"COMPRADOR\(A,ES\).*?FIDUCIANTE\(S\),\s*([A-Z ]+?)\s*,\s*BRASILEIRO",
        texto,
        re.S
    )

    if match:

        return match.group(1).strip()

    return None

# =====================================================
# CLIENTE CESSÃO
# =====================================================

def extrair_cliente_cessao(texto):

    texto = normalizar(texto)

    match = re.search(
        r"CESSIONARIO.*?([A-Z ]+?),\s*BRASILEIRO",
        texto,
        re.S
    )

    if match:

        return match.group(1).strip()

    return None


# =====================================================
# CLIENTE DISTRATO FORMAL
# =====================================================

def extrair_cliente_distrato(texto):

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
# LOCALIZA CLIENTE NA PLANILHA
# =====================================================

def localizar_cliente_planilha(
    texto,
    tabela
):

    texto = normalizar(texto)

    for _, linha in tabela.iterrows():

        cliente = normalizar(
            linha["Cliente"]
        )

        if cliente in texto:

            return linha

    return None

def localizar_cliente_por_unidade(
    unidade,
    cliente_pdf,
    tabela
):

    candidatos = tabela[
        tabela["Unidade"] \
        .astype(str) \
        .str.replace(" ", "") \
        .str.upper()
        ==
        str(unidade)
        .strip()
        .upper()
    ]

    if len(candidatos) == 0:

        return None

    if len(candidatos) == 1:

        return str(
            candidatos.iloc[0]["Cliente"]
        ).strip()

    cliente_pdf = normalizar(
        cliente_pdf or ""
    )

    for _, linha in candidatos.iterrows():

        cliente_tabela = normalizar(
            linha["Cliente"]
        )

        if cliente_tabela in cliente_pdf:

            return str(
                linha["Cliente"]
            ).strip()

        if cliente_pdf in cliente_tabela:

            return str(
                linha["Cliente"]
            ).strip()

    return "CLIENTE DUPLICADO - VALIDAR"
    
def localizar_cliente_no_texto(
    texto,
    tabela
):

    texto = normalizar(texto)

    for _, linha in tabela.iterrows():

        cliente = normalizar(
            linha["Cliente"]
        )

        if cliente in texto:

            return str(
                linha["Cliente"]
            ).strip()

    return None

# =====================================================
# GERA NOME
# =====================================================

def gerar_nome(
    unidade,
    cliente,
    tipo
):

    cliente = str(cliente).strip()

    unidade = str(unidade).strip()

    return (
        f"{PREFIXO} - "
        f"UNIDADE {unidade} - "
        f"{cliente} - "
        f"{tipo}.pdf"
    )


# =====================================================
# PROCESSAMENTO PRINCIPAL
# =====================================================

def processar_fgr_berlim(
    pdfs,
    tabela
):

    nomes = []

    for pdf in pdfs:

        try:

            texto = extrair_texto(
                pdf
            )
            print("=" * 50)
            print(pdf.name)
            print("=" * 50)
            print(texto[:5000])
            print("=" * 50)
            tipo = identificar_tipo_documento(
                texto
            )
            print("TIPO FINAL =", tipo)

            nome = None

            # ---------------------------------
            # CONTRATO
            # ---------------------------------

            if tipo == "CONTRATO":
                print("ENTROU EM CONTRATO")

                unidade = extrair_unidade(
                    texto
                )

                cliente_pdf = extrair_cliente_contrato(
                    texto
                )

                cliente = localizar_cliente_por_unidade(
                    unidade,
                    cliente_pdf,
                    tabela
                )

                if cliente and unidade:

                    nome = gerar_nome(
                        unidade,
                        cliente,
                        "CONTRATO DE COMPRA E VENDA"
                    )

            # ---------------------------------
            # CESSÃO
            # ---------------------------------

            elif tipo == "CESSAO":

                unidade = extrair_unidade(
                    texto
                )

                cliente_pdf = extrair_cliente_cessao(
                    texto
                )

                cliente = localizar_cliente_por_unidade(
                    unidade,
                    cliente_pdf,
                    tabela
                )

                if cliente and unidade:

                    nome = gerar_nome(
                        unidade,
                        cliente,
                        "CESSAO DE DIREITOS"
                    )

            # ---------------------------------
            # DISTRATO FORMAL
            # ---------------------------------

            elif tipo == "DISTRATO_FORMAL":

                unidade = extrair_unidade(
                    texto
                )

                cliente_pdf = extrair_cliente_distrato(
                    texto
                )

                cliente = localizar_cliente_por_unidade(
                    unidade,
                    cliente_pdf,
                    tabela
                )

                if cliente and unidade:

                    nome = gerar_nome(
                        unidade,
                        cliente,
                        "DISTRATO"
                    )

            # ---------------------------------
            # DISTRATO ADMINISTRATIVO
            # ---------------------------------

            elif tipo == "DISTRATO_ADMINISTRATIVO":

                cliente = localizar_cliente_no_texto(
                    texto,
                    tabela
                )

                if cliente:

                    linha = tabela[
                        tabela["Cliente"]
                        .astype(str)
                        .str.strip()
                        ==
                        cliente
                    ].iloc[0]

                    nome = gerar_nome(
                        linha["Unidade"],
                        cliente,
                        "DISTRATO"
                    )

            if not nome:

                nome = (
                    f"DEBUG | "
                    f"TIPO={tipo}"
                )

            nomes.append(
                nome
            )

        except Exception as erro:

            nomes.append(
                f"ERRO - {pdf.name}"
            )

            print(
                f"Erro ao processar {pdf.name}:",
                erro
            )

    return nomes
