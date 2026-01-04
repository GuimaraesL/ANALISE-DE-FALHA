# ui/pages/sidebar.py
"""
Módulo responsável pela renderização e lógica da sidebar.

Este módulo encapsula toda a configuração da sidebar do Streamlit,
incluindo seleção de idioma, inputs de configuração e botão de execução.
"""
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from ui.texts import TEXTS
from core.config_loader import load_config

logger = logging.getLogger(__name__)


def render_sidebar() -> Dict[str, Any]:
    """
    Renderiza a sidebar e retorna as configurações selecionadas.
    
    Exibe os controles de configuração na sidebar do Streamlit:
    - Seletor de idioma
    - Campo de API key (se não configurada)
    - Campo de caminho da pasta raiz
    - Toggles para análise de vídeo/imagem
    - Botão de execução
    
    Returns:
        Dicionário com as configurações:
        - lang_code: "pt" ou "en"
        - texts: Dicionário de textos traduzidos
        - api_key: Chave da API do Gemini
        - root_folder: Caminho da pasta raiz
        - enable_videos: Se análise de vídeo está habilitada
        - enable_images: Se análise de imagem está habilitada
        - execute: Se o botão de execução foi pressionado
    
    Example:
        >>> config = render_sidebar()
        >>> if config["execute"]:
        ...     run_analysis(config)
    """
    config = load_config()
    api_key = config.get("gemini_api_key", "")
    
    with st.sidebar:
        # Seletor de idioma
        language = st.selectbox(
            "🌐 Selecione a linguagem / Select language:",
            ["Português", "English"]
        )
        lang_code = "pt" if language == "Português" else "en"
        texts = TEXTS[lang_code]
        
        # Título e instruções
        st.title(texts["title"])
        st.write(texts["folder_instruction"])
        
        # Input da pasta raiz
        default_folder = r"G:\Meu Drive\01_PYTHON\02_ARQUIVOS PARA TESTES\AF\TESTES"
        root_folder = st.text_input(texts["root_path_input"], value=default_folder)
        
        # Toggles de análise
        enable_videos = st.checkbox(texts["video_disabled_ui"], value=False)
        enable_images = st.checkbox(texts["image_disabled_ui"], value=False)
        
        # Botão de execução
        execute = st.button(texts["run_button"])
    
    logger.debug(f"Sidebar renderizada - Idioma: {lang_code}, Pasta: {root_folder}")
    
    return {
        "lang_code": lang_code,
        "texts": texts,
        "api_key": api_key,
        "root_folder": root_folder,
        "enable_videos": enable_videos,
        "enable_images": enable_images,
        "execute": execute,
    }


def validate_config(config: Dict[str, Any]) -> Optional[str]:
    """
    Valida as configurações da sidebar.
    
    Args:
        config: Dicionário de configurações retornado por render_sidebar().
    
    Returns:
        Mensagem de erro se houver problema, None se tudo estiver válido.
    """
    texts = config["texts"]
    
    if not config["api_key"]:
        return texts["no_api_key"]
    
    if not config["root_folder"]:
        return texts["no_folder"]
    
    if not Path(config["root_folder"]).exists():
        return texts["folder_not_found"].format(config["root_folder"])
    
    return None
