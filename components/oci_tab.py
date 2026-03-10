import streamlit as st
from services.utils import mostrar_imagens_existentes

def render_oci_tab(dados_formulario):
    st.header("OCI Upgrade")
        
    dados_formulario['oci_implementado'] = st.radio("OCI já está implementado nas ferramentas Google?", ("Sim", "Não"), index=None, key='k_oci_impl')
    dados_formulario['oci_platform'] = st.radio("OCI está configurado corretamente na interface da plataforma?", ("Sim", "Não"), index=None, key='k_oci_platform')


    if dados_formulario['oci_implementado'] == "Sim":
        dados_formulario['oci_metodo'] = st.selectbox(
            "Qual método de integração é utilizado?",
            ("Selecione", "Data Manager API", "Data Manager UI", "Google Ads API", "Search Ads API", "Campaign Manager API"),
            key='k_oci_method'
        )
        
        dados_formulario['oci_infos'] = st.multiselect(
            "Quais informações são atualmente integradas?",
            ["gclid", "dclid", "braid", "email", "telefone", "endereço IP", "id da transação", "match id", "atributos de sessão"],
            key='k_oci_infos'
        )

        st.file_uploader("Upload de imagens de validação (OCI)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_oci")
        mostrar_imagens_existentes('existing_img_oci', "OCI") # Painel para mostrar imagens já existentes no Sheets para OCI
    
    else:
        dados_formulario['oci_possible_config'] = st.radio("À princípio, é possível configurar o OCI no ambiente do cliente?", ("Sim", "Não", "Não sei"), index=None, key='k_oci_possible_config')
        dados_formulario['oci_blocks'] = st.text_area("Quais possíveis bloqueios foram identificados para a configuração do OCI?", key='k_oci_blocks')
        
    dados_formulario['obs_oci'] = st.text_area("Observações (OCI)", key='k_obs_oci')