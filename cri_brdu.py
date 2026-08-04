import re
import fitz


# ==========================================
# UTILITÁRIOS
# ==========================================

def normalizar(texto):

    texto = texto.upper()

    substituicoes = {
        "Á": "A",
        "À": "A",
        "Â": "A",
        "Ã": "A",
        "É": "E",
        "Ê": "E",
        "Í": "I",
        "Ó": "O",
        "Ô": "O",
        "Õ": "O",
        "Ú": "U",
        "Ç": "C",
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(
            antigo,
            novo
        )

    return texto


def extrair_texto_pdf(pdf_file):

    texto = ""

    pdf = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    for pagina in pdf:
        texto += pagina.get_text()

    pdf.close()

    return texto


# ==========================================
# EMPREENDIMENTO
# ==========================================

def identificar_empreendimento(texto):

    texto = normalizar(texto)

    if "IMPERATRIZ 03" in texto:
        return "IMPERATRIZ 03"

    if "IMPERATRIZ 04" in texto:
        return "IMPERATRIZ 04"

    if "RIO VERMELHO" in texto:
        return "RIO VERMELHO"

    if "LUZIANIA" in texto:
        return "SPE LUZIANIA"

    if "ORLANDO" in texto:
        return "SPE ORLANDO"

    if "ZURIQUE" in texto:
        return "SPE ZURIQUE"

    return "EMPREENDIMENTO"


# ==========================================
# TIPO DOCUMENTO
# ==========================================

def identificar_tipo_documento(texto):

    texto = normalizar(texto)

    if (
        "NOTIFICACAO EXTRAJUDICIAL DE DISTRATO"
        in texto
    ):
        return "DISTRATO"

    if (
        "COMPROMISSO DE COMPRA E VENDA"
        in texto
    ):
        return "CONTRATO"

    return "DESCONHECIDO"


# ==========================================
# UNIDADE
# ==========================================

def extrair_unidade(texto):

    texto = normalizar(texto)

    # DISTRATO
    match = re.search(
        r"QD\s*(\d+)\s*LT\s*(\d+)",
        texto
    )

    if match:

        quadra = match.group(1).zfill(2)

        lote = match.group(2).zfill(2)

        return quadra, lote

    # CONTRATO
    match = re.search(
        r"QUADRA\s*:?\s*(\d+).*?LOTE.*?(\d+)",
        texto,
        re.S
    )

    if match:

        quadra = match.group(1).zfill(2)

        lote = match.group(2).zfill(2)

        return quadra, lote

    return None, None


# ==========================================
# CLIENTE CONTRATO
# ==========================================

def extrair_cliente_contrato(texto):

    texto = normalizar(texto)

    match = re.search(
        r"DO\(S\)\s+PROMITENTE\(S\)\s+COMPRADOR\(ES\)\:(.*?)BRASILEIR",
        texto,
        re.S
    )

    if match:

        cliente = match.group(1)

        cliente = re.sub(
            r"[^A-Z ]",
            " ",
            cliente
        )

        cliente = " ".join(
            cliente.split()
        )

        return cliente

    return None


# ==========================================
# CLIENTE DISTRATO
# ==========================================

def extrair_cliente_distrato(texto):

    texto = normalizar(texto)

    match = re.search(
        r"\nA\s+([A-Z\s]+?)\s+END",
        texto
    )

    if match:

        cliente = match.group(1)

        cliente = " ".join(
            cliente.split()
        )

        return cliente

    return None


# ==========================================
# CLIENTE GERAL
# ==========================================

def extrair_cliente(texto, tipo):

    if tipo == "CONTRATO":
        return extrair_cliente_contrato(texto)

    if tipo == "DISTRATO":
        return extrair_cliente_distrato(texto)

    return None


# ==========================================
# NOME FINAL
# ==========================================

def gerar_nome(
    empreendimento,
    quadra,
    lote,
    cliente,
    tipo
):

    return (
        f"CRI BRDU ({empreendimento}) - "
        f"QUADRA {quadra} "
        f"LOTE {lote} - "
        f"{cliente} - "
        f"{tipo}.pdf"
    )


# ==========================================
# PROCESSAMENTO
# ==========================================

def processar_cri_brdu(arquivos_pdf):

    arquivos_renomeados = []

    ignorados = []

    for pdf in arquivos_pdf:

        try:

            texto = extrair_texto_pdf(pdf)

            tipo = identificar_tipo_documento(
                texto
            )

            empreendimento = (
                identificar_empreendimento(
                    texto
                )
            )

            quadra, lote = (
                extrair_unidade(
                    texto
                )
            )

            cliente = extrair_cliente(
                texto,
                tipo
            )

            print(
                f"TIPO={tipo}"
            )

            print(
                f"EMPREENDIMENTO={empreendimento}"
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
                tipo == "DESCONHECIDO"
                or not quadra
                or not lote
                or not cliente
            ):

                ignorados.append(
                    f"IGNORADO - {pdf.name}"
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
                f"ERRO - {pdf.name} - {erro}"
            )

    return (
        arquivos_renomeados,
        ignorados
    )
