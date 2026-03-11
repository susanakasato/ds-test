import streamlit as st
from services.utils import State_Keys_Map

def render_gtg_tab():
    st.header("Google Tag Gateway")
        
    st.radio("Possui GTG implementado?", ("Sim", "Não"), index=None, key=State_Keys_Map.GTG_IMPLEMENTED)
    st.text_input("Qual a CDN utilizada?", key=State_Keys_Map.CDN)
    st.radio("Utiliza IaC (Infrastructure as Code)?", ("Sim", "Não"), index=None, key=State_Keys_Map.USE_IAC)
    st.radio("Utiliza TMS?", ("Sim", "Não"), index=None, key=State_Keys_Map.USE_TMS)

    if st.session_state.get(State_Keys_Map.USE_TMS) == "Sim":
        st.selectbox("Qual TMS?", ("Selecione", "Google Tag Manager", "Tealium", "Adobe Launch", "Outros"), key=State_Keys_Map.TMS_TYPE)

        if st.session_state.get(State_Keys_Map.TMS_TYPE) == "Google Tag Manager":
            st.radio("Utiliza GTM Client-Side?", ("Sim", "Não"), index=None, key=State_Keys_Map.GTM_CS)
            if st.session_state.get(State_Keys_Map.GTM_CS) == "Sim":
                st.text_input("IDs do GTM Client-Side (Ex: GTM-XXXXXX):", key=State_Keys_Map.GTM_CS_IDS)

            st.radio("Utiliza GTM Server-Side?", ("Sim", "Não"), index=None, key=State_Keys_Map.GTM_SS)
            if st.session_state.get(State_Keys_Map.GTM_SS) == "Sim":
                st.text_input("Qual servidor utilizado para hospedar o GTM Server Side?", key=State_Keys_Map.GTM_SS_SERVER)
    st.radio("O cliente autorizou novos caminhos para o domínio principal?", ("Sim", "Não"), index=None, key=State_Keys_Map.AUTH_NEW_DOMAIN_PATH)
    if st.session_state.get(State_Keys_Map.GTG_IMPLEMENTED) == "Não":
        st.radio("À princípio, é possível configurar o GTG?", ("Sim", "Não", "Talvez"), index=None, key=State_Keys_Map.POSSIBLE_GTG)
        st.text_area("Quais os possíveis bloqueios para a implementação do GTG?", key=State_Keys_Map.GTG_BLOCKS)
    st.text_area("Observações (GTG)", key=State_Keys_Map.GTG_PS)