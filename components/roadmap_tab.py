from services.google_api import check_client_in_sheets, get_doc_content, get_services, create_roadmap_doc, save_to_sheets
import streamlit as st
from services.utils import RANGE_PLANILHA, PLANILHA_ID, get_column_index_from_diagnosis_db, Diagnosis_Headers
from services.ia_service import gerar_roadmap_ia # <-- IMPORTAR O NOVO SERVIÇO

def activity_to_text(activity_list):
    result = []
    for index, activity in enumerate(activity_list):
        if "activity" in activity and "description" in activity:
            result.append(f"{index+1}. {activity['activity']}: {activity['description']}")
    return "\n".join(result)

def render_roadmap_tab(client):
    sheets_service, docs_service, drive_service = get_services()
    st.header("🛣️ Geração de Roadmap e Plano de Ação")
    st.markdown("Selecione o cliente e clique no botão abaixo para que o sistema analise o diagnóstico e sugira um plano de ação usando Inteligência Artificial. **Você pode editar os textos livremente antes de gerar o documento final.**")

    # BOTÃO COM INTELIGÊNCIA ARTIFICIAL
    if st.button("🪄 Gerar Roadmap", type="secondary"):
        # client = st.session_state.get('k_client')
        with st.spinner(f"🧠 A IA está analisando o diagnóstico de {client} e cruzando com as atividades mapeadas..."):
            
            # 1. Coletar o contexto atual do formulário/sessão
            # diagnosis_data = {
            #     # GTG
            #     "client": cliente_nome,
            #     "gtg_implemented": st.session_state.get('k_gtg'),
            #     "cdn": st.session_state.get('k_cdn'),
            #     "use_iac": st.session_state.get('k_iac'),
            #     "use_tms": st.session_state.get('k_usa_tms'),
            #     "tms_type": st.session_state.get('k_tms_type'),
            #     "gtm_cs": st.session_state.get('k_gtm_cs'),
            #     "gtm_cs_ids": st.session_state.get('k_gtm_cs_ids'),
            #     "gtm_ss": st.session_state.get('k_gtm_ss'),
            #     "gtm_ss_server": st.session_state.get('k_gtm_ss_server'),
            #     "auth_new_path": st.session_state.get('k_novos_caminhos'),
            #     "gtg_implementation_possibility": st.session_state.get('k_possible_gtg'),
            #     "gtg_blocks": st.session_state.get("k_gtg_blocks"),
            #     "gtg_ps": st.session_state.get("k_obs_gtg"),

            #     # SIGNALS GA
            #     "gtm_analysis": st.session_state.get('k_gtm_analysis'),
            #     "urls_forms": st.session_state.get('k_urls_forms'),
            #     "ga_setup": st.session_state.get('k_ga_config'),
            #     "ga_hardcoded": st.session_state.get('k_ga_hard'),
            #     "ga_upd_implementation_possibility": st.session_state.get('k_ga_upd_possible_config'),
            #     "ga_upd_blocks": st.session_state.get('k_ga_upd_blocks'),

            #     # SINGALS - EC
            #     "ec_plataformas": st.session_state.get('k_ec_platforms'),
            #     "ec_google_ads_setup": st.session_state.get('k_ec_platform_gads'),
            #     "ec_search_ads_setup": st.session_state.get('k_ec_platform_sa'),
            #     "ec_campaign_manager_setup": st.session_state.get('k_ec_platform_cm'),
            #     "ec_hardcoded": st.session_state.get('k_ec_hard'),
            #     "ec_implementation_possibility": st.session_state.get('k_ec_possible_config'),
            #     "ec_blocks": st.session_state.get('k_ec_blocks'),

            #     # SIGNALS - ECL
            #     "ecl_platforms": st.session_state.get("k_ecl_platforms"),
            #     "ecl_google_ads_setup": st.session_state.get('k_ecl_platform_gads'),
            #     "ecl_search_ads_setup": st.session_state.get('k_ecl_platform_sa'),
            #     "ecl_campaign_manager_setup": st.session_state.get('k_ecl_platform_cm'),
            #     "ecl_hardcoded": st.session_state.get('k_ecl_hard'),
            #     "ecl_implementation_possibility": st.session_state.get('k_ecl_possible_config'),
            #     "ecl_blocks": st.session_state.get('k_ecl_blocks'),

            #     "upd_ps": st.session_state.get('k_obs_upd'),

            #     # SIGNALS - OCI
            #     "oci_setup": st.session_state.get('k_oci_impl'),
            #     "oci_setup_on_platform": st.session_state.get('k_oci_platform'),
            #     "oci_setup_method": st.session_state.get('k_oci_method'),
            #     "oci_match_infos": st.session_state.get('k_oci_method'),
            #     "oci_implementation_possibility": st.session_state.get('k_oci_possible_config'),
            #     "oci_blocks": st.session_state.get('k_oci_blocks'),
            #     "oci_ps": st.session_state.get("k_obs_oci"),

            # }
            doc_id = st.session_state.get('k_diagnosis_doc_id')
            diagnosis_data = get_doc_content(docs_service, doc_id)

            # 2. Chamar a IA
            roadmap_gerado = gerar_roadmap_ia(diagnosis_data)

            if roadmap_gerado:
                # 3. Atualizar o Session State com a resposta da IA
                st.session_state['k_gtg_roadmap'] = activity_to_text(roadmap_gerado.get("roadmap_gtg", []))
                st.session_state['k_upd_roadmap'] = activity_to_text(roadmap_gerado.get("roadmap_upd", []))
                st.session_state['k_oci_roadmap'] = activity_to_text(roadmap_gerado.get("roadmap_oci", []))
                st.success("✨ Roadmap gerado com sucesso!")

    # Caixas de texto editáveis (Lê do session_state populado pela IA)
    roadmap_gtg = st.text_area("Plano de Ação - Google Tag Gateway", value=st.session_state.get('road_gtg', ''), height=250, key='k_gtg_roadmap')
    roadmap_upd = st.text_area("Plano de Ação - Envio de Sinais (UPD)", value=st.session_state.get('road_upd', ''), height=250, key='k_upd_roadmap')
    roadmap_oci = st.text_area("Plano de Ação - OCI Upgrade", value=st.session_state.get('road_oci', ''), height=250, key='k_oci_roadmap')
    roadmap_data = {
        "gtg": roadmap_gtg,
        "upd": roadmap_upd,
        "oci": roadmap_oci
    }

    # Botão independente para gerar APENAS o documento de Roadmap
    if st.button("📄 Salvar e Gerar Documento de Roadmap", type="primary", use_container_width=True):
        if not client or client == "✨ Cadastrar Novo Cliente...":
            st.error("Selecione um cliente válido no topo da página primeiro.")
        elif not roadmap_gtg and not roadmap_upd and not roadmap_oci:
            st.warning("Gere a sugestão ou digite algo no roadmap antes de criar o documento.")
        else:
            with st.spinner("Salvando dados e gerando documento de Roadmap..."):
                try:
                    # Importa a função (Certifique-se de adicionar 'create_roadmap_doc' nos imports do topo do app.py!)
                    client_sheets_row, client_folder_id, _, doc_id, data = check_client_in_sheets(sheets_service, PLANILHA_ID, RANGE_PLANILHA, client)
                    
                    if not client_folder_id:
                        st.error("Pasta do cliente não encontrada. Salve o diagnóstico primeiro para criar a estrutura do cliente no Drive.")
                    else:
                        doc_id, doc_url, pdf_url = create_roadmap_doc(
                            drive_service, client, client_folder_id, roadmap_data, doc_id
                        )
                        data[get_column_index_from_diagnosis_db(Diagnosis_Headers.ROADMAP_DOC_ID)] = doc_id
                        data[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_ROADMAP)] = roadmap_gtg
                        data[get_column_index_from_diagnosis_db(Diagnosis_Headers.UPD_ROADMAP)] = roadmap_upd
                        data[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_ROADMAP)] = roadmap_oci

                        save_to_sheets(sheets_service, PLANILHA_ID, RANGE_PLANILHA, client_sheets_row, data)

                        st.session_state['k_roadmap_doc_url'] = doc_url
                        st.session_state['k_roadmap_pdf_url'] = pdf_url
                        st.success("Documento de Roadmap gerado com sucesso!")
                        colA, colB = st.columns(2)
                        with colA: 
                            st.link_button("➡️ Abrir Roadmap (Docs)", st.session_state['k_roadmap_doc_url'], use_container_width=True)
                        with colB: 
                            st.link_button("⬇️ Baixar Roadmap (PDF)", st.session_state['k_roadmap_pdf_url'], use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao gerar roadmap: {e}")