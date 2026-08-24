import fitz
import re
import io

import pytesseract
from PIL import Image


# ======================================================
# NORMALIZAÇÃO
# ======================================================

def normalizar(texto):

    if texto is None:
        return ""

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

    print("TOTAL PAGINAS:", len(documento))

    texto = ""

    # =====================================
    # LEITURA NORMAL DE TODAS AS PAGINAS
    # =====================================

    for numero, pagina in enumerate(documento):

        texto_pagina = pagina.get_text("text")

        print("=" * 50)
        print("PAGINA:", numero + 1)
        print("CARACTERES:", len(texto_pagina))

        texto += texto_pagina
        texto += "\n"

    # =====================================
    # OCR AUTOMÁTICO
    # =====================================

    if len(texto.strip()) < 500:

        print("=" * 50)
        print("PDF COM POUCO TEXTO")
        print("INICIANDO OCR")

        texto = ""

        for numero, pagina in enumerate(documento):

            pix = pagina.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )

            imagem = Image.open(
                io.BytesIO(
                    pix.tobytes("png")
                )
            )

            texto_pagina = pytesseract.image_to_string(
                imagem,
                lang="por"
            )

            texto += texto_pagina
            texto += "\n"

    documento.close()

    print("TOTAL CARACTERES:", len(texto))

    return texto


# ======================================================
# EMPREENDIMENTO
# ======================================================

def identificar_empreendimento(texto):

    texto = normalizar(texto)

    empreendimentos = {

        "JARDINS DE MARANGUAPE":
            "Jardins de Maranguape",

        "PORTAL DOS CEDROS":
            "Portal do Cedro",

        "PORTAL DO CEDRO":
            "Portal do Cedro",

        "PORTAL DA CEDRO":
            "Portal do Cedro",

        "PORTAL CEDRO":
            "Portal do Cedro",
    }

    for chave, valor in empreendimentos.items():

        if chave in texto:

            return valor

    print("=" * 50)
    print("NAO IDENTIFICOU EMPREENDIMENTO")
    print(texto[:5000])

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

    padroes = [

        # DISTRATO
        r"LOTE\s*N\.?\s*(\d+)\s*[–\-]\s*QUADRA\s*([A-Z])",

        # CONTRATOS
        r"QUADRA:\s*([A-Z]).{0,300}?LOTE\(S\):\s*(\d+)",

        r"QUADRA\s*([A-Z]).{0,300}?LOTE\s*(\d+)",

        r"LOTE\s*(\d+).{0,300}?QUADRA\s*([A-Z])",

        r"UNIDADE\s*([A-Z])\.?(\d+)",

        r"LOTE([A-Z])\.?(\d+)"
    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.I | re.S
        )

        if not match:
            continue

        grupo1 = match.group(1)
        grupo2 = match.group(2)

        if grupo1.isdigit():

            lote = grupo1
            quadra = grupo2

        else:

            quadra = grupo1
            lote = grupo2

        print(
            f"QUADRA={quadra} "
            f"LOTE={lote}"
        )

        return quadra, lote

    print("=" * 50)
    print("NAO IDENTIFICOU UNIDADE")
    print(texto[:5000])

    return None, None


# ======================================================
# CLIENTE
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

    try:

        lote = f"{int(lote):02d}"

    except:

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

        return filtro.iloc[0]["Cliente"]

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

            # ==================================
            # FALLBACK PELO NOME DO ARQUIVO
            # ==================================

            if not empreendimento:

                nome_pdf = pdf.name.upper()

                if (
                    "JARDINS DE MARANGUAPE"
                    in nome_pdf
                ):

                    empreendimento = (
                        "Jardins de Maranguape"
                    )

                    print(
                        "EMPREENDIMENTO EXTRAIDO DO NOME"
                    )

                elif (
                    "PORTAL DOS CEDROS"
                    in nome_pdf
                    or
                    "PORTAL DO CEDRO"
                    in nome_pdf
                ):

                    empreendimento = (
                        "Portal do Cedro"
                    )

                    print(
                        "EMPREENDIMENTO EXTRAIDO DO NOME"
                    )

            if not quadra or not lote:

                nome_pdf = pdf.name.upper()

                match = re.search(
                    r"LOTE\s+([A-Z])\s+UNIDADE\s+(\d+)",
                    nome_pdf
                )

                if match:

                    quadra = (
                        match.group(1)
                    )

                    lote = (
                        match.group(2)
                    )

                    print(
                        "UNIDADE EXTRAIDA DO NOME:",
                        quadra,
                        lote
                    )

            cliente = buscar_cliente(
                tabela,
                empreendimento,
                quadra,
                lote
            )

            print("=" * 50)
            print(
                "EMPREENDIMENTO:",
                empreendimento
            )
            print(
                "QUADRA:",
                quadra
            )
            print(
                "LOTE:",
                lote
            )
            print(
                "CLIENTE:",
                cliente
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

            arquivos_ignorados.append(
                {
                    "nome": pdf.name,
                    "pdf_bytes": pdf.getvalue()
                }
            )

    print("=" * 50)
    print("TOTAL PDFs:", len(pdfs))
    print("RENOMEADOS:", len(nomes))
    print("ERROS:", len(erros))

    for erro in erros:

        print(erro)

    return (
        nomes,
        erros,
        arquivos_ignorados
    )
