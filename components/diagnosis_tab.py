from components.general_tab import render_general_tab
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
            nome_arquivo = f"{State_Keys_Map.CLIENT.st_state} - {section_name} - {old_links_quantity+idx+1}.{extensao}"
            _, link = upload_image_to_drive(drive_service, img_file, nome_arquivo, folder_id=State_Keys_Map.CLIENT_FOLDER_ID.st_state)
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
    general_tab, gtg_tab, upd_tab, oci_tab = st.tabs(["🧱 Informações Gerais", "🌐 Google Tag Gateway", "📡 Envio de Sinais UPD", "⚙️ OCI Upgrade"])

    with general_tab:
        render_general_tab()
    with gtg_tab:
        render_gtg_tab()
    with upd_tab:
        render_upd_tab()
    with oci_tab:
        render_oci_tab()

    st.divider()
    if st.button("💾 Salvar e Gerar Documento de Diagnóstico", type="primary", use_container_width=True):
        if not State_Keys_Map.CLIENT.st_state:
            st.error("Por favor, preencha o nome do cliente antes de salvar.")
        else:
            with st.spinner("Conectando ao Google Workspace..."):
                try:
                    sheets_service, _, drive_service = get_services()
                    client_row, client_folder_id, diagnosis_doc_id, _, _ = check_client_in_sheets(sheets_service, SHEETS_ID, SHEETS_RANGE, State_Keys_Map.CLIENT.st_state)
                    if client_folder_id is None:
                        client_folder_id = create_drive_folder(drive_service, State_Keys_Map.CLIENT.st_state, PARENT_FOLDER_ID)

                    # Executa a inteligência para as 4 sessões de imagens
                    link_ga4, raw_ga4 = process_or_get_images(State_Keys_Map.GA_IMG_FORM.st_state, "GA4 UPD", State_Keys_Map.GA_IMG_LINKS.st_state)
                    link_ec,  raw_ec  = process_or_get_images(State_Keys_Map.EC_IMG_FORM.st_state, "EC", State_Keys_Map.EC_IMG_LINKS.st_state)
                    link_ecl, raw_ecl = process_or_get_images(State_Keys_Map.ECL_IMG_FORM.st_state, "ECL", State_Keys_Map.ECL_IMG_LINKS.st_state)
                    link_oci, raw_oci = process_or_get_images(State_Keys_Map.OCI_IMG_FORM.st_state, "OCI", State_Keys_Map.OCI_IMG_LINKS.st_state)
                    link_upd, raw_upd = process_or_get_images(State_Keys_Map.UPD_IMG_FORM.st_state, "UPD", State_Keys_Map.UPD_IMG_LINKS.st_state)

                    # Salva os resultados no dados_formulario para a criação do Doc e da linha do Sheets
                    st.session_state[State_Keys_Map.GA_IMG_LINKS.value] = link_ga4
                    st.session_state[State_Keys_Map.EC_IMG_LINKS.value] = link_ec
                    st.session_state[State_Keys_Map.ECL_IMG_LINKS.value] = link_ecl
                    st.session_state[State_Keys_Map.OCI_IMG_LINKS.value] = link_oci
                    st.session_state[State_Keys_Map.UPD_IMG_LINKS.value] = link_upd
                    
                    st.session_state[State_Keys_Map.GA_IMG_RAW.value] = raw_ga4
                    st.session_state[State_Keys_Map.EC_IMG_RAW.value] = raw_ec
                    st.session_state[State_Keys_Map.ECL_IMG_RAW.value] = raw_ecl
                    st.session_state[State_Keys_Map.OCI_IMG_RAW.value] = raw_oci
                    st.session_state[State_Keys_Map.UPD_IMG_RAW.value] = raw_upd


                    data_for_docx = {}
                    for key in State_Keys_Map:
                        data_for_docx[key] = key.st_state

                    # 3. Cria o documento já jogando para dentro da pasta certa
                    st.info("Gerando o documento de diagnóstico...")
                    diagnosis_doc_id, doc_url, pdf_url = create_update_diagnostic_doc(
                        drive_service, State_Keys_Map.CLIENT.st_state, data_for_docx, client_folder_id, diagnosis_doc_id
                    )
                    st.session_state[State_Keys_Map.DIAGNOSIS_DOC_URL.value] = doc_url
                    st.session_state[State_Keys_Map.DIAGNOSIS_PDF_URL.value] = pdf_url

                    sheets_data = [None] * SHEETS_RANGE_WIDTH
                    for key in Headers_Map:
                        sheets_data[get_sheet_column_index(key)] = format_list(key.state_key.st_state)
                    sheets_data[Headers_Map.DIAGNOSIS_DOC_ID.column_index] = diagnosis_doc_id
                    sheets_data[Headers_Map.DRIVE_ID.column_index] = client_folder_id

                    # 3. Salva no Sheets e verifica se tinha doc antigo
                    st.info("Atualizando Banco de Dados (Sheets)...")
                    save_to_sheets(sheets_service, SHEETS_ID, SHEETS_RANGE, client_row, sheets_data)

                    st.success(f"Diagnóstico para {State_Keys_Map.CLIENT.st_state} salvo com sucesso!")

                    update_client_list()
                    

                        
                except Exception as e:
                    st.error(f"Erro ao processar integração com Google: {e}")
    if State_Keys_Map.DIAGNOSIS_DOC_URL.st_state and State_Keys_Map.DIAGNOSIS_PDF_URL.st_state:
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("➡️ Abrir Google Docs", State_Keys_Map.DIAGNOSIS_DOC_URL.st_state, use_container_width=True)
        with col2:
            st.link_button("⬇️ Baixar PDF", State_Keys_Map.DIAGNOSIS_PDF_URL.st_state, use_container_width=True)