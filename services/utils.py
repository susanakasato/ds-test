from enum import Enum
import streamlit as st

PLANILHA_ID = '1D7TLq7-ThUj5WyUn1Ys3X05jKilDDmYjpLSxngK6ij4'
RANGE_PLANILHA = 'DB Diagnóstico!A:AT'
RANGE_PLANILHA_CLIENTES = 'DB Diagnóstico!A2:A'
RANGE_PLANILHA_WIDTH = 46
PARENT_FOLDER_ID = '12ZTADl3NujM3fNhYTHG3C7cYNPPpFaN8'


def mostrar_imagens_existentes(key_state, nome_secao):
    """Cria um painel expansível mostrando quantas imagens já existem e os seus links."""
    links = st.session_state.get(key_state, "")
    if links:
        lista_links = [l.strip() for l in links.split("\n") if l.strip()]
        qtd = len(lista_links)
        if qtd > 0:
            with st.expander(f"✅ {qtd} imagem(ns) já salva(s) para {nome_secao}", expanded=False):
                st.markdown("Se você fizer upload de novos arquivos, eles serão **adicionados** a esta lista.")
                for i, link in enumerate(lista_links):
                    st.markdown(f"🖼️ [Visualizar Imagem {i+1} no Drive]({link})")

def update_lista_clientes():   
    st.session_state['lista_clientes'] = [] # Inicia vazio
    try:
        with st.spinner("Carregando lista de clientes do banco de dados..."):
            from services.google_api import get_services 
            sheets, _, _ = get_services()
            resultado = sheets.spreadsheets().values().get(
                spreadsheetId=PLANILHA_ID, 
                range=RANGE_PLANILHA_CLIENTES
            ).execute()
            
            linhas = resultado.get('values', [])
            clientes = [linha[0].strip() for linha in linhas if linha and len(linha) > 0 and linha[0].strip()]
            
            # Guarda a lista ordenada e sem repetições na memória
            st.session_state['lista_clientes'] = sorted(list(set(clientes)))
    except Exception as e:
        st.error(f"Erro ao carregar a lista de clientes: {e}")

class Diagnosis_Headers(Enum):
    CLIENT = 'Cliente'

    GTG_IMPLEMENTED = 'GTG implementado'
    CDN = 'Qual CDN Utiliza?'
    USE_IAC = 'Utiliza IaC?'
    USE_TMS = 'Utiliza TMS?'
    TMS_TYPE = 'Qual TMS?'
    USE_GTM_CS = 'Utiliza GTM Client-Side?'
    GTM_CS_IDS = 'IDs GTM Client-Side'
    USE_GTM_SS = 'Utiliza GTM Server-Side?'
    GTM_SS_SERVER = 'Qual servidor o GTM Server-Side está hospedado?'
    AUTH_NEW_DOMAIN_PATH = 'O cliente autorizou a criação de novos caminhos no domínio principal?'
    OBS_GTG = 'GTG - Observações'
    POSSIBLE_GTG = 'À princípio, é possível configurar o GTG?'
    GTG_BLOCKS = 'Possíveis bloqueios para a implementação do GTG'

    GTM_ANALYSIS = 'Análise do json do GTM'
    URLS_FORMS = 'URLS onde apresentam potenciais locais de coleta de dados UPD'

    GA_UPD_CONFIG = 'O GA4 UPD já está configurado na plataforma?'
    GA_HARDCODED = 'O GA4 UPD foi implementado via hardcoded (se for o caso) corretamente?'
    GA_IMG_LINKS = 'GA4 UPD - Links de evidências'
    GA_UPD_POSSIBLE_CONFIG = 'À princípio, é possível configurar o GA UPD?'
    GA_UPD_BLOCKS = 'Possíveis bloqueios para a configuração do GA UPD'

    EC_PLATFORMS = 'Quais plataformas Google o cliente utiliza, que poderiam ter o EC implementado?'
    EC_HARDCODED = 'O EC foi implementado via hardcoded (se for o caso) corretamente?'
    EC_IMG_LINKS = 'EC - Links de evidências'
    EC_POSSIBLE_CONFIG = 'À princípio, é possível configurar o EC?'
    EC_BLOCKS = 'Possíveis bloqueios para a configuração do EC'

    ECL_PLATFORMS = 'Quais plataformas Google o cliente utiliza, que poderiam ter o ECL implementado?'
    ECL_HARDCODED = 'O ECL foi implementado via hardcoded (se for o caso) corretamente?'
    ECL_IMG_LINKS = 'ECL - Links de evidências'
    ECL_POSSIBLE_CONFIG = 'À princípio, é possível configurar o ECl?'
    ECL_BLOCKS = 'Possíveis bloqueios para a configuração do ECL'

    OBS_SIGNALS = 'Envio de sinais - Observações'

    OCI_IMPLEMENTED = 'O OCI já está implementado?'
    OCI_PLATFORM = 'O OCI já está configurado na plataforma?'
    OCI_METHOD = 'Qual o método utilizado para a configuração do OCI?'
    OCI_INFOS = 'Quais dados estão sendo utilizadas e cruzados para o OCI?'
    OCI_IMG_LINKS = 'OCI - Links de evidências'
    OCI_POSSIBLE_CONFIG = 'À princípio, é possível configurar o OCI?'
    OCI_BLOCKS = 'Possíveis bloqueios para a configuração do OCI'
    OBS_OCI = 'OCI - Observações'

    DIAGNOSIS_DOC_ID = 'ID do documento diagnóstico gerado'
    DRIVE_ID = 'ID da pasta do Drive do cliente'
    ROADMAP_DOC_ID = 'ID do documento roadmap gerado'

    GTG_ROADMAP = 'GTG Roadmap'
    UPD_ROADMAP = 'UPD Roadmap'
    OCI_ROADMAP = 'OCI Roadmap'

def getPlatformFromKey(key):
    dict = {
        "gads": "Google Ads",
        "sa": "Search Ads 360",
        "cm": "Campaign Manager 360"
    }
    return dict.get(key, key)

def getKeyFromPlatform(platform):
    dict = {
        "Google Ads": "gads",
        "Search Ads 360": "sa",
        "Campaign Manager 360": "cm"
    }
    return dict.get(platform, platform)

def get_column_index_from_diagnosis_db(diagnosis_headers):
    """Função específica para retornar o índice da coluna dado o nome do header, usando a constante RANGE_PLANILHA."""
    if st.session_state.get('diagnosis_headers') is None:
        from services.google_api import get_services, get_headers_map
        sheets_service, _, _ = get_services()
        st.session_state['diagnosis_headers'] = get_headers_map(sheets_service, PLANILHA_ID, RANGE_PLANILHA)
    return st.session_state['diagnosis_headers'].get(diagnosis_headers.value, -1)

# def get_form_data():
#     # NOVA FUNÇÃO: Decide se faz upload de novas imagens ou se baixa as antigas para o Docx
#     def processar_ou_resgatar_imagens(lista_arquivos_novos, nome_secao, links_existentes):
#         urls_finais = []
#         raw_images_para_docx = []

#         old_links_quantity = len([l.strip() for l in links_existentes.split('\n') if l.strip()]) if links_existentes else 0
        
#         # 1. Se o usuário enviou imagens NOVAS no formulário:
#         if lista_arquivos_novos: 
#             for idx, img_file in enumerate(lista_arquivos_novos):
#                 st.info(f"Salvando imagem {idx+1} de {nome_secao} no Drive...")
#                 img_file.seek(0)
#                 raw_images_para_docx.append(img_file) # Envia para o Docx
                
#                 extensao = img_file.name.split('.')[-1]
#                 nome_arquivo = f"{cliente_nome} - {nome_secao} - {old_links_quantity+idx+1}.{extensao}"
#                 _, link = upload_image_to_drive(drive_service, img_file, nome_arquivo, folder_id=pasta_cliente_id)
#                 urls_finais.append(link)
        
#         # 2. Se NÃO há imagens novas, mas JÁ EXISTEM links antigos salvos no Sheets:
#         if old_links_quantity > 0:
#             links = [l.strip() for l in links_existentes.split('\n') if l.strip()]
#             for idx, link in enumerate(links):
#                 try:
#                     # Extrai o File ID do link do Google Drive (ex: https://drive.google.com/file/d/ID_AQUI/view)
#                     if '/d/' in link:
#                         file_id = link.split('/d/')[1].split('/')[0]
#                         # Faz o download da imagem para a memória e envia para o Docx
#                         img_bytes = download_image_from_drive(drive_service, file_id)
#                         raw_images_para_docx.append(img_bytes)
#                         urls_finais.append(link) # Mantém o link antigo para salvar novamente no Sheets
#                 except Exception as e:
#                     print(f"Erro ao baixar imagem antiga {link}: {e}")
                    
#             # Mantém os links antigos intactos para não apagar do Sheets
#         return '\n'.join(urls_finais), raw_images_para_docx

#     # Executa a inteligência para as 4 sessões de imagens
#     link_ga4, raw_ga4 = processar_ou_resgatar_imagens(st.session_state.get('img_ga4'), "GA4 UPD", st.session_state.get('existing_img_ga4'))
#     link_ec, raw_ec   = processar_ou_resgatar_imagens(st.session_state.get('img_ec'), "EC", st.session_state.get('existing_img_ec'))
#     link_ecl, raw_ecl = processar_ou_resgatar_imagens(st.session_state.get('img_ecl'), "ECL", st.session_state.get('existing_img_ecl'))
#     link_oci, raw_oci = processar_ou_resgatar_imagens(st.session_state.get('img_oci'), "OCI", st.session_state.get('existing_img_oci'))

#     # Salva os resultados no dados_formulario para a criação do Doc e da linha do Sheets
#     dados_formulario['link_img_ga4'] = link_ga4
#     dados_formulario['link_img_ec']  = link_ec
#     dados_formulario['link_img_ecl'] = link_ecl
#     dados_formulario['link_img_oci'] = link_oci
    
#     dados_formulario['raw_img_ga4'] = raw_ga4
#     dados_formulario['raw_img_ec']  = raw_ec
#     dados_formulario['raw_img_ecl'] = raw_ecl
#     dados_formulario['raw_img_oci'] = raw_oci

#     # Função auxiliar para formatar listas (multiselect) como texto separado por vírgula
#     def formatar_lista(item):
#         if isinstance(item, list):
#             return "\n".join(item)
#         return str(item) if item else ""
    
#     # 2. Transforma o dicionário em uma lista (linha) para o Sheets
#     data_line = [None] * RANGE_PLANILHA_WIDTH
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.CLIENT)] = cliente_nome # Preenche o nome do cliente na coluna A (Nome)
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_IMPLEMENTED)] = formatar_lista(dados_formulario.get('gtg_implementado'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.CDN)] = formatar_lista(dados_formulario.get('cdn'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_IAC)] = formatar_lista(dados_formulario.get('iac'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_TMS)] = formatar_lista(dados_formulario.get('usa_tms'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.TMS_TYPE)] = formatar_lista(dados_formulario.get('tms_type'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_GTM_CS)] = formatar_lista(dados_formulario.get('gtm_cs'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_CS_IDS)] = formatar_lista(dados_formulario.get('gtm_cs_ids'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.USE_GTM_SS)] = formatar_lista(dados_formulario.get('gtm_ss'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_SS_SERVER)] = formatar_lista(dados_formulario.get('gtm_ss_server'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.AUTH_NEW_DOMAIN_PATH)] = formatar_lista(dados_formulario.get('novos_caminhos'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.POSSIBLE_GTG)] = formatar_lista(dados_formulario.get('possible_gtg'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTG_BLOCKS)] = formatar_lista(dados_formulario.get('gtg_blocks'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_GTG)] = formatar_lista(dados_formulario.get('obs_gtg'))

#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GTM_ANALYSIS)] = formatar_lista(dados_formulario.get('gtm_analise'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.URLS_FORMS)] = formatar_lista(dados_formulario.get('urls_forms'))

#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_CONFIG)] = formatar_lista(dados_formulario.get('ga_platform'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_HARDCODED)] = formatar_lista(dados_formulario.get('ga_hardcoded'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_ga4'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('ga_upd_possible_config'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.GA_UPD_BLOCKS)] = formatar_lista(dados_formulario.get('ga_upd_blocks'))

#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_PLATFORMS)] = formatar_lista(dados_formulario.get('ec_platforms'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_HARDCODED)] = formatar_lista(dados_formulario.get('ec_hardcoded'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_ec'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('ec_possible_config'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.EC_BLOCKS)] = formatar_lista(dados_formulario.get('ec_blocks'))

#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_PLATFORMS)] = formatar_lista(dados_formulario.get('ecl_platforms'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_HARDCODED)] = formatar_lista(dados_formulario.get('ecl_hardcoded'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_ecl'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('ecl_possible_config'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.ECL_BLOCKS)] = formatar_lista(dados_formulario.get('ecl_blocks'))

#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_SIGNALS)] = formatar_lista(dados_formulario.get('obs_upd'))

#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_IMPLEMENTED)] = formatar_lista(dados_formulario.get('oci_implementado'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_PLATFORM)] = formatar_lista(dados_formulario.get('oci_platform'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_METHOD)] = formatar_lista(dados_formulario.get('oci_metodo'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_INFOS)] = formatar_lista(dados_formulario.get('oci_infos'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_IMG_LINKS)] = formatar_lista(dados_formulario.get('link_img_oci'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_POSSIBLE_CONFIG)] = formatar_lista(dados_formulario.get('oci_possible_config'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OCI_BLOCKS)] = formatar_lista(dados_formulario.get('oci_blocks'))
#     data_line[get_column_index_from_diagnosis_db(Diagnosis_Headers.OBS_OCI)] = formatar_lista(dados_formulario.get('obs_oci'))

#    return data_line
