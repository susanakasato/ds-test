from enum import Enum
import streamlit as st

SHEETS_ID = '1D7TLq7-ThUj5WyUn1Ys3X05jKilDDmYjpLSxngK6ij4'
SHEETS_RANGE = 'DB Diagnóstico!A:AU'
SHEETS_RANGE_CLIENT = 'DB Diagnóstico!A2:A'
SHEETS_RANGE_WIDTH = 47
PARENT_FOLDER_ID = '12ZTADl3NujM3fNhYTHG3C7cYNPPpFaN8'

def show_existing_images(key_state, section_name):
    """Cria um painel expansível mostrando quantas imagens já existem e os seus links."""
    links = st.session_state.get(key_state, "")
    if links:
        lista_links = [l.strip() for l in links.split("\n") if l.strip()]
        qtd = len(lista_links)
        if qtd > 0:
            with st.expander(f"✅ {qtd} imagem(ns) já salva(s) para {section_name}", expanded=False):
                st.markdown("Se você fizer upload de novos arquivos, eles serão **adicionados** a esta lista.")
                for i, link in enumerate(lista_links):
                    st.markdown(f"🖼️ [Visualizar Imagem {i+1} no Drive]({link})")

def update_client_list():   
    st.session_state['client_list'] = [] # Inicia vazio
    try:
        with st.spinner("Carregando lista de clientes do banco de dados..."):
            from services.google_api import get_services 
            sheets, _, _ = get_services()
            resultado = sheets.spreadsheets().values().get(
                spreadsheetId=SHEETS_ID, 
                range=SHEETS_RANGE_CLIENT
            ).execute()
            
            linhas = resultado.get('values', [])
            clientes = [linha[0].strip() for linha in linhas if linha and len(linha) > 0 and linha[0].strip()]
            
            # Guarda a lista ordenada e sem repetições na memória
            st.session_state['client_list'] = sorted(list(set(clientes)))
    except Exception as e:
        st.error(f"Erro ao carregar a lista de clientes: {e}")

class Headers_Map(Enum):
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
    GTG_PS = 'GTG - Observações'
    POSSIBLE_GTG = 'À princípio, é possível configurar o GTG?'
    GTG_BLOCKS = 'Possíveis bloqueios para a implementação do GTG'

    GTM_ANALYSIS = 'Análise do json do GTM'
    FORM_URLS = 'URLS onde apresentam potenciais locais de coleta de dados UPD'
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

    UPD_PS = 'Envio de sinais - Observações'

    OCI_IMPLEMENTED = 'O OCI já está implementado?'
    OCI_PLATFORM = 'O OCI já está configurado na plataforma?'
    OCI_METHOD = 'Qual o método utilizado para a configuração do OCI?'
    OCI_INFOS = 'Quais dados estão sendo utilizadas e cruzados para o OCI?'
    OCI_IMG_LINKS = 'OCI - Links de evidências'
    OCI_POSSIBLE_CONFIG = 'À princípio, é possível configurar o OCI?'
    OCI_BLOCKS = 'Possíveis bloqueios para a configuração do OCI'
    OCI_PS = 'OCI - Observações'

    DIAGNOSIS_DOC_ID = 'ID do documento diagnóstico gerado'
    DRIVE_ID = 'ID da pasta do Drive do cliente'
    ROADMAP_DOC_ID = 'ID do documento roadmap gerado'

    GTG_ROADMAP = 'GTG Roadmap'
    UPD_ROADMAP = 'UPD Roadmap'
    OCI_ROADMAP = 'OCI Roadmap'

def get_sheet_column_index(Headers_Map):
    """Função específica para retornar o índice da coluna dado o nome do header, usando a constante RANGE_PLANILHA."""
    if st.session_state.get('Headers_Map') is None:
        from services.google_api import get_services, get_headers_map
        sheets_service, _, _ = get_services()
        st.session_state['Headers_Map'] = get_headers_map(sheets_service, SHEETS_ID, SHEETS_RANGE)
    return st.session_state['Headers_Map'].get(Headers_Map.value, -1)

class State_Keys_Map(Enum):
    CLIENT = 'form_client'

    GTG_IMPLEMENTED = 'form_gtg'
    CDN = 'form_cdn'
    USE_IAC = 'form_iac'
    USE_TMS = 'form_use_tms'
    TMS_TYPE = 'form_tms_type'
    USE_GTM_CS = 'form_gtm_cs'
    GTM_CS_IDS = 'form_gtm_cs_ids'
    USE_GTM_SS = 'form_gtm_ss'
    GTM_SS_SERVER = 'form_gtm_ss_server'
    AUTH_NEW_DOMAIN_PATH = 'form_auth_new_domain_path'
    GTG_PS = 'form_gtg_ps'
    POSSIBLE_GTG = 'form_possible_gtg'
    GTG_BLOCKS = 'form_gtg_blocks'

    GTM_ANALYSIS = 'form_gtm_analysis'
    FORM_URLS = 'form_form_urls'
    UPD_IMG_LINKS = 'form_upd_image_links'
    UPD_IMG_FORM = 'form_upd_image_form'
    UPD_IMG_RAW = 'form_upd_image_raw'
    UPD_PS = 'form_upd_ps'

    GA_UPD_CONFIG = 'form_ga_config'
    GA_HARDCODED = 'form_ga_hardcoded'
    GA_IMG_LINKS = 'form_ga_image_links'
    GA_IMG_FORM = 'form_ga_image_form'
    GA_IMG_RAW = 'form_ga_image_raw'
    GA_UPD_POSSIBLE_CONFIG = 'form_ga_upd_possible_config'
    GA_UPD_BLOCKS = 'form_ga_upd_blocks'

    EC_PLATFORMS = 'form_ec_platforms'
    EC_HARDCODED = 'form_ec_hardcoded'
    EC_IMG_LINKS = 'form_ec_image_links'
    EC_IMG_FORM = 'form_ec_image_form'
    EC_IMG_RAW = 'form_ec_image_raw'
    EC_POSSIBLE_CONFIG = 'form_ec_possible_config'
    EC_BLOCKS = 'form_ec_blocks'

    ECL_PLATFORMS = 'form_ecl_platforms'
    ECL_HARDCODED = 'form_ecl_hardcoded'
    ECL_IMG_LINKS = 'form_ecl_image_links'
    ECL_IMG_FORM = 'form_ecl_image_form'
    ECL_IMG_RAW = 'form_ecl_image_raw'
    ECL_POSSIBLE_CONFIG = 'form_ecl_possible_config'
    ECL_BLOCKS = 'form_ecl_blocks'

    OCI_IMPLEMENTED = 'form_oci_impl'
    OCI_PLATFORM = 'form_oci_platform'
    OCI_METHOD = 'form_oci_method'
    OCI_INFOS = 'form_oci_infos'
    OCI_IMG_LINKS = 'form_oci_img_links'
    OCI_IMG_FORM = 'form_oci_image_form'
    OCI_IMG_RAW = 'form_oci_image_raw'
    OCI_POSSIBLE_CONFIG = 'form_oci_possible_config'
    OCI_BLOCKS = 'form_oci_blocks'
    OCI_PS = 'form_oci_ps'

    DIAGNOSIS_DOC_ID = 'form_diagnosis_doc_id'
    DIAGNOSIS_DOC_URL = 'form_diagnosis_doc_url'
    DIAGNOSIS_PDF_URL = 'form_diagnosis_pdf_url'
    DRIVE_ID = 'form_drive_id'
    ROADMAP_DOC_ID = 'form_roadmap_doc_id'
    ROADMAP_DOC_URL = 'form_roadmap_doc_url'
    ROADMAP_PDF_URL = 'form_roadmap_pdf_url'

    GTG_ROADMAP = 'form_gtg_roadmap'
    UPD_ROADMAP = 'form_upd_roadmap'
    OCI_ROADMAP = 'form_oci_roadmap'

def get_platform_from_key(key):
    dict = {
        "gads": "Google Ads",
        "sa": "Search Ads 360",
        "cm": "Campaign Manager 360"
    }
    return dict.get(key, key)

def get_key_from_platform(platform):
    dict = {
        "Google Ads": "gads",
        "Search Ads 360": "sa",
        "Campaign Manager 360": "cm"
    }
    return dict.get(platform, platform)

def format_list(item):
    if isinstance(item, list):
        return "\n".join(item)
    return str(item) if item else ""