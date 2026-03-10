from enum import Enum
import streamlit as st

PLANILHA_ID = '1D7TLq7-ThUj5WyUn1Ys3X05jKilDDmYjpLSxngK6ij4'
RANGE_PLANILHA = 'DB Diagnóstico!A:AU'
RANGE_PLANILHA_CLIENTES = 'DB Diagnóstico!A2:A'
RANGE_PLANILHA_WIDTH = 47
PARENT_FOLDER_ID = '12ZTADl3NujM3fNhYTHG3C7cYNPPpFaN8'


def mostrar_imagens_existentes(key_state, nome_secao):
    """Cria um painel expansível mostrando quantas imagens já existem e os seus links."""
    links = st.session_state.get(key_state, "")
    if links:
        lista_links = [l.strip() for l in links.split("\n") if l.strip()]
        qtd = len(lista_links)
        if qtd > 0:
            with st.expander(f"✅ {qtd} imagem(ns) já salva(s) para {nome_secao}", expanded=False):
                st.markdown("Se você fizer upload de novos arquivos, eles serão **adicionados** a esta lista.")
                for i, link in enumerate(lista_links):
                    st.markdown(f"🖼️ [Visualizar Imagem {i+1} no Drive]({link})")

def update_lista_clientes():   
    st.session_state['lista_clientes'] = [] # Inicia vazio
    try:
        with st.spinner("Carregando lista de clientes do banco de dados..."):
            from services.google_api import get_services 
            sheets, _, _ = get_services()
            resultado = sheets.spreadsheets().values().get(
                spreadsheetId=PLANILHA_ID, 
                range=RANGE_PLANILHA_CLIENTES
            ).execute()
            
            linhas = resultado.get('values', [])
            clientes = [linha[0].strip() for linha in linhas if linha and len(linha) > 0 and linha[0].strip()]
            
            # Guarda a lista ordenada e sem repetições na memória
            st.session_state['lista_clientes'] = sorted(list(set(clientes)))
    except Exception as e:
        st.error(f"Erro ao carregar a lista de clientes: {e}")

class Diagnosis_Headers(Enum):
    CLIENT = 'Cliente'

    GTG_IMPLEMENTED = 'GTG implementado'
    CDN = 'Qual CDN Utiliza?'
    USE_IAC = 'Utiliza IaC?'
    USE_TMS = 'Utiliza TMS?'
    TMS_TYPE = 'Qual TMS?'
    USE_GTM_CS = 'Utiliza GTM Client-Side?'
    GTM_CS_IDS = 'IDs GTM Client-Side'
    USE_GTM_SS = 'Utiliza GTM Server-Side?'
    GTM_SS_SERVER = 'Qual servidor o GTM Server-Side está hospedado?'
    AUTH_NEW_DOMAIN_PATH = 'O cliente autorizou a criação de novos caminhos no domínio principal?'
    OBS_GTG = 'GTG - Observações'
    POSSIBLE_GTG = 'À princípio, é possível configurar o GTG?'
    GTG_BLOCKS = 'Possíveis bloqueios para a implementação do GTG'

    GTM_ANALYSIS = 'Análise do json do GTM'
    URLS_FORMS = 'URLS onde apresentam potenciais locais de coleta de dados UPD'
    UPD_IMG_LINKS = 'UPD - Links de evidências'

    GA_UPD_CONFIG = 'O GA4 UPD já está configurado na plataforma?'
    GA_HARDCODED = 'O GA4 UPD foi implementado via hardcoded (se for o caso) corretamente?'
    GA_IMG_LINKS = 'GA4 UPD - Links de evidências'
    GA_UPD_POSSIBLE_CONFIG = 'À princípio, é possível configurar o GA UPD?'
    GA_UPD_BLOCKS = 'Possíveis bloqueios para a configuração do GA UPD'

    EC_PLATFORMS = 'Quais plataformas Google o cliente utiliza, que poderiam ter o EC implementado?'
    EC_HARDCODED = 'O EC foi implementado via hardcoded (se for o caso) corretamente?'
    EC_IMG_LINKS = 'EC - Links de evidências'
    EC_POSSIBLE_CONFIG = 'À princípio, é possível configurar o EC?'
    EC_BLOCKS = 'Possíveis bloqueios para a configuração do EC'

    ECL_PLATFORMS = 'Quais plataformas Google o cliente utiliza, que poderiam ter o ECL implementado?'
    ECL_HARDCODED = 'O ECL foi implementado via hardcoded (se for o caso) corretamente?'
    ECL_IMG_LINKS = 'ECL - Links de evidências'
    ECL_POSSIBLE_CONFIG = 'À princípio, é possível configurar o ECl?'
    ECL_BLOCKS = 'Possíveis bloqueios para a configuração do ECL'

    OBS_SIGNALS = 'Envio de sinais - Observações'

    OCI_IMPLEMENTED = 'O OCI já está implementado?'
    OCI_PLATFORM = 'O OCI já está configurado na plataforma?'
    OCI_METHOD = 'Qual o método utilizado para a configuração do OCI?'
    OCI_INFOS = 'Quais dados estão sendo utilizadas e cruzados para o OCI?'
    OCI_IMG_LINKS = 'OCI - Links de evidências'
    OCI_POSSIBLE_CONFIG = 'À princípio, é possível configurar o OCI?'
    OCI_BLOCKS = 'Possíveis bloqueios para a configuração do OCI'
    OBS_OCI = 'OCI - Observações'

    DIAGNOSIS_DOC_ID = 'ID do documento diagnóstico gerado'
    DRIVE_ID = 'ID da pasta do Drive do cliente'
    ROADMAP_DOC_ID = 'ID do documento roadmap gerado'

    GTG_ROADMAP = 'GTG Roadmap'
    UPD_ROADMAP = 'UPD Roadmap'
    OCI_ROADMAP = 'OCI Roadmap'

def getPlatformFromKey(key):
    dict = {
        "gads": "Google Ads",
        "sa": "Search Ads 360",
        "cm": "Campaign Manager 360"
    }
    return dict.get(key, key)

def getKeyFromPlatform(platform):
    dict = {
        "Google Ads": "gads",
        "Search Ads 360": "sa",
        "Campaign Manager 360": "cm"
    }
    return dict.get(platform, platform)

def get_column_index_from_diagnosis_db(diagnosis_headers):
    """Função específica para retornar o índice da coluna dado o nome do header, usando a constante RANGE_PLANILHA."""
    if st.session_state.get('diagnosis_headers') is None:
        from services.google_api import get_services, get_headers_map
        sheets_service, _, _ = get_services()
        st.session_state['diagnosis_headers'] = get_headers_map(sheets_service, PLANILHA_ID, RANGE_PLANILHA)
    return st.session_state['diagnosis_headers'].get(diagnosis_headers.value, -1)