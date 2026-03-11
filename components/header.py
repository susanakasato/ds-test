import streamlit as st
from services.google_api import check_client_in_sheets, get_services
from services.utils import SHEETS_ID, SHEETS_RANGE, SHEETS_RANGE_WIDTH, Headers_Map, get_sheet_column_index, get_platform_from_key, State_Keys_Map

NEW_CLIENT_PLACEHOLDER = "✨ Cadastrar Novo Cliente..."

def clear_form():
    # keys = st.session_state.keys()
    # form_keys = [key for key in st.session_state.keys() if key.startswith('form_')]
    # for key in chaves_para_apagar:
    #     if isinstance(st.session_state[key], list):
    #         st.session_state[key] = []
    #     elif isinstance(st.session_state[key], str):
    #         st.session_state[key] = ""
    #     else:
    #         st.session_state[key] = None
    keys = [key for key in st.session_state.keys() if key.startswith('form_')]
    for key in keys:
        del st.session_state[key]

def carregar_dados_cliente():
    if st.session_state.get("dropdown_client") != NEW_CLIENT_PLACEHOLDER:
        return
    
    clear_form()
    st.session_state['form_load_status'] = None
    st.session_state[State_Keys_Map.CLIENT] = st.session_state.get("dropdown_client")
    with st.spinner("Buscando dados no banco..."):
        try:
            sheets_service, _, _ = get_services()
            _, _, _, _, row = check_client_in_sheets(sheets_service, SHEETS_ID, SHEETS_RANGE, st.session_state.get('form_client'))
            if row:
                while len(row) < SHEETS_RANGE_WIDTH:
                    row.append("")
                
                # --- GOOGLE TAG GATEWAY ---
                st.session_state[State_Keys_Map.GTG_IMPLEMENTED] = row[get_sheet_column_index(Headers_Map.GTG_IMPLEMENTED)]
                st.session_state[State_Keys_Map.CDN] = row[get_sheet_column_index(Headers_Map.CDN)]
                st.session_state[State_Keys_Map.USE_IAC] = row[get_sheet_column_index(Headers_Map.USE_IAC)]
                st.session_state[State_Keys_Map.USE_TMS] = row[get_sheet_column_index(Headers_Map.USE_TMS)]
                st.session_state[State_Keys_Map.TMS_TYPE] = row[get_sheet_column_index(Headers_Map.TMS_TYPE)]
                st.session_state[State_Keys_Map.USE_GTM_CS] = row[get_sheet_column_index(Headers_Map.USE_GTM_CS)]
                st.session_state[State_Keys_Map.GTM_CS_IDS] = row[get_sheet_column_index(Headers_Map.GTM_CS_IDS)]
                st.session_state[State_Keys_Map.GTM_SS] = row[get_sheet_column_index(Headers_Map.USE_GTM_SS)]
                st.session_state[State_Keys_Map.GTM_SS_SERVER] = row[get_sheet_column_index(Headers_Map.GTM_SS_SERVER)]
                st.session_state[State_Keys_Map.AUTH_NEW_DOMAIN_PATH] = row[get_sheet_column_index(Headers_Map.AUTH_NEW_DOMAIN_PATH)]
                st.session_state[State_Keys_Map.POSSIBLE_GTG] = row[get_sheet_column_index(Headers_Map.POSSIBLE_GTG)]
                st.session_state[State_Keys_Map.GTG_BLOCKS] = row[get_sheet_column_index(Headers_Map.GTG_BLOCKS)]
                st.session_state[State_Keys_Map.GTG_PS] = row[get_sheet_column_index(Headers_Map.GTG_PS)]

                # --- UPD ---
                st.session_state[State_Keys_Map.GTM_ANALYSIS] = row[get_sheet_column_index(Headers_Map.GTM_ANALYSIS)]
                st.session_state[State_Keys_Map.FORM_URLS] = row[get_sheet_column_index(Headers_Map.FORM_URLS)]
                st.session_state[State_Keys_Map.UPD_IMG_LINKS] = row[get_sheet_column_index(Headers_Map.UPD_IMG_LINKS)]

                # --- GA --- 
                st.session_state[State_Keys_Map.GA_UPD_CONFIG] = row[get_sheet_column_index(Headers_Map.GA_UPD_CONFIG)]
                st.session_state[State_Keys_Map.GA_HARDCODED] = row[get_sheet_column_index(Headers_Map.GA_HARDCODED)]
                st.session_state[State_Keys_Map.GA_IMG_LINKS] = row[get_sheet_column_index(Headers_Map.GA_IMG_LINKS)]
                st.session_state[State_Keys_Map.GA_UPD_POSSIBLE_CONFIG] = row[get_sheet_column_index(Headers_Map.GA_UPD_POSSIBLE_CONFIG)]
                st.session_state[State_Keys_Map.GA_UPD_BLOCKS] = row[get_sheet_column_index(Headers_Map.GA_UPD_BLOCKS)]

                # --- EC ---
                ec_platforms_formatted = row[get_sheet_column_index(Headers_Map.EC_PLATFORMS)].split("\n")
                ec_platforms = []
                for plat in ec_platforms_formatted:
                    plat_key = plat.split(" (")[0] if " (" in plat else plat
                    platform = get_platform_from_key(plat_key)
                    ec_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'form_ec_platform_{platform}'] = status
                st.session_state[State_Keys_Map.EC_PLATFORMS] = ec_platforms
                st.session_state[State_Keys_Map.EC_HARDCODED] = row[get_sheet_column_index(Headers_Map.EC_HARDCODED)]
                st.session_state[State_Keys_Map.EC_IMG_LINKS] = row[get_sheet_column_index(Headers_Map.EC_IMG_LINKS)]
                st.session_state[State_Keys_Map.EC_POSSIBLE_CONFIG] = row[get_sheet_column_index(Headers_Map.EC_POSSIBLE_CONFIG)]
                st.session_state[State_Keys_Map.EC_BLOCKS] = row[get_sheet_column_index(Headers_Map.EC_BLOCKS)]

                # --- ECL ---
                ecl_platforms_formatted = row[get_sheet_column_index(Headers_Map.ECL_PLATFORMS)].split("\n")
                ecl_platforms = []
                for plat in ecl_platforms_formatted:
                    plat_key = plat.split(" (")[0] if " (" in plat else plat
                    platform = get_platform_from_key(plat_key)
                    ecl_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'form_ecl_platform_{plat_key}'] = status
                st.session_state[State_Keys_Map.ECL_PLATFORMS] = ecl_platforms
                st.session_state[State_Keys_Map.ECL_HARDCODED] = row[get_sheet_column_index(Headers_Map.ECL_HARDCODED)]
                st.session_state[State_Keys_Map.ECL_IMG_LINKS] = row[get_sheet_column_index(Headers_Map.ECL_IMG_LINKS)]
                st.session_state[State_Keys_Map.ECL_POSSIBLE_CONFIG] = row[get_sheet_column_index(Headers_Map.ECL_POSSIBLE_CONFIG)]
                st.session_state[State_Keys_Map.ECL_BLOCKS] = row[get_sheet_column_index(Headers_Map.ECL_BLOCKS)]

                st.session_state[State_Keys_Map.UPD_PS] = row[get_sheet_column_index(Headers_Map.UPD_PS)]

                # --- OCI ---
                st.session_state[State_Keys_Map.UPD_PS] = row[get_sheet_column_index(Headers_Map.OBS_SIGNALS)]
                st.session_state[State_Keys_Map.OCI_IMPLEMENTED] = row[get_sheet_column_index(Headers_Map.OCI_IMPLEMENTED)]
                st.session_state[State_Keys_Map.OCI_PLATFORM] = row[get_sheet_column_index(Headers_Map.OCI_PLATFORM)]
                st.session_state[State_Keys_Map.OCI_METHOD] = row[get_sheet_column_index(Headers_Map.OCI_METHOD)]
                oci_infos = row[get_sheet_column_index(Headers_Map.OCI_INFOS)]
                if oci_infos:
                    st.session_state[State_Keys_Map.OCI_INFOS] = [x.strip() for x in oci_infos.split('\n') if x.strip() in ["gclid", "dclid", "braid", "email", "telefone", "endereço IP", "id da transação", "match id", "atributos de sessão"]]
                st.session_state[State_Keys_Map.OCI_IMG_LINKS] = row[get_sheet_column_index(Headers_Map.OCI_IMG_LINKS)]
                st.session_state[State_Keys_Map.OCI_POSSIBLE_CONFIG] = row[get_sheet_column_index(Headers_Map.OCI_POSSIBLE_CONFIG)]
                st.session_state[State_Keys_Map.OCI_BLOCKS] = row[get_sheet_column_index(Headers_Map.OCI_BLOCKS)]
                st.session_state[State_Keys_Map.OCI_PS] = row[get_sheet_column_index(Headers_Map.OCI_PS)]

                # --- DOCS ---
                diagnosis_doc_id = row[get_sheet_column_index(Headers_Map.DIAGNOSIS_DOC_ID)]
                st.session_state[State_Keys_Map.DIAGNOSIS_DOC_ID] = diagnosis_doc_id
                st.session_state[State_Keys_Map.DIAGNOSIS_DOC_URL] = f"https://docs.google.com/document/d/{diagnosis_doc_id}/edit"
                st.session_state[State_Keys_Map.DIAGNOSIS_PDF_URL] = f"https://docs.google.com/document/d/{diagnosis_doc_id}/export?format=pdf"

                # --- ROADMAP ---
                st.session_state[State_Keys_Map.GTG_ROADMAP] = row[get_sheet_column_index(Headers_Map.GTG_ROADMAP)]
                st.session_state[State_Keys_Map.UPD_ROADMAP] = row[get_sheet_column_index(Headers_Map.UPD_ROADMAP)]
                st.session_state[State_Keys_Map.OCI_ROADMAP] = row[get_sheet_column_index(Headers_Map.OCI_ROADMAP)]

                roadmap_doc_id = row[get_sheet_column_index(Headers_Map.ROADMAP_DOC_ID)]
                st.session_state[State_Keys_Map.ROADMAP_DOC_ID] = roadmap_doc_id
                st.session_state[State_Keys_Map.ROADMAP_DOC_URL] = f"https://docs.google.com/document/d/{roadmap_doc_id}/edit"
                st.session_state[State_Keys_Map.ROADMAP_PDF_URL] = f"https://docs.google.com/document/d/{roadmap_doc_id}/export?format=pdf"

                st.session_state['form_load_status'] = True
                   
        except Exception as e:
            st.session_state['form_load_status'] = e

def render_header():
    dropdown_options = [NEW_CLIENT_PLACEHOLDER] + st.session_state['client_list']

    st.write("Selecione o cliente ou cadastre um novo:")
    clientSection, clearFormSection = st.columns([3, 1], vertical_alignment="center")
    with clientSection:
        selected_client = st.selectbox(
            "Cliente",
            options=dropdown_options, 
            key="dropdown_client",
            on_change=carregar_dados_cliente,
            label_visibility="collapsed"
        )
        
    with clearFormSection:
        if st.button("🧹 Limpar Formulário", use_container_width=True):
            clear_form()

    if selected_client == NEW_CLIENT_PLACEHOLDER:
        st.text_input("Digite o nome do novo cliente *", key="form_client")
        return
    else:
        st.session_state['form_client'] = selected_client

        if st.session_state.get("form_load_status") and st.session_state.get("form_load_status") == True:
            st.success("✨ Formulário preenchido com dados existentes!") 

        elif st.session_state.get("form_load_status") and st.session_state.get("form_load_status") == False:
            st.error(f"Erro ao carregar cliente: {st.session_state.get(State_Keys_Map.CLIENT)}. Cliente não encontrado na base de dados.")

    