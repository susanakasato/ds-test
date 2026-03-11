import streamlit as st # pyright: ignore[reportMissingImports]
from components.gtg_tab import render_gtg_tab
from components.upd_tab import render_upd_tab
from components.oci_tab import render_oci_tab
from services.google_api import check_client_in_sheets, create_drive_folder, create_update_diagnostic_doc, download_image_from_drive, get_services, save_to_sheets, upload_image_to_drive
from services.utils import PARENT_FOLDER_ID, SHEETS_ID, SHEETS_RANGE, SHEETS_RANGE_WIDTH, Headers_Map, State_Keys_Map, format_list, get_sheet_column_index, update_client_list

def process_or_get_images(new_files_list, section_name, existing_links):
    _, _, drive_service = get_services()
    final_urls = []
    raw_images_for_docx = []

    old_links_quantity = len([l.strip() for l in existing_links.split('\n') if l.strip()]) if existing_links else 0
    
    # 1. Se o usuário enviou imagens NOVAS no formulário:
    if new_files_list: 
        for idx, img_file in enumerate(new_files_list):
            st.info(f"Salvando imagem {idx+1} de {section_name} no Drive...")
            img_file.seek(0)
            raw_images_for_docx.append(img_file) # Envia para o Docx
            
            extensao = img_file.name.split('.')[-1]
            nome_arquivo = f"{st.session_state.get(State_Keys_Map.CLIENT)} - {section_name} - {old_links_quantity+idx+1}.{extensao}"
            _, link = upload_image_to_drive(drive_service, img_file, nome_arquivo, folder_id=st.session_state.get(State_Keys_Map.CLIENT_FOLDER_ID))
            final_urls.append(link)
    
    # 2. Se NÃO há imagens novas, mas JÁ EXISTEM links antigos salvos no Sheets:
    if old_links_quantity > 0:
        links = [l.strip() for l in existing_links.split('\n') if l.strip()]
        for idx, link in enumerate(links):
            try:
                # Extrai o File ID do link do Google Drive (ex: https://drive.google.com/file/d/ID_AQUI/view)
                if '/d/' in link:
                    file_id = link.split('/d/')[1].split('/')[0]
                    # Faz o download da imagem para a memória e envia para o Docx
                    img_bytes = download_image_from_drive(drive_service, file_id)
                    raw_images_for_docx.append(img_bytes)
                    final_urls.append(link) # Mantém o link antigo para salvar novamente no Sheets
            except Exception as e:
                print(f"Erro ao baixar imagem antiga {link}: {e}")
                
        # Mantém os links antigos intactos para não apagar do Sheets
    return '\n'.join(final_urls), raw_images_for_docx

def render_diagnosis_tab():
    # Criação das Abas
    gtg_tab, upd_tab, oci_tab = st.tabs(["🌐 Google Tag Gateway", "📡 Envio de Sinais UPD", "⚙️ OCI Upgrade"])

    with gtg_tab:
        render_gtg_tab()
    with upd_tab:
        render_upd_tab()
    with oci_tab:
        render_oci_tab()

    st.divider()
    if st.button("💾 Salvar e Gerar Documento de Diagnóstico", type="primary", use_container_width=True):
        if not st.session_state.get('form_client'):
            st.error("Por favor, preencha o nome do cliente antes de salvar.")
        else:
            with st.spinner("Conectando ao Google Workspace..."):
                try:
                    sheets_service, _, drive_service = get_services()
                    client_row, client_folder_id, diagnosis_doc_ud, _, _ = check_client_in_sheets(sheets_service, SHEETS_ID, SHEETS_RANGE, st.session_state.get('form_client'))
                    if client_folder_id is None:
                        client_folder_id = create_drive_folder(drive_service, st.session_state.get('form_client'), PARENT_FOLDER_ID)

                    # Executa a inteligência para as 4 sessões de imagens
                    link_ga4, raw_ga4 = process_or_get_images(st.session_state.get(State_Keys_Map.GA_IMG_FORM), "GA4 UPD", st.session_state.get(State_Keys_Map.GA_IMG_LINKS))
                    link_ec,  raw_ec  = process_or_get_images(st.session_state.get(State_Keys_Map.EC_IMG_FORM), "EC", st.session_state.get(State_Keys_Map.EC_IMG_LINKS))
                    link_ecl, raw_ecl = process_or_get_images(st.session_state.get(State_Keys_Map.ECL_IMG_FORM), "ECL", st.session_state.get(State_Keys_Map.ECL_IMG_LINKS))
                    link_oci, raw_oci = process_or_get_images(st.session_state.get(State_Keys_Map.OCI_IMG_FORM), "OCI", st.session_state.get(State_Keys_Map.OCI_IMG_LINKS))
                    link_upd, raw_upd = process_or_get_images(st.session_state.get(State_Keys_Map.UPD_IMG_FORM), "UPD", st.session_state.get(State_Keys_Map.UPD_IMG_LINKS))

                    # Salva os resultados no dados_formulario para a criação do Doc e da linha do Sheets
                    st.session_state[State_Keys_Map.GA_IMG_LINKS] = link_ga4
                    st.session_state[State_Keys_Map.EC_IMG_LINKS]  = link_ec
                    st.session_state[State_Keys_Map.ECL_IMG_LINKS] = link_ecl
                    st.session_state[State_Keys_Map.OCI_IMG_LINKS] = link_oci
                    st.session_state[State_Keys_Map.UPD_IMG_LINKS] = link_upd
                    
                    st.session_state[State_Keys_Map.GA_IMG_RAW] = raw_ga4
                    st.session_state[State_Keys_Map.EC_IMG_RAW]  = raw_ec
                    st.session_state[State_Keys_Map.ECL_IMG_RAW] = raw_ecl
                    st.session_state[State_Keys_Map.OCI_IMG_RAW] = raw_oci
                    st.session_state[State_Keys_Map.UPD_IMG_RAW] = raw_upd

                    # 2. Transforma o dicionário em uma lista (linha) para o Sheets
                    sheets_data = [None] * SHEETS_RANGE_WIDTH
                    sheets_data[get_sheet_column_index(Headers_Map.CLIENT)] = st.session_state.get(State_Keys_Map.CLIENT)
                    sheets_data[get_sheet_column_index(Headers_Map.GTG_IMPLEMENTED)] = st.session_state.get(State_Keys_Map.GTG_IMPLEMENTED)
                    sheets_data[get_sheet_column_index(Headers_Map.CDN)] = format_list(st.session_state.get(State_Keys_Map.CDN))
                    sheets_data[get_sheet_column_index(Headers_Map.USE_IAC)] = format_list(st.session_state.get(State_Keys_Map.USE_IAC))
                    sheets_data[get_sheet_column_index(Headers_Map.USE_TMS)] = format_list(st.session_state.get(State_Keys_Map.USE_TMS))
                    sheets_data[get_sheet_column_index(Headers_Map.TMS_TYPE)] = format_list(st.session_state.get(State_Keys_Map.TMS_TYPE))
                    sheets_data[get_sheet_column_index(Headers_Map.USE_GTM_CS)] = format_list(st.session_state.get(State_Keys_Map.USE_GTM_CS))
                    sheets_data[get_sheet_column_index(Headers_Map.GTM_CS_IDS)] = format_list(st.session_state.get(State_Keys_Map.GTM_CS_IDS))
                    sheets_data[get_sheet_column_index(Headers_Map.USE_GTM_SS)] = format_list(st.session_state.get(State_Keys_Map.USE_GTM_SS))
                    sheets_data[get_sheet_column_index(Headers_Map.GTM_SS_SERVER)] = format_list(st.session_state.get(State_Keys_Map.GTM_SS_SERVER))
                    sheets_data[get_sheet_column_index(Headers_Map.AUTH_NEW_DOMAIN_PATH)] = format_list(st.session_state.get(State_Keys_Map.AUTH_NEW_DOMAIN_PATH))
                    sheets_data[get_sheet_column_index(Headers_Map.POSSIBLE_GTG)] = format_list(st.session_state.get(State_Keys_Map.POSSIBLE_GTG))
                    sheets_data[get_sheet_column_index(Headers_Map.GTG_BLOCKS)] = format_list(st.session_state.get(State_Keys_Map.GTG_BLOCKS))
                    sheets_data[get_sheet_column_index(Headers_Map.GTG_PS)] = format_list(st.session_state.get(State_Keys_Map.GTG_PS))

                    sheets_data[get_sheet_column_index(Headers_Map.GTM_ANALYSIS)] = format_list(st.session_state.get(State_Keys_Map.GTM_ANALYSIS))
                    sheets_data[get_sheet_column_index(Headers_Map.URLS_FORMS)] = format_list(st.session_state.get(State_Keys_Map.FORM_URLS))
                    sheets_data[get_sheet_column_index(Headers_Map.UPD_IMG_LINKS)] = format_list(st.session_state.get(State_Keys_Map.UPD_IMG_LINKS))
                    sheets_data[get_sheet_column_index(Headers_Map.UPD_PS)] = format_list(st.session_state.get(State_Keys_Map.UPD_PS))

                    sheets_data[get_sheet_column_index(Headers_Map.GA_UPD_CONFIG)] = format_list(st.session_state.get(State_Keys_Map.GA_UPD_CONFIG))
                    sheets_data[get_sheet_column_index(Headers_Map.GA_HARDCODED)] = format_list(st.session_state.get(State_Keys_Map.GA_HARDCODED))
                    sheets_data[get_sheet_column_index(Headers_Map.GA_IMG_LINKS)] = format_list(st.session_state.get(State_Keys_Map.GA_IMG_LINKS))
                    sheets_data[get_sheet_column_index(Headers_Map.GA_UPD_POSSIBLE_CONFIG)] = format_list(st.session_state.get(State_Keys_Map.GA_UPD_POSSIBLE_CONFIG))
                    sheets_data[get_sheet_column_index(Headers_Map.GA_UPD_BLOCKS)] = format_list(st.session_state.get(State_Keys_Map.GA_UPD_BLOCKS))

                    sheets_data[get_sheet_column_index(Headers_Map.EC_PLATFORMS)] = format_list(st.session_state.get(State_Keys_Map.EC_PLATFORMS))
                    sheets_data[get_sheet_column_index(Headers_Map.EC_HARDCODED)] = format_list(st.session_state.get(State_Keys_Map.EC_HARDCODED))
                    sheets_data[get_sheet_column_index(Headers_Map.EC_IMG_LINKS)] = format_list(st.session_state.get(State_Keys_Map.EC_IMG_LINKS))
                    sheets_data[get_sheet_column_index(Headers_Map.EC_POSSIBLE_CONFIG)] = format_list(st.session_state.get(State_Keys_Map.EC_POSSIBLE_CONFIG))
                    sheets_data[get_sheet_column_index(Headers_Map.EC_BLOCKS)] = format_list(st.session_state.get(State_Keys_Map.EC_BLOCKS))

                    sheets_data[get_sheet_column_index(Headers_Map.ECL_PLATFORMS)] = format_list(st.session_state.get(State_Keys_Map.ECL_PLATFORMS))
                    sheets_data[get_sheet_column_index(Headers_Map.ECL_HARDCODED)] = format_list(st.session_state.get(State_Keys_Map.ECL_HARDCODED))
                    sheets_data[get_sheet_column_index(Headers_Map.ECL_IMG_LINKS)] = format_list(st.session_state.get(State_Keys_Map.ECL_IMG_LINKS))
                    sheets_data[get_sheet_column_index(Headers_Map.ECL_POSSIBLE_CONFIG)] = format_list(st.session_state.get(State_Keys_Map.ECL_POSSIBLE_CONFIG))
                    sheets_data[get_sheet_column_index(Headers_Map.ECL_BLOCKS)] = format_list(st.session_state.get(State_Keys_Map.ECL_BLOCKS))


                    sheets_data[get_sheet_column_index(Headers_Map.OCI_IMPLEMENTED)] = format_list(st.session_state.get(State_Keys_Map.OCI_IMPLEMENTED))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_PLATFORM)] = format_list(st.session_state.get(State_Keys_Map.OCI_PLATFORM))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_METHOD)] = format_list(st.session_state.get(State_Keys_Map.OCI_METHOD))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_INFOS)] = format_list(st.session_state.get(State_Keys_Map.OCI_INFOS))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_IMG_LINKS)] = format_list(st.session_state.get(State_Keys_Map.OCI_IMG_LINKS))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_POSSIBLE_CONFIG)] = format_list(st.session_state.get(State_Keys_Map.OCI_POSSIBLE_CONFIG))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_BLOCKS)] = format_list(st.session_state.get(State_Keys_Map.OCI_BLOCKS))
                    sheets_data[get_sheet_column_index(Headers_Map.OCI_PS)] = format_list(st.session_state.get(State_Keys_Map.OCI_PS))

                    data_for_docx = {}
                    for key in State_Keys_Map:
                        data_for_docx[key.value] = st.session_state.get(key.value)

                    # 3. Cria o documento já jogando para dentro da pasta certa
                    st.info("Gerando o documento de diagnóstico...")
                    diagnosis_doc_id, doc_url, pdf_url = create_update_diagnostic_doc(
                        drive_service, st.session_state.get(State_Keys_Map.CLIENT), data_for_docx, client_folder_id, diagnosis_doc_id
                    )
                    st.session_state[State_Keys_Map.DIAGNOSIS_DOC_URL] = doc_url
                    st.session_state[State_Keys_Map.DIAGNOSIS_PDF_URL] = pdf_url

                    # sheets_data[29] = diagnosis_doc_id  # Coluna AD: ID do Documento
                    # sheets_data[30] = client_folder_id  # Coluna AE: ID da
                    sheets_data[get_sheet_column_index(Headers_Map.DIAGNOSIS_diagnosis_doc_id)] = diagnosis_doc_id
                    sheets_data[get_sheet_column_index(Headers_Map.DRIVE_ID)] = client_folder_id

                    # 3. Salva no Sheets e verifica se tinha doc antigo
                    st.info("Atualizando Banco de Dados (Sheets)...")
                    save_to_sheets(sheets_service, SHEETS_ID, SHEETS_RANGE, client_row, sheets_data)

                    st.success(f"Diagnóstico para {st.session_state.get(State_Keys_Map.CLIENT)} salvo com sucesso!")

                    update_client_list()
                    

                        
                except Exception as e:
                    st.error(f"Erro ao processar integração com Google: {e}")
    if st.session_state.get(State_Keys_Map.DIAGNOSIS_DOC_URL) and st.session_state.get(State_Keys_Map.DIAGNOSIS_PDF_URL):
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("➡️ Abrir Google Docs", st.session_state.get(State_Keys_Map.DIAGNOSIS_DOC_URL), use_container_width=True)
        with col2:
            st.link_button("⬇️ Baixar PDF", st.session_state.get(State_Keys_Map.DIAGNOSIS_PDF_URL), use_container_width=True)