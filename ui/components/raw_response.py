# ui/components/raw_response.py
"""
Componente de visualização da resposta bruta da IA.

Este módulo contém a função para exibir a resposta textual completa
da IA de forma visualmente atraente, com seções coloridas distintas
para Ishikawa, 5 Porquês, Plano de Ação e Conclusão.
"""
import streamlit as st
import html as html_lib
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Configurações de estilo para cada tipo de seção
SECTION_STYLES = {
    "Diagrama de Ishikawa": {
        "gradient": "linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%)",
        "border_color": "#3B82F6",
        "title_color": "#60A5FA",
        "emoji": "📊"
    },
    "5 Porquês": {
        "gradient": "linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(74, 222, 128, 0.1) 100%)",
        "border_color": "#22C55E",
        "title_color": "#4ADE80",
        "emoji": "🔍"
    },
    "Plano de Ação": {
        "gradient": "linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%)",
        "border_color": "#F59E0B",
        "title_color": "#FBBF24",
        "emoji": "🎯"
    },
    "Conclusão Final": {
        "gradient": "linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(196, 181, 253, 0.1) 100%)",
        "border_color": "#A855F7",
        "title_color": "#C4B5FD",
        "emoji": "🏁"
    }
}

DEFAULT_STYLE = {
    "gradient": "linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(156, 163, 175, 0.1) 100%)",
    "border_color": "#6B7280",
    "title_color": "#9CA3AF",
    "emoji": "📝"
}


def _clean_response(raw_response: str) -> str:
    """
    Limpa a resposta bruta removendo artefatos indesejados.
    
    Remove:
    - Blocos de código vazios (```)
    - Backticks isolados ou triplos em linhas próprias
    - Espaços extras entre seções
    """
    cleaned = raw_response
    
    # Remove blocos de código vazios (``` seguido de ``` com espaços/newlines entre)
    cleaned = re.sub(r'```\s*```', '', cleaned)
    
    # Remove backticks triplos isolados em linhas próprias (com ou sem espaços)
    cleaned = re.sub(r'^\s*```\s*$', '', cleaned, flags=re.MULTILINE)
    
    # Remove backticks simples isolados que sobraram
    cleaned = re.sub(r'^`+\s*$', '', cleaned, flags=re.MULTILINE)
    
    # Remove linhas que são apenas backticks (triplos ou menos)
    cleaned = re.sub(r'\n\s*`{1,3}\s*\n', '\n', cleaned)
    
    # Remove backticks no início ou final do texto
    cleaned = re.sub(r'^`{1,3}\s*', '', cleaned)
    cleaned = re.sub(r'\s*`{1,3}$', '', cleaned)
    
    # Remove múltiplas linhas em branco consecutivas
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()


def display_raw_response(raw_response: str) -> None:
    """
    Exibe a resposta bruta da IA de forma visualmente atraente.
    
    Divide o conteúdo em seções baseadas em padrões **Título** e aplica
    estilos diferentes para cada tipo de seção (Ishikawa, 5 Porquês, etc.).
    
    Args:
        raw_response: Texto bruto da resposta da IA.
    
    Note:
        Se o texto não seguir o padrão esperado, é renderizado como
        markdown simples em um container estilizado.
    """
    if not raw_response or not raw_response.strip():
        st.info("Nenhuma resposta bruta disponível")
        return

    # Limpa artefatos indesejados (backticks vazios, etc.)
    cleaned_response = _clean_response(raw_response)
    
    # Divide a resposta em seções usando padrão **Título**
    sections = re.split(r'\*\*([^*]+)\*\*', cleaned_response)

    if len(sections) > 1:
        _render_structured_response(sections)
    else:
        _render_simple_response(cleaned_response)
    
    logger.debug(f"Resposta bruta renderizada ({len(raw_response)} caracteres)")


def _get_section_style(section_title: str) -> dict:
    """Retorna o estilo apropriado para uma seção baseado no título."""
    for keyword, style in SECTION_STYLES.items():
        if keyword in section_title:
            return style
    return DEFAULT_STYLE


def _render_section_header(section_title: str, style: dict) -> None:
    """Renderiza o cabeçalho de uma seção com estilo apropriado."""
    st.markdown(f"""
    <div style="
        background: {style['gradient']};
        border-left: 4px solid {style['border_color']};
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    ">
    <h3 style="color: {style['title_color']}; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">
        {style['emoji']} {html_lib.escape(section_title)}
    </h3>
    """, unsafe_allow_html=True)


def _render_section_content(content: str) -> None:
    """Renderiza o conteúdo de uma seção com formatação apropriada."""
    lines = content.strip().split('\n')
    for line in lines:
        stripped = line.strip()
        # Ignora linhas vazias ou que contêm apenas backticks
        if not stripped or stripped == '```' or stripped.startswith('```'):
            continue
            
        if stripped.startswith('- '):
            # Item de lista
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                padding: 8px 12px;
                margin: 5px 0;
                border-left: 3px solid rgba(255, 255, 255, 0.3);
                font-size: 0.95em;
            ">
            {html_lib.escape(stripped)}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Parágrafo normal
            st.markdown(f"""
            <p style="
                margin: 8px 0;
                padding: 5px 10px;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 4px;
                font-size: 0.95em;
                line-height: 1.6;
            ">
            {html_lib.escape(stripped)}
            </p>
            """, unsafe_allow_html=True)


def _render_structured_response(sections: list) -> None:
    """Renderiza a resposta dividida em seções estruturadas."""
    i = 1
    while i < len(sections):
        section_title = sections[i].strip()
        section_content = sections[i + 1] if i + 1 < len(sections) else ""

        if section_title and section_content.strip():
            style = _get_section_style(section_title)
            _render_section_header(section_title, style)
            _render_section_content(section_content)
            # Fecha a div da seção
            st.markdown("</div>", unsafe_allow_html=True)

        i += 2


def _render_simple_response(raw_response: str) -> None:
    """Renderiza resposta sem estrutura detectada em container simples."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.9) 100%);
        border: 2px solid rgba(37, 99, 235, 0.5);
        border-radius: 15px;
        padding: 25px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        color: #E2E8F0;
        line-height: 1.7;
    ">
    {raw_response}
    </div>
    """, unsafe_allow_html=True)
