import json
import streamlit as st
from google import genai
from google.genai import types

def gerar_roadmap_ia(diagnosis_data):
    # 1. Recupera a chave do arquivo .streamlit/secrets.toml
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("🔑 Chave da API do Gemini não encontrada. Verifique o arquivo secrets.toml.")
        return None

    # Inicializa o novo client
    client = genai.Client(api_key=api_key)
    
    # 2. Catálogo de Atividades Pré-Mapeadas
    atividades_catalogo = {
        "GTG": [
            {"id": "GTG01", "atividade": "Montar arquitetura GTG (4h)", "desc": "Desenho da solução técnica."},
            {"id": "GTG02", "atividade": "Criação do doc. guia de impl. (5h)", "desc": "Criação de documento contendo instruções de configuração prática do GTG, de acordo com a tecnologia utilizada pelo cliente."},
            {"id": "GTG03", "atividade": "Implementar GTG (16h)", "desc": "Responsável realiza a implementação do GTG de acordo com as recomendações feitas a partir do diagnóstico montado."},
            {"id": "GTG04", "atividade": "Validação do GTG implementado (6h)", "desc": "Verificação da coleta de dados Google para o destino correto, assim como o redirecionamento desta coleta para as ferramentas finais (GA, GAds, CM360, SA360)."}
        ],
        "UPD": [
            {"id": "UPD01", "atividade": "Montar arquitetura Envio de Sinais UPD (5h)", "desc": "Através da identificação dos campos de dados UPD, verificar presença destas informações na camada de dados."},
            {"id": "UPD02", "atividade": "Mapear camada de dados (3h)", "desc": "Verificar presença de informações na data layer."},
            {"id": "UPD03", "atividade": "Criar doc. de impl. da camada de dados (3h)", "desc": "Criar documento contendo instruções de configuração prática da camada de dados, de acordo com a tecnologia utilizada pelo cliente, especificando as informações e os momentos que as informações devem ser disponibilizadas."},
            {"id": "UPD04", "atividade": "Implementar camada de dados (12h)", "desc": "Cliente irá implementar camada de dados de acordo com o documento disponibilizado."},
            {"id": "UPD05", "atividade": "Validar camada de dados (3h)", "desc": "Verificar presença de informações mapeadas na camada de dados."},
            {"id": "UPD06", "atividade": "Configurar envio UPD (4h)", "desc": "Configurar GTM, GA, GAds, CM, SA."},
            {"id": "UPD07", "atividade": "Validar envio de sinais (6h)", "desc": "Validações finais nas ferramentas GTM, GA, GAds, CM, SA e log de requisições."}
        ],
        "OCI": [
            {"id": "OCI01", "atividade": "Montar arquitetura GTG (4h)", "desc": "Desenho da solução técnica."},
            {"id": "OCI02", "atividade": "Criar doc. de envio de sinais p/ backend (4h)", "desc": "Montar documentação com instruções técnicas para configuração de envio de sinais para o backend, de acordo com os sinais faltantes identificados no processo de diagnóstico."},
            {"id": "OCI03", "atividade": "Configurar envio p/ backend (16h)", "desc": "O time de desenvolvimento terá como responsabilidade implementar o envio de informações adicionais para ferramentas de CRM, através de campos escondidos (hidden inputs), modificando tanto a estrutura de formulários presentes no site e a lógica de cadastramento, como também a estrutura da tabela do CRM."},
            {"id": "OCI04", "atividade": "Mapear ferramenta para integração offline (1h)", "desc": "Listar ferramentas para integrações offline, com a relação de possíveis métodos de integração."},
            {"id": "OCI05", "atividade": "Configurar a integração de dados offline (4h)", "desc": "A DP6 irá configurar a integração de dados pelo Data Manager UI."},
            {"id": "OCI06", "atividade": "criar doc. para integração de dados offline (4h)", "desc": "A DP6 irá criar documentação técnica para integração de dados offline para o cliente implementar."},
            {"id": "OCI07", "atividade": "Configurar a integração de dados offline (12h)", "desc": "O cliente irá implementar a integração de dados offline de acordo com o documento disponibilizado."},
            {"id": "OCI08", "atividade": "Validar conversões offline (6h)", "desc": "Validação no GAds, CM e SA e criação de documento."}
        ]
    }

    # 3. Construção do Prompt
    prompt = f"""
    Você é um Arquiteto de Dados e Consultor Sênior de Marketing Analytics e está participando de um projeto Data Stength, onde o intuito é implementar e validar alguns
    recursos de coleta de dados e ativação dos mesmos, como otimização de mídia, para o cliente. Com base no diagnóstico do cliente (que é real e foi coletado via formulário), 
    sua tarefa é criar um Roadmap de Implementação detalhado, que será entregue ao cliente em formato de documento.
    Crie um Roadmap de Implementação para o cliente baseado no diagnóstico abaixo.
    
    DIAGNÓSTICO DO CLIENTE:
    {diagnosis_data}
    
    ATIVIDADES PRÉ-MAPEADAS (Nosso catálogo padrão):
    {json.dumps(atividades_catalogo, indent=2, ensure_ascii=False)}
    
    INSTRUÇÕES:
    1. Analise o diagnóstico. Se o cliente já tem algo implementado (ex: GTG="Sim"), o roadmap daquela área deve dizer apenas "Não há necessidade de roadmap. Cliente já atende os requisitos.".
    2. Para as áreas que precisam de implementação, crie um plano de ação passo a passo listado numericamente.
    3. Use as 'Atividades Pré-Mapeadas' que fizerem sentido.
    4. CRIE NOVAS ATIVIDADES sugeridas por você (IA) que complementem o plano de forma inteligente (adicione a tag ✨[Sugestão IA] antes do nome da atividade).
    5. Retorne ESTRITAMENTE um objeto JSON com as chaves: "roadmap_gtg", "roadmap_upd" e "roadmap_oci". O valor de cada chave, que corresponde à uma seção, deve conter um array, contendo as atividades listadas, e cada atividade deve ser um json com os campos "activity" e "description".
    6. Avalie a necessidade das atividades pré-mapeadas, pois há cenários em que nem todas as atividades serão necessárias. Assim como, há cenários em que você pode sugerir novas atividades, que possam encaixar perfeitamente.
    7. Para o caso de envio de sinais, considere a análise do gtm se estiver disponível, onde também é possível identificar se o cliente já possui os recursos configurados e se está configurado corretamente. Caso já esteja configurado, o ideal seria adicionar atividades de validação de hash e de configuração.
    8. Analise a informação sobre a possibilidade de implementação/configuração e os possíveis bloqueios para implementação de todas as vertentes. Se houver bloqueios, considere atividades de validação de hipóteses, como por exemplo: "Validar hipótese de bloqueio X com o time de desenvolvimento do cliente (2h)".
    9. Caso a configuração/implementação esteja sinalizada como feita, inserir atividade de validação do que já está implementado/configurado, para garantir que o que foi implementado está funcionando corretamente e coletando os dados necessários.
    10. Caso a configuração/implementação esteja sinalizada como não feita, inserir atividade de configuração/implementação, mesmo que não esteja pré-mapeada, para garantir que o roadmap entregue ao cliente seja completo e com um passo a passo claro do que deve ser feito.
    11. No roadmap final, não há a necessidade de inserir o id da atividade.
    """

    try:
        # Faz a chamada para a IA usando o modelo mais recente e forçando a saída em JSON
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        # Como forçamos o mimetype, o response.text já é um JSON limpo e válido
        resultado_json = json.loads(response.text)
        return resultado_json
        
    except Exception as e:
        st.error(f"Erro na comunicação com a IA: {e}")
        return None