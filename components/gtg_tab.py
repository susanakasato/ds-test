import streamlit as st

def render_gtg_tab(dados_formulario):
    st.header("Google Tag Gateway")
        
    dados_formulario['gtg_implementado'] = st.radio("Possui GTG implementado?", ("Sim", "Não"), index=None, key='k_gtg')
    dados_formulario['cdn'] = st.text_input("Qual a CDN utilizada?", key='k_cdn')
    dados_formulario['iac'] = st.radio("Utiliza IaC (Infrastructure as Code)?", ("Sim", "Não"), index=None, key='k_iac')
    
    usa_tms = st.radio("Utiliza TMS?", ("Sim", "Não"), index=None, key='k_usa_tms')
    dados_formulario['usa_tms'] = usa_tms

    if usa_tms == "Sim":
        tms_type = st.selectbox("Qual TMS?", ("Selecione", "Google Tag Manager", "Tealium", "Adobe Launch", "Outros"), key='k_tms_type')
        st.session_state['tms_type'] = tms_type # Salva no estado para a Aba 2 ler
        dados_formulario['tms_type'] = tms_type

        if tms_type == "Google Tag Manager":
            gtm_cs = st.radio("Utiliza GTM Client-Side?", ("Sim", "Não"), index=None, key='k_gtm_cs')
            dados_formulario['gtm_cs'] = gtm_cs
            if gtm_cs == "Sim":
                dados_formulario['gtm_cs_ids'] = st.text_input("IDs do GTM Client-Side (Ex: GTM-XXXXXX):", key='k_gtm_cs_ids')
            
            gtm_ss = st.radio("Utiliza GTM Server-Side?", ("Sim", "Não"), index=None, key='k_gtm_ss')
            dados_formulario['gtm_ss'] = gtm_ss
            if gtm_ss == "Sim":
                dados_formulario['gtm_ss_server'] = st.text_input("Qual servidor utilizado para hospedar o GTM Server Side?", key='k_gtm_ss_server')
    dados_formulario['novos_caminhos'] = st.radio("O cliente autorizou novos caminhos para o domínio principal?", ("Sim", "Não"), index=None, key='k_novos_caminhos')
    if dados_formulario['gtg_implementado'] == "Não":
        dados_formulario['possible_gtg'] = st.radio("À princípio, é possível configurar o GTG?", ("Sim", "Não", "Talvez"), index=None, key='k_possible_gtg')
        dados_formulario['gtg_blocks'] = st.text_area("Quais os possíveis bloqueios para a implementação do GTG?", key='k_gtg_blocks')
    dados_formulario['obs_gtg'] = st.text_area("Observações (GTG)", key='k_obs_gtg')