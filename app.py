from components.diagnosis_tab import render_diagnosis_tab
from components.header import render_header
from components.roadmap_tab import render_roadmap_tab
import streamlit as st
from services.google_api import authenticate_google, check_client_in_sheets, create_drive_folder, create_update_diagnostic_doc, download_image_from_drive, get_headers_map, get_services, save_auth_token, save_to_sheets, upload_image_to_drive
from services.utils import update_lista_clientes




# Configuração inicial da página
st.set_page_config(page_title="DS30 | Diagnóstico & Roadmap", layout="wide")

if "code" in st.query_params:
    codigo_google = st.query_params["code"]
    save_auth_token(codigo_google)
    st.query_params.clear() # Limpa a URL para ficar bonita novamente
    st.success("Login no Google realizado com sucesso!")

# 2. Verifica as credenciais
creds, auth_url = authenticate_google()

# 3. Se não estiver logado, mostra o botão e PARA a renderização do app
if not creds:
    st.title("🔒 Autenticação Necessária")
    st.warning("Para utilizar o sistema de diagnóstico, gerar relatórios e anexar imagens, é necessário conectar a sua conta do Google.")
    st.link_button("🔑 Fazer Login com o Google", auth_url, type="primary")
    st.stop() # Interrompe a leitura do código aqui. O formulário abaixo só aparece se logar!

headerTitle, headerLogo = st.columns([6, 1], vertical_alignment="center")
with headerTitle:
    st.title("DS30 | Diagnóstico & Roadmap")
with headerLogo:
    st.image("images/logo.png", width=120)

if 'lista_clientes' not in st.session_state:
    update_lista_clientes() # Carrega a lista de clientes do Google Sheets apenas uma vez e guarda na memória (Session State)

render_header()

diagnosis_tab, roadmap_tab = st.tabs(["📝 Diagnóstico", "🛣️ Roadmap Sugerido"])

with diagnosis_tab:
    render_diagnosis_tab(st.session_state.get('k_client', ''))

    # ==========================================
# ABA 4: ROADMAP SUGERIDO (EDITÁVEL)
# ==========================================
with roadmap_tab:
    render_roadmap_tab(st.session_state.get('k_client', ''))

