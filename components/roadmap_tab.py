from services.google_api import check_client_in_sheets, get_services
import streamlit as st
from services.utils import RANGE_PLANILHA
from services.utils import PLANILHA_ID

def render_roadmap_tab(cliente_nome):
    st.header("🛣️ Geração de Roadmap e Plano de Ação")
    st.markdown("Clique no botão abaixo para que o sistema analise as respostas das abas anteriores e sugira um plano de ação. **Você pode editar os textos livremente antes de gerar o documento final.**")

    # Textos padrão baseados no seu mapeamento
    txt_base_gtg = "1. Conceder acessos (4h): Fornecer acessos à plataforma CDN e os recursos necessários.\n2. Montar diagnóstico (5h): Análise técnica da estrutura atual de coleta.\n3. Montar arquitetura (4h): Criação do desenho da solução técnica.\n4. Criar documentação de implementação (5h): Documento com instruções do GTG.\n5. Implementar GTG (16h): Cliente implementa de acordo com recomendações.\n6. Validar destino de requisições (6h): Verificação da coleta de dados."
    
    txt_base_upd = "1. Conceder acessos* (4h): Garantir acessos para validação e implementação.\n2. Montar diagnóstico (5h): Análise técnica de possíveis implementações UPD.\n3. Montar arquitetura (5h): Criação do desenho da solução técnica.\n4. Mapear camada de dados* (3h): Verificar presença de informações na data layer.\n5. Doc. de implementação de camada de dados* (3h): Necessidade de implementação.\n6. Implementar camada de dados* (12h): Responsabilidade do cliente.\n7. Validar camada de dados* (3h): Validar campos mapeados.\n8. Configurar envio UPD (DP6: 4h | Cliente: 6h): Configurar GA, GAds, CM, SA.\n9. Validar envio de sinais (6h): Validações finais nas ferramentas."
    
    txt_base_oci = "1. Conceder acessos* (4h): Garantir acessos suficientes.\n2. Montar diagnóstico (5h): Análise técnica de integrações offline.\n3. Montar arquitetura (5h): Criação do desenho da solução técnica.\n4. Criar doc. de envio de sinais p/ backend (4h): Instruções para o backend.\n5. Configurar envio p/ backend (16h): Dev do cliente implementa hidden inputs.\n6. Mapear ferramentas para integrações (1h): Mapear métodos.\n7. Conceder acessos 2 (2h): Acessos de configuração OCI.\n8. Configurar integração offline (DP6: 4h | Cliente: 12h): Configuração na interface/API.\n9. Validar conversões offline (6h): Validação e criação de documento."

    if st.button("🪄 Gerar Sugestão Baseada no Diagnóstico", type="secondary"):
        # Lógica GTG
        if st.session_state.get('k_gtg') != "Sim": st.session_state['road_gtg'] = txt_base_gtg
        else: st.session_state['road_gtg'] = "Não há necessidade de roadmap para GTG. Cliente já possui implementação."
        
        # Lógica UPD (Aproximação: se GA Interface ou EC não estiverem perfeitamente preenchidos)
        precisa_upd = False
        if st.session_state.get('k_ga_config') != 'Sim' and st.session_state.get('k_ga_hard') != 'Sim': precisa_upd = True
        if not st.session_state.get('k_ec_plats') and st.session_state.get('k_ec_hard') != 'Sim': precisa_upd = True
        
        if precisa_upd: st.session_state['road_upd'] = txt_base_upd
        else: st.session_state['road_upd'] = "Não há necessidade de roadmap para UPD. Cliente já atende os requisitos."

        # Lógica OCI
        if st.session_state.get('k_oci_impl') != "Sim": st.session_state['road_oci'] = txt_base_oci
        else: st.session_state['road_oci'] = "Não há necessidade de roadmap para OCI. Cliente já atende os requisitos."

    # Caixas de texto editáveis (O usuário pode alterar o texto livremente aqui)
    roadmap_gtg = st.text_area("Plano de Ação - Google Tag Gateway", value=st.session_state.get('road_gtg', ''), height=150)
    roadmap_upd = st.text_area("Plano de Ação - Envio de Sinais (UPD)", value=st.session_state.get('road_upd', ''), height=200)
    roadmap_oci = st.text_area("Plano de Ação - OCI Upgrade", value=st.session_state.get('road_oci', ''), height=200)

    # Botão independente para gerar APENAS o documento de Roadmap
    if st.button("📄 Gerar e Salvar Documento de Roadmap", type="primary"):
        if not cliente_nome or cliente_nome == "✨ Cadastrar Novo Cliente...":
            st.error("Selecione um cliente válido no topo da página primeiro.")
        elif not roadmap_gtg and not roadmap_upd and not roadmap_oci:
            st.warning("Gere a sugestão ou digite algo no roadmap antes de criar o documento.")
        else:
            with st.spinner("Gerando documento de Roadmap..."):
                try:
                    # Importa a função (Certifique-se de adicionar 'create_roadmap_doc' nos imports do topo do app.py!)
                    from services.google_api import create_roadmap_doc 
                    
                    sheets_service, docs_service, drive_service = get_services()
                    _, pasta_cliente_id, _, _ = check_client_in_sheets(sheets_service, PLANILHA_ID, RANGE_PLANILHA, cliente_nome, -1)
                    
                    if not pasta_cliente_id:
                        st.error("Pasta do cliente não encontrada. Salve o diagnóstico primeiro para criar a estrutura do cliente no Drive.")
                    else:
                        doc_id, doc_url, pdf_url = create_roadmap_doc(
                            docs_service, drive_service, cliente_nome, pasta_cliente_id, roadmap_gtg, roadmap_upd, roadmap_oci
                        )
                        st.session_state['k_doc_url'] = doc_url
                        st.session_state['k_pdf_url'] = pdf_url
                        st.success("Documento de Roadmap gerado com sucesso!")
                        colA, colB = st.columns(2)
                        with colA: st.link_button("➡️ Abrir Roadmap (Docs)", st.session_state['k_doc_url'], use_container_width=True)
                        with colB: st.link_button("⬇️ Baixar Roadmap (PDF)", st.session_state['k_pdf_url'], use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao gerar roadmap: {e}")