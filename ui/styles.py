# ui/styles.py
"""
Módulo responsável pelo carregamento e gerenciamento de estilos CSS.

Este módulo contém funções para carregar arquivos CSS externos e aplicá-los
à interface Streamlit, garantindo consistência visual em toda a aplicação.
"""
import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_css(css_filename: str = "styles.css") -> None:
    """
    Carrega e aplica um arquivo CSS externo à aplicação Streamlit.
    
    Args:
        css_filename: Nome do arquivo CSS a ser carregado.
            Por padrão, busca 'styles.css' na raiz do projeto.
    
    Note:
        Se o arquivo não for encontrado, exibe um aviso e continua
        com os estilos padrão do Streamlit.
    """
    css_path = Path(css_filename)
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            logger.info(f"CSS carregado: {css_path}")
    else:
        st.warning(f"⚠️ Arquivo {css_filename} não encontrado. Usando estilo padrão.")
        logger.warning(f"Arquivo CSS não encontrado: {css_path}")
