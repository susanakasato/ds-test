import streamlit as st # pyright: ignore[reportMissingImports]
import time
from services.google_api import check_client_in_sheets, get_services
from services.utils import SHEETS_ID, SHEETS_RANGE, SHEETS_RANGE_WIDTH, Headers_Map, get_sheet_column_index, get_platform_from_key, State_Keys_Map, sheet_to_state

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
    if st.session_state.get("dropdown_client") == NEW_CLIENT_PLACEHOLDER:
        return
    # clear_form()
    st.session_state['form_load_status'] = None
    st.session_state[State_Keys_Map.CLIENT.value] = st.session_state.get("dropdown_client")
    with st.spinner("Buscando dados no banco..."):
        temp_msg = st.empty()
        try:
            sheets_service, _, _ = get_services()
            _, _, _, _, row = check_client_in_sheets(sheets_service, SHEETS_ID, SHEETS_RANGE, State_Keys_Map.CLIENT.st_state)
            
            if row:
                while len(row) < SHEETS_RANGE_WIDTH:
                    row.append("")
                # --- GOOGLE TAG GATEWAY ---
                for key in State_Keys_Map:
                    st.session_state[key.value] = sheet_to_state(row, key)
                # st.session_state[State_Keys_Map.GTG_IMPLEMENTED.value] = row[Headers_Map.GTG_IMPLEMENTED.column_index]
                # st.session_state[State_Keys_Map.CDN.value] = row[Headers_Map.CDN.column_index]
                # st.session_state[State_Keys_Map.USE_IAC.value] = row[Headers_Map.USE_IAC.column_index]
                # st.session_state[State_Keys_Map.USE_TMS.value] = row[Headers_Map.USE_TMS.column_index]
                # st.session_state[State_Keys_Map.TMS_TYPE.value] = row[Headers_Map.TMS_TYPE.column_index]
                # st.session_state[State_Keys_Map.USE_GTM_CS.value] = row[Headers_Map.USE_GTM_CS.column_index]
                # st.session_state[State_Keys_Map.GTM_CS_IDS.value] = row[Headers_Map.GTM_CS_IDS.column_index]
                # st.session_state[State_Keys_Map.USE_GTM_SS.value] = row[Headers_Map.USE_GTM_SS.column_index]
                # st.session_state[State_Keys_Map.GTM_SS_SERVER.value] = row[Headers_Map.GTM_SS_SERVER.column_index]
                # st.session_state[State_Keys_Map.AUTH_NEW_DOMAIN_PATH.value] = row[Headers_Map.AUTH_NEW_DOMAIN_PATH.column_index]
                # st.session_state[State_Keys_Map.POSSIBLE_GTG.value] = row[Headers_Map.POSSIBLE_GTG.column_index]
                # st.session_state[State_Keys_Map.GTG_BLOCKS.value] = row[Headers_Map.GTG_BLOCKS.column_index]
                # st.session_state[State_Keys_Map.GTG_PS.value] = row[Headers_Map.GTG_PS.column_index]

                # # --- UPD ---
                # st.session_state[State_Keys_Map.GTM_ANALYSIS.value] = row[Headers_Map.GTM_ANALYSIS.column_index]
                # st.session_state[State_Keys_Map.FORM_URLS.value] = row[Headers_Map.FORM_URLS.column_index]
                # st.session_state[State_Keys_Map.UPD_IMG_LINKS.value] = row[Headers_Map.UPD_IMG_LINKS.column_index]
                # st.session_state[State_Keys_Map.UPD_PS.value] = row[Headers_Map.UPD_PS.column_index]

                # # --- GA --- 
                # st.session_state[State_Keys_Map.GA_UPD_CONFIG.value] = row[Headers_Map.GA_UPD_CONFIG.column_index]
                # st.session_state[State_Keys_Map.GA_HARDCODED.value] = row[Headers_Map.GA_HARDCODED.column_index]
                # st.session_state[State_Keys_Map.GA_IMG_LINKS.value] = row[Headers_Map.GA_IMG_LINKS.column_index]
                # st.session_state[State_Keys_Map.GA_UPD_POSSIBLE_CONFIG.value] = row[Headers_Map.GA_UPD_POSSIBLE_CONFIG.column_index]
                # st.session_state[State_Keys_Map.GA_UPD_BLOCKS.value] = row[Headers_Map.GA_UPD_BLOCKS.column_index]

                # --- EC ---
                ec_platforms_formatted = row[Headers_Map.EC_PLATFORM_CONFIG.column_index].split("\n")
                ec_platforms = []
                for plat in ec_platforms_formatted:
                    plat_key = plat.split(" (")[0] if " (" in plat else plat
                    platform = get_platform_from_key(plat_key)
                    ec_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'form_ec_platform_{platform}'] = status
                # st.session_state[State_Keys_Map.EC_HARDCODED.value] = row[Headers_Map.EC_HARDCODED.column_index]
                # st.session_state[State_Keys_Map.EC_IMG_LINKS.value] = row[Headers_Map.EC_IMG_LINKS.column_index]
                # st.session_state[State_Keys_Map.EC_POSSIBLE_CONFIG.value] = row[Headers_Map.EC_POSSIBLE_CONFIG.column_index]
                # st.session_state[State_Keys_Map.EC_BLOCKS.value] = row[Headers_Map.EC_BLOCKS.column_index]

                # --- ECL ---
                ecl_platforms_formatted = row[Headers_Map.ECL_PLATFORM_CONFIG.column_index].split("\n")
                ecl_platforms = []
                for plat in ecl_platforms_formatted:
                    plat_key = plat.split(" (")[0] if " (" in plat else plat
                    platform = get_platform_from_key(plat_key)
                    ecl_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'form_ecl_platform_{plat_key}'] = status
                # st.session_state[State_Keys_Map.ECL_HARDCODED.value] = row[Headers_Map.ECL_HARDCODED.column_index]
                # st.session_state[State_Keys_Map.ECL_IMG_LINKS.value] = row[Headers_Map.ECL_IMG_LINKS.column_index]
                # st.session_state[State_Keys_Map.ECL_POSSIBLE_CONFIG.value] = row[Headers_Map.ECL_POSSIBLE_CONFIG.column_index]
                # st.session_state[State_Keys_Map.ECL_BLOCKS.value] = row[Headers_Map.ECL_BLOCKS.column_index]


                # # --- OCI ---
                # st.session_state[State_Keys_Map.OCI_IMPLEMENTED.value] = row[Headers_Map.OCI_IMPLEMENTED.column_index]
                # st.session_state[State_Keys_Map.OCI_PLATFORM.value] = row[Headers_Map.OCI_PLATFORM.column_index]
                # st.session_state[State_Keys_Map.OCI_METHOD.value] = row[Headers_Map.OCI_METHOD.column_index]
                # oci_infos = row[Headers_Map.OCI_INFOS.column_index]
                # if oci_infos:
                #     st.session_state[State_Keys_Map.OCI_INFOS.value] = oci_infos.split('\n') if State_Keys_Map.OCI_INFOS.st_state else []
                # st.session_state[State_Keys_Map.OCI_IMG_LINKS.value] = row[Headers_Map.OCI_IMG_LINKS.column_index]
                # st.session_state[State_Keys_Map.OCI_POSSIBLE_CONFIG.value] = row[Headers_Map.OCI_POSSIBLE_CONFIG.column_index]
                # st.session_state[State_Keys_Map.OCI_BLOCKS.value] = row[Headers_Map.OCI_BLOCKS.column_index]
                # st.session_state[State_Keys_Map.OCI_PS.value] = row[Headers_Map.OCI_PS.column_index]

                # --- DOCS ---
                diagnosis_doc_id = row[Headers_Map.DIAGNOSIS_DOC_ID.column_index]
                # st.session_state[State_Keys_Map.DIAGNOSIS_DOC_ID.value] = diagnosis_doc_id
                st.session_state[State_Keys_Map.DIAGNOSIS_DOC_URL.value] = f"https://docs.google.com/document/d/{diagnosis_doc_id}/edit"
                st.session_state[State_Keys_Map.DIAGNOSIS_PDF_URL.value] = f"https://docs.google.com/document/d/{diagnosis_doc_id}/export?format=pdf"

                # --- ROADMAP ---
                # st.session_state[State_Keys_Map.GTG_ROADMAP.value] = row[Headers_Map.GTG_ROADMAP.column_index]
                # st.session_state[State_Keys_Map.UPD_ROADMAP.value] = row[Headers_Map.UPD_ROADMAP.column_index]
                # st.session_state[State_Keys_Map.OCI_ROADMAP.value] = row[Headers_Map.OCI_ROADMAP.column_index]

                roadmap_doc_id = row[Headers_Map.ROADMAP_DOC_ID.column_index]
                # st.session_state[State_Keys_Map.ROADMAP_DOC_ID.value] = roadmap_doc_id
                st.session_state[State_Keys_Map.ROADMAP_DOC_URL.value] = f"https://docs.google.com/document/d/{roadmap_doc_id}/edit"
                st.session_state[State_Keys_Map.ROADMAP_PDF_URL.value] = f"https://docs.google.com/document/d/{roadmap_doc_id}/export?format=pdf"

                st.session_state['form_load_status'] = True
            else:
                st.session_state['form_load_status'] = None
        except Exception as e:
            st.session_state['form_load_status'] = False
            print(f"Erro ao carregar dados do cliente: {e}")
            
    if st.session_state['form_load_status'] == None:
        temp_msg.warning("Cliente não encontrado. Por favor, preencha o formulário para cadastrar um novo cliente ou selecione outro cliente existente.")
    elif st.session_state['form_load_status'] == True:
        temp_msg.success("✨ Formulário preenchido com dados existentes!")
    elif st.session_state['form_load_status'] == False:
        temp_msg.error("Erro ao carregar dados do cliente. Por favor, tente novamente ou selecione outro cliente.")
    time.sleep(1)
    temp_msg.empty()

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
        st.text_input("Digite o nome do novo cliente *", key=State_Keys_Map.CLIENT.value)
        return

    