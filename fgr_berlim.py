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

    if "CESSAO DE DIREITOS" in texto:
        return "CESSAO"

    if "TERMO DE RESCISAO" in texto:
        return "DISTRATO_FORMAL"

    if "CANCELAMENTOS ADMINISTRATIVOS" in texto:
        return "DISTRATO_ADMINISTRATIVO"

    if "INSTRUMENTO PARTICULAR DE CONTRATO" in texto:
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
        r"COMO OUTORGADO\(A,S\).*?,\s*([A-Z ]+?),\s*BRASILEIRO",
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
            print("TIPO =", tipo)

            nome = None

            # ---------------------------------
            # CONTRATO
            # ---------------------------------

            if tipo == "CONTRATO":
                print("ENTROU EM CONTRATO")

                cliente = extrair_cliente_contrato(
                    texto
                )

                unidade = extrair_unidade(
                    texto
                )
                print("CLIENTE =", cliente)
                print("UNIDADE =", unidade)

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

                cliente = extrair_cliente_cessao(
                    texto
                )

                unidade = extrair_unidade(
                    texto
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

                cliente = extrair_cliente_distrato(
                    texto
                )

                unidade = extrair_unidade(
                    texto
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

                linha = localizar_cliente_planilha(
                    texto,
                    tabela
                )

                if linha is not None:

                    nome = gerar_nome(
                        linha["Unidade"],
                        linha["Cliente"],
                        "DISTRATO"
                    )

            if not nome:

                nome = (
                    f"NAO_IDENTIFICADO - "
                    f"{pdf.name}"
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
