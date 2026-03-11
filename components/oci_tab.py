import streamlit as st # pyright: ignore[reportMissingImports]
from services.utils import State_Keys_Map, show_existing_images

def render_oci_tab():
    st.header("OCI Upgrade")
    st.radio("OCI já está implementado nas ferramentas Google?", ("Sim", "Não"), index=None, key=State_Keys_Map.OCI_IMPLEMENTED)
    st.radio("OCI está configurado corretamente na interface da plataforma?", ("Sim", "Não"), index=None, key=State_Keys_Map.OCI_PLATFORM)
    if st.session_state[State_Keys_Map.OCI_IMPLEMENTED] == "Sim":
        st.selectbox(
            "Qual método de integração é utilizado?",
            ("Selecione", "Data Manager API", "Data Manager UI", "Google Ads API", "Search Ads API", "Campaign Manager API"),
            key=State_Keys_Map.OCI_METHOD
        )
        st.multiselect(
            "Quais informações são atualmente integradas?",
            ["gclid", "dclid", "braid", "email", "telefone", "endereço IP", "id da transação", "match id", "atributos de sessão"],
            key=State_Keys_Map.OCI_INFOS
        )
        st.file_uploader("Upload de imagens de validação (OCI)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key=State_Keys_Map.OCI_IMG_FORM)
        show_existing_images(State_Keys_Map.OCI_IMG_LINKS, "OCI")
    else:
        st.radio("À princípio, é possível configurar o OCI no ambiente do cliente?", ("Sim", "Não", "Não sei"), index=None, key=State_Keys_Map.OCI_POSSIBLE_CONFIG)
        st.text_area("Quais possíveis bloqueios foram identificados para a configuração do OCI?", key=State_Keys_Map.OCI_BLOCKS)

    st.text_area("Observações (OCI)", key=State_Keys_Map.OCI_PS)