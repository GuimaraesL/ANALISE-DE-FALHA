# app.py
"""
Ponto de entrada principal da aplicação de Análise de Falhas.

Este módulo é o entry point do Streamlit e deve ser mantido limpo,
delegando a lógica de UI para os módulos especializados em ui/.

Fluxo de Execução:
    1. Carrega estilos CSS
    2. Renderiza sidebar e obtém configurações
    3. Valida configurações (Fail Fast)
    4. Executa análise se botão foi pressionado
    5. Renderiza resultados se existirem

Usage:
    streamlit run app.py
"""
import streamlit as st
from pathlib import Path
import os
import sys
import logging

# Configurar logging antes de qualquer outro import
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ajustar PYTHONPATH para garantir imports do projeto
sys.path.insert(0, str(Path(__file__).parent))

# Imports do projeto
try:
    from ui.styles import load_css
    from ui.pages.sidebar import render_sidebar, validate_config
    from ui.pages.results import render_results
    from ui.texts import TEXTS
    from core.failure_analysis_app import FailureAnalysisApp
    from core.config_loader import load_config
except ModuleNotFoundError as e:
    st.error(f"❌ Erro ao importar módulos: {e}. Verifique se os diretórios 'core' e 'ui' existem.")
    logger.error(f"Erro ao importar módulos: {e}")
    st.stop()


def setup_google_credentials() -> None:
    """
    Configura as credenciais do Google Cloud para análise de vídeo.
    
    Carrega o caminho do arquivo de credenciais do config.json e
    define a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS.
    """
    config = load_config()
    credentials_path = config.get("google_credentials_path")
    
    if credentials_path and Path(credentials_path).exists():
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        logger.info(f"Credenciais do Google Cloud carregadas: {credentials_path}")
    else:
        st.warning(
            f"⚠️ Arquivo de credenciais '{credentials_path}' não encontrado. "
            "A análise de vídeo pode falhar."
        )
        logger.warning(f"Credenciais não encontradas: {credentials_path}")


def run_analysis(config: dict) -> None:
    """
    Executa o pipeline de análise de falhas.
    
    Args:
        config: Dicionário de configurações da sidebar contendo:
            - api_key: Chave da API Gemini
            - root_folder: Pasta raiz para análise
            - enable_videos: Flag de análise de vídeo
            - enable_images: Flag de análise de imagem
            - lang_code: Código do idioma
    """
    texts = config["texts"]
    
    # Indicador de processamento
    processing_msg = st.empty()
    processing_msg.write(texts["processing"])
    logger.info(f"Iniciando análise na pasta: {config['root_folder']}")
    
    # Instanciar e executar o app de análise
    app = FailureAnalysisApp(
        root_folder=config["root_folder"],
        gemini_api_key=config["api_key"],
        enable_images=config["enable_images"],
        enable_videos=config["enable_videos"],
        language=config["lang_code"]
    )
    
    app.run()
    
    # Limpar mensagem de processamento
    processing_msg.empty()
    
    # Armazenar resultados e configurações no session_state
    st.session_state["results"] = app.results if app.results else []
    st.session_state["enable_videos"] = config["enable_videos"]
    st.session_state["enable_images"] = config["enable_images"]
    st.session_state["lang_code"] = config["lang_code"]
    
    logger.info(f"Análise concluída. {len(app.results)} resultados processados.")


def main() -> None:
    """
    Função principal que orquestra a aplicação Streamlit.
    
    Segue o padrão de Clean Architecture, delegando para
    módulos especializados:
    - ui/styles.py: Carregamento de CSS
    - ui/pages/sidebar.py: Configurações do usuário
    - ui/pages/results.py: Renderização de resultados
    """
    # 1. Setup inicial
    load_css()
    setup_google_credentials()
    
    # 2. Renderiza sidebar e obtém configurações
    config = render_sidebar()
    
    # 3. Processa execução se botão foi pressionado
    if config["execute"]:
        # Valida configurações (Fail Fast)
        error_message = validate_config(config)
        if error_message:
            st.error(error_message)
            return
        
        # Executa análise
        run_analysis(config)
    
    # 4. Renderiza resultados se existirem
    if "results" in st.session_state and st.session_state["results"]:
        lang_code = st.session_state.get("lang_code", config["lang_code"])
        render_results(lang_code)


if __name__ == "__main__":
    main()
