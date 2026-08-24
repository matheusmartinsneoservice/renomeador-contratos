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
        or
        "PORTAL CEDRO" in texto
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
        r"QUADRA:\s*([A-Z])",
        texto,
        re.I
    )

    match_lote = re.search(
        r"LOTE\(S\):\s*(\d+)",
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

    if (
        empreendimento is None
        or quadra is None
        or lote is None
    ):
        return None

    quadra = str(quadra).strip()

    lote = str(lote).strip()

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
    print("RESULTADOS:", len(filtro))
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

    arquivos_ignorados = []
    
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
        
            cliente = buscar_cliente(
                tabela,
                empreendimento,
                quadra,
                lote
            )
            
            if (
                not empreendimento
                or not quadra
                or not lote
                or not cliente
            ):

                erros.append(
                    f"{pdf.name} - "
                    f"EMP={empreendimento} | "
                    f"Q={quadra} | "
                    f"L={lote} | "
                    f"CLI={cliente}"
                )

                arquivos_ignorados.append(
                    {
                        "nome": pdf.name,
                        "pdf_bytes": pdf.getvalue()
                    }
                )

                continue
            nome = (
                f"TESTE | "
                f"EMP={empreendimento} | "
                f"Q={quadra} | "
                f"L={lote} | "
                f"CLI={cliente}"
            )

            nomes.append(nome)

        except Exception as erro:

            erros.append(
                f"{pdf.name} - {erro}"
            )

            arquivos_ignorados.append(
                {
                    "nome": pdf.name,
                    "pdf_bytes": pdf.getvalue()
                }
            )

    print("================================")
    print("TOTAL PDFs:", len(pdfs))
    print("RENOMEADOS:", len(nomes))
    print("ERROS:", len(erros))

    for erro in erros:
        print(erro)
        
    return nomes, erros, arquivos_ignorados
