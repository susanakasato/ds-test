import streamlit as st
import ast
import json

from services.utils import mostrar_imagens_existentes

def analisar_json_gtm(gtm_data):
    container = gtm_data.get('containerVersion', {})
    tags = container.get('tag', [])
    variables = container.get('variable', [])
    
    # Usaremos um dicionário para guardar o mapeamento relacional
    # Estrutura: { 'Nome da Var': {'metodo': '...', 'campos': [...], 'tags_que_usam': []} }
    upd_variables_dict = {}
    
    # --- 1. IDENTIFICAR VARIÁVEIS UPD ---
    for var in variables:
        if var.get('type') == 'awec':
            var_name = var.get('name')
            params = var.get('parameter', [])
            metodo = "Desconhecido"
            
            # Analisar os parâmetros para descobrir o método e os campos (email, telefone)
            for p in params:
                key = p.get('key')
                val = p.get('value')
                type = p.get('type')

                if type == "TEMPLATE" and key == "mode":
                    metodo = val

                
            upd_variables_dict[var_name] = {
                'var_name': var_name,
                'method': metodo
            }

    # --- 2. ANALISAR TAGS E CRIAR RELACIONAMENTO ---
    # Adicionadas as tags solicitadas: awupd (Ads UPD Event) e gcl_setup (Conversion Linker)
    tipos_alvo = {
        'awct': 'Google Ads Conversion',
        'flc': 'Floodlight Counter',
        'fls': 'Floodlight Sales',
        'gaawc': 'GA4 Config',
        'gaawe': 'GA4 Event',
        'awud': 'Google Ads User Provided Data Event',
        'gclidw': 'Conversion Linker'
    }
    
    target_tags_dict = {}
    
    for tag in tags:
        tag_name = tag.get('name')
        t_type = tag.get('type')
        paused = tag.get('paused', False)
        
        if t_type in tipos_alvo:
            upd_var_name = '-'
            setting_status = ''
            params = tag.get('parameter', [])
            eventSettings = next((p for p in params if p.get("key") == "eventSettingsTable"), None)
            if eventSettings is not None:
                eventSettings = eventSettings.get("list", [])
                for eventSetting in eventSettings:
                    parameter_name_status = False
                    parameter_value_type_status = False

                    for item in eventSetting.get("map", []):
                        if item.get("key") == "parameter" and item.get("value") == "user_data":
                            parameter_name_status = True
                        elif item.get("key") == "parameterValue":
                            upd_var_name = item.get("value").replace("{{", "").replace("}}", "")
                            if upd_var_name in upd_variables_dict.keys():
                                parameter_value_type_status = True

                    if parameter_name_status and parameter_value_type_status:
                        setting_status = "✅ Correto"
                    elif parameter_name_status and not parameter_value_type_status:
                        setting_status = "❌ Incorreto - Variável usada não é do tipo User-Provided Data"
                    elif not parameter_name_status and parameter_value_type_status:
                        setting_status = "❌ Incorreto - Parâmetro usado não é 'user_data'"
                    elif not parameter_name_status and not parameter_value_type_status:
                        setting_status = "⚠️ Não configurado"
                    if parameter_name_status or parameter_value_type_status:
                        break
            else:
                setting_status = "⚠️ Não configurado"
            target_tags_dict[tag_name] = {
                'tag_name': tag_name,
                'type': tipos_alvo[t_type],
                'setting_status': setting_status,
                'var_name': upd_var_name,
                'paused': paused
            }

    result = {
        'upd_variables': upd_variables_dict,
        'target_tags': target_tags_dict
    }

    return result

def render_gtm_analysis_table(gtm_analise_result):
    st.info("🔍 Resultado da Análise Automática:")
    upd_var = gtm_analise_result.get('upd_variables', {})
    upd_var_keys = upd_var.keys()
    upd_var_table = {
        "Nome": [],
        "Método": []
    }
    for var_name in upd_var_keys:
        upd_var_table["Nome"].append(upd_var[var_name]['var_name'])
        upd_var_table["Método"].append(upd_var[var_name]['method'])
    target_tags = gtm_analise_result.get('target_tags', {})
    tags_keys = target_tags.keys()
    tags_table = {
        "Nome": [],
        "Tipo": [],
        "Pausada": [],
        "Status Configuração UPD": [],
        "Variável UPD Usada": []
    }
    for tag_name in tags_keys:
        tag_info = target_tags[tag_name]
        tags_table["Nome"].append(tag_name)
        tags_table["Tipo"].append(tag_info['type'])
        tags_table["Pausada"].append("⏸️ Sim" if tag_info['paused'] else "▶️ Não")
        tags_table["Status Configuração UPD"].append(tag_info['setting_status'])
        tags_table["Variável UPD Usada"].append(tag_info['var_name'])
    st.text("📌 Variáveis UPD Encontradas:")
    st.table(upd_var_table)
    st.text("📌 Tags Relevantes para UPD Encontradas:")
    st.table(tags_table)

def render_upd_tab(dados_formulario):
    st.header("Envio de Sinais UPD")

    tms_atual = st.session_state.get('tms_type')

    if tms_atual == "Google Tag Manager":
        st.subheader("Análise do Container GTM")
        uploaded_file = st.file_uploader("Upload do GTM Container Export (JSON)", type="json")
        
        if uploaded_file is not None or st.session_state.get('k_gtm_analise'):
            try:
                if uploaded_file is not None:
                    gtm_data = json.load(uploaded_file)
                    st.success("Arquivo carregado com sucesso!")
                    gtm_analise_result = analisar_json_gtm(gtm_data)
                    st.session_state["k_gtm_analise"] = gtm_analise_result

                elif st.session_state.get('k_gtm_analise'):
                    gtm_analise_result = ast.literal_eval(st.session_state.get('k_gtm_analise'))
                
                render_gtm_analysis_table(gtm_analise_result)
                dados_formulario['gtm_analise'] = gtm_analise_result
                
            except Exception as e:
                st.error(f"Erro ao ler ou analisar o arquivo JSON: {e}")

    dados_formulario['urls_forms'] = st.text_area("Liste as URLs onde há a presença de formulários possíveis de coleta de dados UPD:", key='k_urls_forms')

    st.divider()

    # --- Subseção: Google Analytics ---
    st.subheader("📈 Google Analytics")
    dados_formulario['ga_platform'] = st.radio("A coleta de dados fornecidos pelo usuário foi ativada na interface do GA4?", ("Sim", "Não"), index=None, key='k_ga_config')
    
    if dados_formulario['ga_platform'] == "Não" or tms_atual != "Google Tag Manager":
        dados_formulario['ga_hardcoded'] = st.radio("A implementação foi feita corretamente via hard coded? (GA)", ("Sim", "Não"), index=None, key='k_ga_hard')
    st.file_uploader("Upload de imagens de validação (GA)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_ga4")
    mostrar_imagens_existentes('existing_img_ga4', "GA4 UPD") # Painel para mostrar imagens já existentes no Sheets para GA4 UPD
    if dados_formulario['ga_platform'] == "Não" and dados_formulario['ga_hardcoded'] == "Não":
        dados_formulario['ga_upd_possible_config'] = st.radio("À princípio, é possível configurar o GA UPD?", ("Sim", "Não", "Talvez"), index=None, key='k_ga_upd_possible_config')
        dados_formulario['ga_upd_blocks'] = st.text_area("Quais seriam os possíveis bloqueios para a configuração do GA UPD?", key='k_ga_upd_blocks')

    st.divider()

    # --- Subseção: Enhanced Conversions ---
    st.subheader("🎯 Enhanced Conversions")

    ec_platforms = st.multiselect(
        "Quais plataformas o cliente utiliza que poderiam configurar o EC?",
        ["Google Ads", "Search Ads 360", "Campaign Manager 360"],
        key='k_ec_platforms'
    )
    formatted_ec_platforms = []
    status_need_ec_config = False
    if ec_platforms:
        st.markdown("**Validação de Configuração (EC):**")
        for plat in ec_platforms:
            status_ec = st.radio(f"A configuração EC foi feita corretamente na plataforma {plat}?", ("Sim", "Não"), key=f"k_ec_platform_{plat}", index=None)
            status_texto = f"Configurado corretamente: {status_ec}" if status_ec else "Status não informado"
            if status_ec == "Não":
                status_need_ec_config = True
            formatted_ec_platforms.append(f"{plat} ({status_texto})")
    dados_formulario['ec_platforms'] = formatted_ec_platforms
    
    # Condição: Se EC não ativada (nenhuma selecionada) ou não usa GTM
    if tms_atual != "Google Tag Manager":
        dados_formulario['ec_hardcoded'] = st.radio("A implementação foi feita corretamente via hard coded? (EC)", ("Sim", "Não"), index=None, key='k_ec_hard')
    st.file_uploader("Upload de imagens de validação (EC)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_ec")
    mostrar_imagens_existentes('existing_img_ec', "EC") 
    if status_need_ec_config:
        dados_formulario['ec_possible_config'] = st.radio("À princípio, é possível configurar o EC?", ("Sim", "Não", "Talvez"), index=None, key='k_ec_possible_config')
        dados_formulario['ec_blocks'] = st.text_area("Quais seriam os possíveis bloqueios para a configuração do EC?", key='k_ec_blocks')

    st.divider()

    # --- Subseção: Enhanced Conversions for Leads ---
    st.subheader("🧲 Enhanced Conversions for Leads")
    ecl_platforms = st.multiselect(
        "Quais plataformas o cliente utiliza que poderiam configurar o ECL?",
        ["Google Ads", "Search Ads 360", "Campaign Manager 360"],
        key='k_ecl_platforms'
    )
    formatted_ecl_platforms = []
    status_need_ecl_config = False
    if ecl_platforms:
        st.markdown("**Validação de Configuração (ECL):**")
        for plat in ecl_platforms:
            status_ecl = st.radio(f"A configuração ECL foi feita corretamente na plataforma {plat}?", ("Sim", "Não"), key=f"k_ecl_platform_{plat}", index=None)
            status_texto = f"Configurado corretamente: {status_ecl}" if status_ecl else "Status não informado"
            if status_ecl == "Não":
                status_need_ecl_config = True
            formatted_ecl_platforms.append(f"{plat} ({status_texto})")
    dados_formulario['ecl_platforms'] = formatted_ecl_platforms
    if tms_atual != "Google Tag Manager":
        dados_formulario['ecl_hardcoded'] = st.radio("A implementação foi feita corretamente via hard coded? (ECL)", ("Sim", "Não"), index=None, key='k_ecl_hard')
    st.file_uploader("Upload de imagens de validação (ECL)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_ecl")
    mostrar_imagens_existentes('existing_img_ecl', "ECL") # Painel para mostrar imagens já existentes no Sheets para ECL
    if status_need_ecl_config:
        dados_formulario['ecl_possible_config'] = st.radio("À princípio, é possível configurar o ECL?", ("Sim", "Não", "Talvez"), index=None, key='k_ecl_possible_config')
        dados_formulario['ecl_blocks'] = st.text_area("Quais seriam os possíveis bloqueios para a configuração do ECL?", key='k_ecl_blocks')

    st.subheader("🟦 Geral")
    dados_formulario['obs_upd'] = st.text_area("Observações (Envio de Sinais UPD)", key='k_obs_upd')