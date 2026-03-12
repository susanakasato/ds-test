import streamlit as st # pyright: ignore[reportMissingImports]
from services.utils import State_Keys_Map

def render_gtg_tab():
    st.radio("Possui GTG implementado?", ("Sim", "Não"), index=None, key=State_Keys_Map.GTG_IMPLEMENTED.value)
    st.text_input("Qual a CDN utilizada?", key=State_Keys_Map.CDN.value)
    st.radio("Utiliza IaC (Infrastructure as Code)?", ("Sim", "Não"), index=None, key=State_Keys_Map.USE_IAC.value)
    st.radio("Utiliza TMS?", ("Sim", "Não"), index=None, key=State_Keys_Map.USE_TMS.value)

    if State_Keys_Map.USE_TMS.st_state == "Sim":
        st.selectbox("Qual TMS?", ("Selecione", "Google Tag Manager", "Tealium", "Adobe Launch", "Outros"), key=State_Keys_Map.TMS_TYPE.value)

        if State_Keys_Map.TMS_TYPE.st_state == "Google Tag Manager":
            st.radio("Utiliza GTM Client-Side?", ("Sim", "Não"), index=None, key=State_Keys_Map.USE_GTM_CS.value)
            if State_Keys_Map.USE_GTM_CS.st_state == "Sim":
                st.text_input("IDs do GTM Client-Side (Ex: GTM-XXXXXX):", key=State_Keys_Map.GTM_CS_IDS.value)

            st.radio("Utiliza GTM Server-Side?", ("Sim", "Não"), index=None, key=State_Keys_Map.USE_GTM_SS.value)
            if State_Keys_Map.USE_GTM_SS.st_state == "Sim":
                st.text_input("Qual servidor utilizado para hospedar o GTM Server Side?", key=State_Keys_Map.GTM_SS_SERVER.value)
    st.radio("O cliente autorizou novos caminhos para o domínio principal?", ("Sim", "Não"), index=None, key=State_Keys_Map.AUTH_NEW_DOMAIN_PATH.value)
    if State_Keys_Map.GTG_IMPLEMENTED.st_state == "Não":
        st.radio("À princípio, é possível configurar o GTG?", ("Sim", "Não", "Talvez"), index=None, key=State_Keys_Map.POSSIBLE_GTG.value)
        st.text_area("Quais os possíveis bloqueios para a implementação do GTG?", key=State_Keys_Map.GTG_BLOCKS.value)
    st.text_area("Observações (GTG)", key=State_Keys_Map.GTG_PS.value)