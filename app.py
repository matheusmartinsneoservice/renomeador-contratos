import streamlit as st
import pandas as pd
import base64
import streamlit.components.v1 as components
import io
import zipfile

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:

    st.title("Acesso Restrito")

    email = st.text_input(
        "E-mail corporativo"
    )

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        if not email.lower().endswith(
            "@neoservice.com.br"
        ):

            st.error(
                "Utilize um e-mail corporativo Neo Service."
            )

        elif senha == st.secrets["APP_PASSWORD"]:

            st.session_state["autenticado"] = True

            st.session_state["email"] = email

            st.rerun()

        else:

            st.error(
                "Senha inválida."
            )

    st.stop()
    
from tekoa import processar_tekoa
from d_urbanismo import processar_d_urbanismo
from marechal import processar_marechal
from gran_paradiso import processar_gran_paradiso
from innovar import processar_innovar
from fgr_berlim import processar_fgr_berlim
from cri_brdu import processar_cri_brdu
import gran_paradiso

# =====================================
# CONFIGURAÇÃO
# =====================================


# =====================================
# ESTADO
# =====================================

if "passo" not in st.session_state:
    st.session_state["passo"] = 1

# =====================================
# RELATÓRIOS
# =====================================

RELATORIOS = {
        "CRI BRDU | 4ª EMISSÃO": {

        "empreendimentos": [
            "IMPERATRIZ 03",
            "IMPERATRIZ 04",
            "RIO VERMELHO",
            "SPE LUZIÂNIA",
            "SPE ORLANDO",
            "SPE ZURIQUE"
        ],
            
        "tipo": "QUADRA_LOTE",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgAv9VZfe5pZQq6kH08BOpc7Abs-MrBN6L8jtK-028bm6WU?e=6Rer7I"
    },
    
    "CRI FGR BERLIM": {

        "empreendimentos": [
            "JARDINS BERLIM"
        ],

        "tipo": "UNIDADE",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgB3mlBT2Ga-S5b2vQ5x9fVKAX8ZnNPVcYWJQw4Q5d2cKE4?e=FmjjcG"

    },
    
    "CRI INNOVAR": {

        "empreendimentos": [
            "ARES BAIRRO PARQUE PF",
            "CONDOMÍNIO RANCHO LM FAZENDA RESORT",
            "RESIDENCIAL DON ANTONIO",
            "RESIDENCIAL MORADA DAS MISSÕES",
            "RESIDENCIAL NOVA RIO GRANDE",
            "SCP ARES BAIRRO PARQUE"
        ],

        "tipo": "QUADRA_LOTE",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgDAYb7tgdQWRLtJJRyW_bqsARtgZpVMX0LrYNu1lWbokKk?e=ko4oO0"
    },

    "CRI GRAN PARADISO": {

        "empreendimentos": [
            "GP"
        ],

        "tipo": "UNIDADE_TIPO_LETRA",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgBsFpO15Jr6TIVPunSvVQ5HASF1TiORQvJ3gArXrUjwF_k?e=WoQhGg"
    },

    "CRI MARECHAL": {

        "empreendimentos": [],

        "tipo": "QUADRA_LOTE",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgCgzB4-b_pmRagVWCWdnd7wATkimcpzDpoIp0ogmOmAcL4?e=NfWdiy"
    },

    "CRI BAUTEN TEKOÁ": {

        "empreendimentos": [
            "TEKOÁ"
        ],

        "tipo": "UNIDADE",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgBroGJ7jWL1QYTeYv19DPwiASdF-Ek_tAnwyw5L_vqMWfs?e=Ujt3Vf"
    },

    "CRI PORTAL DO CEDROS": {

        "empreendimentos": [
            "PORTAL DO CEDRO",
            "JARDINS DE MARANGUAPE"
        ],

        "tipo": "QUADRA_LOTE",

        "sharepoint":
        "https://empresa.sharepoint.com/.../PORTAL_CEDRO"
    },

    "CRI SER RIO": {

        "empreendimentos": [
            "LOTEAMENTO RESIDENCIAL ONIX"
        ],

        "tipo": "QUADRA_LOTE",

        "sharepoint":
        "https://empresa.sharepoint.com/.../SER_RIO"
    },

    "CRI D URBANISMO": {

        "empreendimentos": [
            "BOSQUE DO CATU",
            "CAMINHOS DA SERRA",
            "COLINAS"
        ],

        "tipo": "EMPREENDIMENTO_UNIDADE",

        "sharepoint":
        "https://arquivosneoservice.sharepoint.com/:f:/g/IgAetQpxegqlTZSreDDDDesLAQVOnDa4rJZSl9zd3_blosQ?e=zp0LgA"
    }

}

# =====================================
# PDF VIEWER
# =====================================

def exibir_pdf(uploaded_file):

    pdf_bytes = uploaded_file.getvalue()

    with zipfile.ZipFile(
        zip_buffer,
        "r"
    ) as teste_zip:

        st.write(
            teste_zip.namelist()
        )

    st.download_button(
        label="📥 Abrir PDF",
        data=pdf_bytes,
        file_name=uploaded_file.name,
        mime="application/pdf"
    )

    try:

        st.write(
            f"PDF selecionado: {nome_renomeado}"
        )

    except Exception:

        st.warning(
            "Não foi possível exibir o PDF."
        )

# =====================================
# PASSO 1
# =====================================

def tela_relatorio():

    st.image(
        "Logo_neoservice.png",
        width=250
    )

    st.title(
        "Renomeação de contratos"
    )

    st.progress(1 / 7)

    st.subheader(
        "Passo 1 de 7 - Escolher Relatório"
    )

    pesquisa = st.text_input(
        "Pesquisar relatório"
    )

    filtrados = [
        r
        for r in RELATORIOS
        if pesquisa.lower()
        in r.lower()
    ]

    relatorio = st.selectbox(
        "Relatório",
        filtrados
    )

    if st.button("Próximo"):

        st.session_state["relatorio"] = relatorio

        # limpa a tabela ao trocar de relatório

        if "tabela" in st.session_state:
            del st.session_state["tabela"]

        st.session_state["passo"] = 2

        st.rerun()

# =====================================
# PASSO 2
# =====================================

def tela_relacao():

    st.progress(2 / 7)

    st.subheader(
        "Passo 2 de 7 - Relação de Contratos"
    )

    relatorio = st.session_state[
        "relatorio"
    ]

    st.info(
        f"Relatório selecionado: {relatorio}"
    )

    # EXEMPLO

    if relatorio == "CRI INNOVAR":

        st.info(
            """
    Exemplo de preenchimento:

    Empreendimento: RESIDENCIAL NOVA RIO GRANDE
    Quadra: 17
    Lote: 013
    Cliente: MAURICIO BIAVASCHI SCHMIDT
    """
        )

    elif relatorio == "CRI GRAN PARADISO":

        st.info(
            """
    Exemplo de preenchimento:

    Unidade: 055
    Tipo: APTO DIAMANTE
    Letra: G
    Cliente: MARCELO CESAR GONÇALVES DA SILVA
    """
        )

    elif relatorio == "CRI MARECHAL":

        st.info(
            """
    Exemplo de preenchimento:

    Quadra: 10
    Lote: 012
    Cliente: CLEITON DOS SANTOS BORGES DA CONCEIÇÃO
    """
        )
    
    elif relatorio == "CRI D URBANISMO":

        st.info(
            """
    Exemplo de preenchimento:

    Empreendimento: COLINAS
    Unidade: E.4
    Cliente: JOSE SOARES VIANA
    """
        )
        
    elif relatorio == "CRI FGR BERLIM":

        st.info(
                """
    Exemplo de preenchimento:

    Unidade: 01-06
    Cliente: BARBARA ALENCAR COELHO
    """
        )
            
    tipo = RELATORIOS[relatorio]["tipo"]

    if tipo == "UNIDADE":
    
        colunas = [
            "Unidade",
            "Cliente"
        ]

    elif tipo == "EMPREENDIMENTO_UNIDADE":

        colunas = [
            "Empreendimento",
            "Unidade",
            "Cliente"
        ]
    elif tipo == "UNIDADE_TIPO_LETRA":

        colunas = [
            "Unidade",
            "Tipo",
            "Letra",
            "Cliente"
        ]

    else:

        colunas = [
            "Empreendimento",
            "Quadra",
            "Lote",
            "Cliente"
        ]

    if "tabela" not in st.session_state:

        st.session_state["tabela"] = pd.DataFrame(
            "",
            index=range(20),
            columns=colunas
        )

    tabela = st.data_editor(
        st.session_state["tabela"],
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        height=500
    )

    st.session_state["tabela"] = tabela

    c1, c2 = st.columns(2)

    with c1:

        if st.button("Voltar"):

            st.session_state["passo"] = 1

            st.rerun()

    with c2:

        if st.button("Próximo"):

            st.session_state["tabela"] = tabela.replace(
                "",
                pd.NA
            ).dropna(
                how="all"
            )

            st.session_state["passo"] = 3

            st.rerun()

# =====================================
# PASSO 3
# =====================================

def tela_upload():

    st.progress(3 / 7)

    st.subheader(
        "Passo 3 de 7 - Upload PDFs"
    )

    pdfs = st.file_uploader(
        "Selecionar contratos",
        type=["pdf"],
        accept_multiple_files=True
    )

    if pdfs:

        st.session_state["pdfs"] = pdfs

        st.success(
            f"{len(pdfs)} PDF(s) carregado(s)"
        )

        for pdf in pdfs:

            st.write(
                f"📄 {pdf.name}"
            )

    c1, c2 = st.columns(2)

    with c1:

        if st.button("Voltar"):

            st.session_state["passo"] = 2
            st.rerun()

    with c2:

        if st.button("Próximo"):

            st.session_state["passo"] = 4
            st.rerun()

# =====================================
# PASSO 4
# =====================================

def tela_renomeacao():

    st.progress(4 / 7)

    st.subheader(
        "Passo 4 de 7 - Renomeação"
    )

    relatorio = st.session_state.get(
        "relatorio"
    )

    tabela = st.session_state.get(
        "tabela"
    )

    tabela = tabela.copy()

    for coluna in tabela.columns:

        tabela[coluna] = (
            tabela[coluna]
            .astype(str)
            .str.replace("\\n", " ", regex=False)
            .str.replace("\\r", " ", regex=False)
            .str.replace("\n", " ", regex=False)
            .str.replace("\r", " ", regex=False)
            .str.strip()
        )

    pdfs = st.session_state.get(
        "pdfs",
        []
    )

    st.info(
        f"Relatório selecionado: {relatorio}"
    )

    st.write(
        f"Registros cadastrados: {len(tabela)}"
    )

    st.write(
        f"PDF(s) carregado(s): {len(pdfs)}"
    )

    if st.button(
        "Iniciar Renomeação"
    ):

        barra = st.progress(0)

        nomes = []

        contratos_processados = []

        if relatorio == "CRI BAUTEN TEKOÁ":

            nomes = processar_tekoa(
                pdfs,
                tabela
            )

        elif relatorio == "CRI D URBANISMO":

            nomes = processar_d_urbanismo(
                pdfs,
                tabela
            )

        elif relatorio == "CRI MARECHAL":

            nomes = processar_marechal(
                pdfs,
                tabela
            )

        elif relatorio == "CRI GRAN PARADISO":

            nomes = processar_gran_paradiso(
                pdfs,
                tabela
            )

        elif relatorio == "CRI INNOVAR":

            nomes = processar_innovar(
                pdfs,
                tabela
            )
            
        elif relatorio == "CRI FGR BERLIM":

            nomes = processar_fgr_berlim(
                pdfs,
                tabela
            )
            
        elif empreendimento == "CRI BRDU":

            arquivos_renomeados, ignorados = (
                processar_cri_brdu(
                    arquivos_pdf,
                    tabela
                )
            )
                
        for pdf, nome in zip(
            pdfs,
            nomes
        ):

            contratos_processados.append(
                {
                    "pdf_bytes": pdf.getvalue(),
                    "nome": nome
                }
            )

        barra.progress(100)

        st.session_state[
            "contratos_processados"
        ] = contratos_processados

        st.session_state[
            "arquivos_renomeados"
        ] = nomes

        st.session_state[
            "processados"
        ] = len(nomes)

        st.session_state[
            "ignorados"
        ] = 0

        st.session_state[
            "passo"
        ] = 5

        st.rerun()

# =====================================
# PASSO 5
# =====================================

def tela_resultado():

    st.progress(5 / 7)

    st.subheader(
        "Passo 5 de 7 - Arquivos Renomeados"
    )

    st.success(
        "Processamento concluído"
    )

    arquivos = st.session_state.get(
        "arquivos_renomeados",
        []
    )

    for arquivo in arquivos:

        st.write(
            f"✅ {arquivo}"
        )

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"Processados: {st.session_state.get('processados',0)}"
        )

    with col2:

        st.info(
            f"Ignorados: {st.session_state.get('ignorados',0)}"
        )

    if st.button("Próximo"):

        st.session_state["passo"] = 6
        st.rerun()



# =====================================
# PASSO 6
# =====================================

def tela_assinaturas():

    st.progress(6 / 7)

    st.subheader(
        "Passo 6 de 7 - Conferir Assinaturas"
    )

    st.info(
        """
        Confira manualmente os contratos antes de enviar para o SharePoint.

        ✅ Verifique as assinaturas

        ✅ Verifique se todas as páginas estão presentes

        ✅ Verifique se o contrato corresponde ao cliente correto
        """
    )

    contratos_processados = st.session_state.get(
        "contratos_processados",
        []
    )

    if contratos_processados:

        # ZIP COM TODOS OS CONTRATOS

        zip_buffer = io.BytesIO()

        st.write(
            "Qtd processados:",
            len(contratos_processados)
        )

        for contrato in contratos_processados:

            st.write(
                contrato["nome"]
            )

        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zip_file:

            for contrato in contratos_processados:

                zip_file.writestr(
                    contrato["nome"],
                    contrato["pdf_bytes"]
                )

        zip_buffer.seek(0)

        with zipfile.ZipFile(
            zip_buffer,
            "r"
        ) as teste_zip:

            st.write(
                "Arquivos dentro do ZIP:"
            )

            st.write(
                teste_zip.namelist()
            )

        zip_buffer.seek(0)

        st.download_button(
            label="📦 Baixar Todos os Contratos (.ZIP)",
            data=zip_buffer,
            file_name="Contratos_Renomeados.zip",
            mime="application/zip"
        )

        st.divider()

        indice = st.selectbox(
            "Visualizar contrato",
            range(len(contratos_processados)),
            format_func=lambda i:
                contratos_processados[i]["nome"]
        )

        nome_renomeado = contratos_processados[indice]["nome"]

        pdf_bytes = contratos_processados[indice]["pdf_bytes"]

        st.download_button(
            label="📥 Baixar contrato selecionado",
            data=pdf_bytes,
            file_name=nome_renomeado,
            mime="application/pdf"
        )

        st.write(
            f"Arquivo será salvo como: {nome_renomeado}"
        )

    else:

        st.warning(
            "Nenhum contrato processado encontrado."
        )

    c1, c2 = st.columns(2)

    with c1:

        if st.button("Voltar"):

            st.session_state["passo"] = 5

            st.rerun()

    with c2:

        if st.button("Próximo"):

            st.session_state["passo"] = 7

            st.rerun()
# =====================================
# PASSO 7
# =====================================

def tela_sharepoint():

    st.progress(7 / 7)

    st.subheader(
        "Passo 7 de 7 - SharePoint"
    )

    st.success(
        """
        ✅ Arquivos renomeados com sucesso

        Próximos passos:

        1. Abrir o SharePoint

        2. Salvar os contratos conferidos

        3. O Power Automate continuará o fluxo automaticamente
        """
    )

    relatorio = st.session_state.get(
        "relatorio"
    )

    st.link_button(
        "📂 Abrir Pasta SharePoint",
        RELATORIOS[relatorio]["sharepoint"]
    )
    
    col1, col2 = st.columns(2)

    with col1:

        if st.button("🔄 Novo Processo"):

            st.session_state["passo"] = 1

            st.session_state.pop("tabela", None)
            st.session_state.pop("pdfs", None)
            st.session_state.pop("relatorio", None)

            st.rerun()

    with col2:

        if st.button("🚪 Sair"):

            st.session_state.clear()

            st.rerun()
    
# =====================================
# NAVEGAÇÃO
# =====================================

if st.session_state["passo"] == 1:
    tela_relatorio()

elif st.session_state["passo"] == 2:
    tela_relacao()

elif st.session_state["passo"] == 3:
    tela_upload()

elif st.session_state["passo"] == 4:
    tela_renomeacao()

elif st.session_state["passo"] == 5:
    tela_resultado()

elif st.session_state["passo"] == 6:
    tela_assinaturas()

elif st.session_state["passo"] == 7:
    tela_sharepoint()
