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
                for key in State_Keys_Map:
                    st.session_state[key.value] = sheet_to_state(row, key)

                ec_platforms_formatted = row[Headers_Map.EC_PLATFORM_CONFIG.column_index].split("\n")
                ec_platforms = []
                for plat in ec_platforms_formatted:
                    plat_key = plat.split(" (")[0] if " (" in plat else plat
                    platform = get_platform_from_key(plat_key)
                    ec_platforms.append(platform) 
                    status = "Sim" if "Sim" in plat else "Não" if "Não" in plat else None
                    if status:
                        st.session_state[f'form_ec_platform_{platform}'] = status

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
                        
                diagnosis_doc_id = row[Headers_Map.DIAGNOSIS_DOC_ID.column_index]
                st.session_state[State_Keys_Map.DIAGNOSIS_DOC_URL.value] = f"https://docs.google.com/document/d/{diagnosis_doc_id}/edit"
                st.session_state[State_Keys_Map.DIAGNOSIS_PDF_URL.value] = f"https://docs.google.com/document/d/{diagnosis_doc_id}/export?format=pdf"

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
    st.session_state[State_Keys_Map.CLIENT.value] = selected_client

    