import streamlit as st
from enum import Enum
from components.gtg_tab import render_gtg_tab
from components.upd_tab import render_upd_tab
from components.oci_tab import render_oci_tab
from services.google_api import check_client_in_sheets, create_drive_folder, create_update_diagnostic_doc, download_image_from_drive, get_services, save_to_sheets, upload_image_to_drive
from services.utils import PARENT_FOLDER_ID, PLANILHA_ID, RANGE_PLANILHA, RANGE_PLANILHA_WIDTH, Diagnosis_Headers, get_column_index_from_diagnosis_db, update_lista_clientes

def render_diagnosis_tab(cliente_nome):
    # Criação das Abas
    gtg_tab, upd_tab, oci_tab = st.tabs(["🌐 Google Tag Gateway", "📡 Envio de Sinais UPD", "⚙️ OCI Upgrade"])

    dados_formulario = {"cliente": cliente_nome}

    with gtg_tab:
        render_gtg_tab(dados_formulario)
    with upd_tab:
        render_upd_tab(dados_formulario)
    with oci_tab:
        render_oci_tab(dados_formulario)

    # ==========================================
    # BOTÃO DE SUBMISSÃO E FLUXO DE DADOS
    # ==========================================
    st.divider()
    if st.button("💾 Salvar e Gerar Documento de Diagnóstico", type="primary", use_container_width=True):
        print(f"primeir: {cliente_nome}")
        print(f"segundo: {st.session_state.get('k_client')}")
        if not cliente_nome:
            st.error("Por favor, preencha o nome do cliente antes de salvar.")
        else:
            print("Conectando ao Google")
            with st.spinner("Conectando ao Google Workspace..."):
                try:
                    # 1. Inicializa os serviços
                    sheets_service, docs_service, drive_service = get_services()
                    
                    # ID da sua planilha no Google Sheets (pegue da URL da planilha)

                    NOME_CLIENTE = dados_formulario['cliente']

                    # 1. Verifica se o cliente existe no Sheets
                    linha_cliente, pasta_cliente_id, doc_id, _, _ = check_client_in_sheets(
                        sheets_service, PLANILHA_ID, RANGE_PLANILHA, NOME_CLIENTE
                    )

                    # 2. Se não existir, cria a nova pasta no Drive
                    if pasta_cliente_id is None:
                        pasta_cliente_id = create_drive_folder(drive_service, NOME_CLIENTE, PARENT_FOLDER_ID)


                    # NOVA FUNÇÃO: Decide se faz upload de novas imagens ou se baixa as antigas para o Docx
                    def processar_ou_resgatar_imagens(lista_arquivos_novos, nome_secao, links_existentes):
                        urls_finais = []
                        raw_images_para_docx = []

                        old_links_quantity = len([l.strip() for l in links_existentes.split('\n') if l.strip()]) if links_existentes else 0
                        
                        # 1. Se o usuário enviou imagens NOVAS no formulário:
                        if lista_arquivos_novos: 
                            for idx, img_file in enumerate(lista_arquivos_novos):
                                st.info(f"Salvando imagem {idx+1} de {nome_secao} no Drive...")
                                img_file.seek(0)
                                raw_images_para_docx.append(img_file) # Envia para o Docx
                                
                                extensao = img_file.name.split('.')[-1]
                                nome_arquivo = f"{cliente_nome} - {nome_secao} - {old_links_quantity+idx+1}.{extensao}"
                                _, link = upload_image_to_drive(drive_service, img_file, nome_arquivo, folder_id=pasta_cliente_id)
                                urls_finais.append(link)
                        
                        # 2. Se NÃO há imagens novas, mas JÁ EXISTEM links antigos salvos no Sheets:
                        if old_links_quantity > 0:
                            links = [l.strip() for l in links_existentes.split('\n') if l.strip()]
                            for idx, link in enumerate(links):
                                try:
                                    # Extrai o File ID do link do Google Drive (ex: https://drive.google.com/file/d/ID_AQUI/view)
                                    if '/d/' in link:
                                        file_id = link.split('/d/')[1].split('/')[0]
                                        # Faz o download da imagem para a memória e envia para o Docx
                                        img_bytes = download_image_from_drive(drive_service, file_id)
                                        raw_images_para_docx.append(img_bytes)
                                        urls_finais.append(link) # Mantém o link antigo para salvar novamente no Sheets
                                except Exception as e:
                                    print(f"Erro ao baixar imagem antiga {link}: {e}")
                                    
                            # Mantém os links antigos intactos para não apagar do Sheets
                        return '\n'.join(urls_finais), raw_images_para_docx

                    # Executa a inteligência para as 4 sessões de imagens
                    link_ga4, raw_ga4 = processar_ou_resgatar_imagens(st.session_state.get('img_ga4'), "GA4 UPD", st.session_state.get('existing_img_ga4'))
                    link_ec, raw_ec   = processar_ou_resgatar_imagens(st.session_state.get('img_ec'), "EC", st.session_state.get('existing_img_ec'))
                    link_ecl, raw_ecl = processar_ou_resgatar_imagens(st.session_state.get('img_ecl'), "ECL", st.session_state.get('existing_img_ecl'))
                    link_oci, raw_oci = processar_ou_resgatar_imagens(st.session_state.get('img_oci'), "OCI", st.session_state.get('existing_img_oci'))
                    link_upd, raw_upd = processar_ou_resgatar_imagens(st.session_state.get('img_upd'), "UPD", st.session_state.get('existing_img_upd'))

                    # Salva os resultados no dados_formulario para a criação do Doc e da linha do Sheets
                    dados_formulario['link_img_ga4'] = link_ga4
                    dados_formulario['link_img_ec']  = link_ec
                    dados_formulario['link_img_ecl'] = link_ecl
                    dados_formulario['link_img_oci'] = link_oci
                    dados_formulario['link_img_upd'] = link_upd
                    
                    dados_formulario['raw_img_ga4'] = raw_ga4
                    dados_formulario['raw_img_ec']  = raw_ec
                    dados_formulario['raw_img_ecl'] = raw_ecl
                    dados_formulario['raw_img_oci'] = raw_oci
                    dados_formulario['raw_img_upd'] = raw_upd

                    # Função auxiliar para formatar listas (multiselect) como texto separado por vírgula
                    def formatar_lista(item):
                        if isinstance(item, list):
                            return "\n".join(item)
                        return str(item) if item else ""
                    
                    # 2. Transforma o dicionário em uma lista (linha) para o Sheets
                    linha_dados = [None] * RANGE_PLANILHA_WIDTH
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.CLIENT)] = cliente_nome # Preenche o nome do cliente na coluna A (Nome)
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_IMPLEMENTED)] = formatar_lista(dados_formulario.get('gtg_implementado'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.CDN)] = formatar_lista(dados_formulario.get('cdn'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_IAC)] = formatar_lista(dados_formulario.get('iac'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_TMS)] = formatar_lista(dados_formulario.get('usa_tms'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.TMS_TYPE)] = formatar_lista(dados_formulario.get('tms_type'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_GTM_CS)] = formatar_lista(dados_formulario.get('gtm_cs'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_CS_IDS)] = formatar_lista(dados_formulario.get('gtm_cs_ids'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_GTM_SS)] = formatar_lista(dados_formulario.get('gtm_ss'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_SS_SERVER)] = formatar_lista(dados_formulario.get('gtm_ss_server'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.AUTH_NEW_DOMAIN_PATH)] = formatar_lista(dados_formulario.get('novos_caminhos'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.POSSIBLE_GTG)] = formatar_lista(dados_formulario.get('possible_gtg'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_BLOCKS)] = formatar_lista(dados_formulario.get('gtg_blocks'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_GTG)] = formatar_lista(dados_formulario.get('obs_gtg'))

                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_ANALYSIS)] = formatar_lista(dados_formulario.get('gtm_analise'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.URLS_FORMS)] = formatar_lista(dados_formulario.get('urls_forms'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.UPD_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_upd'))

                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_CONFIG)] = formatar_lista(dados_formulario.get('ga_platform'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_HARDCODED)] = formatar_lista(dados_formulario.get('ga_hardcoded'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_ga4'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('ga_upd_possible_config'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_BLOCKS)] = formatar_lista(dados_formulario.get('ga_upd_blocks'))

                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_PLATFORMS)] = formatar_lista(dados_formulario.get('ec_platforms'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_HARDCODED)] = formatar_lista(dados_formulario.get('ec_hardcoded'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_ec'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('ec_possible_config'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_BLOCKS)] = formatar_lista(dados_formulario.get('ec_blocks'))

                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_PLATFORMS)] = formatar_lista(dados_formulario.get('ecl_platforms'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_HARDCODED)] = formatar_lista(dados_formulario.get('ecl_hardcoded'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_ecl'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('ecl_possible_config'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_BLOCKS)] = formatar_lista(dados_formulario.get('ecl_blocks'))

                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_SIGNALS)] = formatar_lista(dados_formulario.get('obs_upd'))

                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_IMPLEMENTED)] = formatar_lista(dados_formulario.get('oci_implementado'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_PLATFORM)] = formatar_lista(dados_formulario.get('oci_platform'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_METHOD)] = formatar_lista(dados_formulario.get('oci_metodo'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_INFOS)] = formatar_lista(dados_formulario.get('oci_infos'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_oci'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('oci_possible_config'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_BLOCKS)] = formatar_lista(dados_formulario.get('oci_blocks'))
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_OCI)] = formatar_lista(dados_formulario.get('obs_oci'))

 
                    # 3. Cria o documento já jogando para dentro da pasta certa
                    st.info("Gerando o documento de diagnóstico...")
                    doc_id, doc_url, pdf_url = create_update_diagnostic_doc(
                        drive_service, NOME_CLIENTE, dados_formulario, pasta_cliente_id, doc_id
                    )
                    st.session_state['k_diagnosis_doc_url'] = doc_url
                    st.session_state['k_diagnosis_pdf_url'] = pdf_url

                    # linha_dados[29] = doc_id  # Coluna AD: ID do Documento
                    # linha_dados[30] = pasta_cliente_id  # Coluna AE: ID da
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.DIAGNOSIS_DOC_ID)] = doc_id
                    linha_dados[get_column_index_from_diagnosis_db(Diagnosis_Headers.DRIVE_ID)] = pasta_cliente_id

                    # 3. Salva no Sheets e verifica se tinha doc antigo
                    st.info("Atualizando Banco de Dados (Sheets)...")
                    save_to_sheets(sheets_service, PLANILHA_ID, RANGE_PLANILHA, linha_cliente, linha_dados)

                    st.success(f"Diagnóstico para {cliente_nome} salvo com sucesso!")

                    update_lista_clientes()
                    

                        
                except Exception as e:
                    st.error(f"Erro ao processar integração com Google: {e}")
    if st.session_state.get('k_diagnosis_doc_url') and st.session_state.get('k_diagnosis_pdf_url'):
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("➡️ Abrir Google Docs", st.session_state.get('k_diagnosis_doc_url'), use_container_width=True)
        with col2:
            st.link_button("⬇️ Baixar PDF", st.session_state.get('k_diagnosis_pdf_url'), use_container_width=True)