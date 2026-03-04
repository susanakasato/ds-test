from services.google_api import check_client_in_sheets, get_services
import streamlit as st
from services.utils import PLANILHA_ID, RANGE_PLANILHA, Diagnosis_Headers, get_column_index_from_diagnosis_db

def limpar_form():
    # Encontra todas as chaves do formulário no Session State
    chaves_para_apagar = [key for key in st.session_state.keys() if key.startswith('k_')]
    chaves_imagem = [key for key in st.session_state.keys() if key.startswith('img_') or key.startswith('existing_img_')]
    # Apaga uma por uma
    for key in chaves_para_apagar:
        if isinstance(st.session_state[key], list):
            st.session_state[key] = []
        elif isinstance(st.session_state[key], str):
            st.session_state[key] = ""
        else:
            st.session_state[key] = None
        
    for key in chaves_imagem:
        del st.session_state[key]
        
# def update_session(key, value, valid_options=None):
#     """Injeta um valor com segurança no formulário (Session State)"""
#     if not value: return
#     if valid_options and value not in valid_options: return
#     st.session_state[key] = value

# No arquivo header.py

def carregar_dados_cliente():
    limpar_form() # Limpa o formulário antes de carregar os dados do cliente selecionado
    cliente_selecionado = st.session_state.get("dropdown_cliente")
    
    # Se mudar para "Novo Cliente", limpa o formulário e para
    if cliente_selecionado == "✨ Cadastrar Novo Cliente...":
        st.text_input("Digite o nome do novo cliente *", key="k_client")
        return

    # Caso contrário, busca os dados APENAS ESTA VEZ
    st.session_state['k_client'] = cliente_selecionado
    with st.spinner("Buscando dados no banco..."):
        try:
            sheets, _, _ = get_services()
            _, _, _, row = check_client_in_sheets(sheets, PLANILHA_ID, RANGE_PLANILHA, cliente_selecionado, -1)
            
            if row:
                def get_val(idx): return row[idx] if len(row) > idx else ""
                
                # --- GOOGLE TAG GATEWAY ---
                st.session_state['k_gtg'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_IMPLEMENTED))
                st.session_state['k_cdn'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.CDN))
                st.session_state['k_iac'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_IAC))
                st.session_state['k_usa_tms'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_TMS))
                st.session_state['k_tms_type'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.TMS_TYPE))
                st.session_state['k_gtm_cs'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_GTM_CS))
                st.session_state['k_gtm_cs_ids'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_CS_IDS))
                st.session_state['k_gtm_ss'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_GTM_SS))
                st.session_state['k_gtm_ss_server'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_SS_SERVER))
                st.session_state['k_novos_caminhos'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.AUTH_NEW_DOMAIN_PATH))
                st.session_state['k_possible_gtg'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.POSSIBLE_GTG))
                st.session_state['k_gtg_blocks'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_BLOCKS))
                st.session_state['k_obs_gtg'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_GTG))

                # --- UPD ---
                st.session_state['k_gtm_analise'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_ANALYSIS))
                st.session_state['k_urls_forms'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.URLS_FORMS))

                # --- GA --- 
                st.session_state['k_ga_config'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_CONFIG))
                st.session_state['k_ga_hard'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_HARDCODED))
                st.session_state['existing_img_ga4'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_IMG_LINKS))
                st.session_state['k_ga_upd_possible_config'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_POSSIBLE_CONFIG))
                st.session_state['k_ga_upd_blocks'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_BLOCKS))
                
                # --- EC ---
                ec_platforms_formatted = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_PLATFORMS)).split("\n")
                ec_platforms = []
                for plat in ec_platforms_formatted:
                    platform = plat.split(" (")[0] if " (" in plat else plat
                    ec_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'k_ec_platform_{platform}'] = status
                st.session_state['k_ec_platforms'] = ec_platforms
                st.session_state['k_ec_hard'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_HARDCODED))
                st.session_state['existing_img_ec'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_IMG_LINKS))
                st.session_state['k_ec_possible_config'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_POSSIBLE_CONFIG))
                st.session_state['k_ec_blocks'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_BLOCKS))

                # --- ECL ---
                ecl_platforms_formatted = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_PLATFORMS)).split("\n")
                ecl_platforms = []
                for plat in ecl_platforms_formatted:
                    platform = plat.split(" (")[0] if " (" in plat else plat
                    ecl_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'k_ecl_platform_{platform}'] = status
                st.session_state['k_ecl_platforms'] = ecl_platforms
                st.session_state['k_ecl_hard'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_HARDCODED))
                st.session_state['existing_img_ecl'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_IMG_LINKS))
                st.session_state['k_ecl_possible_config'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_POSSIBLE_CONFIG))
                st.session_state['k_ecl_blocks'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_BLOCKS))

                # --- OCI ---
                st.session_state['k_obs_upd'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_SIGNALS))
                st.session_state['k_oci_impl'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_IMPLEMENTED))
                st.session_state['k_oci_platform'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_PLATFORM))
                st.session_state['k_oci_metodo'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_METHOD))
                oci_infos = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_INFOS))
                if oci_infos:
                    st.session_state['k_oci_infos'] = [x.strip() for x in oci_infos.split('\n') if x.strip() in ["gclid", "dclid", "braid", "email", "telefone", "endereço IP", "id da transação", "match id", "atributos de sessão"]]
                st.session_state['existing_img_oci'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_IMG_LINKS))
                st.session_state['k_oci_possible_config'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_POSSIBLE_CONFIG))
                st.session_state['k_oci_blocks'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_BLOCKS))
                st.session_state['k_obs_oci'] = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_OCI))

                # --- DOCS ---
                doc_id = get_val(get_column_index_from_diagnosis_db(Diagnosis_Headers.DOC_ID))
                st.session_state['k_doc_url'] = f"https://docs.google.com/document/d/{doc_id}/edit"
                st.session_state['k_pdf_url'] = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"

                st.success("✨ Formulário preenchido com dados existentes!")    
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")

def render_header():
    opcoes_dropdown = ["✨ Cadastrar Novo Cliente..."] + st.session_state['lista_clientes']

    col1, col2 = st.columns([3, 1])
    with col1:
        # O Dropdown principal
        cliente_selecionado = st.selectbox(
            "Selecione o Cliente ou cadastre um novo *", 
            options=opcoes_dropdown, 
            key="dropdown_cliente",
            on_change=carregar_dados_cliente
        )
        
    with col2:
        st.write("") 
        st.write("") 
        # NOVO: Botão de Limpeza
        if st.button("🧹 Limpar Formulário", use_container_width=True):
            limpar_form()

    