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
    Exibe a resposta bruta da IA com layout premium unificado.
    """
    if not raw_response or not raw_response.strip():
        st.info("Nenhuma resposta bruta disponível")
        return

    cleaned_response = _clean_response(raw_response)
    
    # Keyword patterns for macro sections
    macro_keywords = ["ishikawa", "porquê", "whys", "plano de ação", "action plan", "conclusão", "conclusion"]
    
    # Split by bold titles OR markdown headers
    # regex matches: **Title** OR # Title OR ## Title OR ### Title
    parts = re.split(r'(?:\*\*|#{1,3}\s+)([^*#\n]+)(?:\*\*|(?=\n|$))', cleaned_response)
    
    # Render intro text if exists
    if parts[0].strip():
        st.markdown(f'<div style="color: #E2E8F0; margin-bottom: 20px; line-height: 1.6;">{parts[0].strip()}</div>', unsafe_allow_html=True)

    i = 1
    while i < len(parts):
        title = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        
        # Check if it's a macro section (Premium Box)
        is_macro = any(kw in title.lower() for kw in macro_keywords)
        
        if is_macro:
            style = _get_section_style(title)
            # Se extraído com sucesso, removemos o JSON do raw_response para não poluir a visualização textual
            # As variáveis json_match, raw_content, ai_results e json_str não estão definidas neste escopo.
            # Este bloco de código parece ser de um contexto diferente onde essas variáveis são acessíveis.
            # Para manter a sintaxe correta e evitar NameError, este bloco é comentado ou removido,
            # pois não pode ser incorporado fielmente sem as definições das variáveis.
            # if json_match:
            #     # Remove o bloco JSON do conteúdo textual
            #     json_raw_block = json_match.group(0)
            #     clean_text = raw_content.replace(json_raw_block, "").strip()
            #     ai_results["raw_response"] = clean_text
            # elif json_str.startswith("{") and "}" in json_str:
            #     # Se for apenas JSON, limpa para não mostrar chaves na bruta
            #     ai_results["raw_response"] = "Consulte o Diagrama de Ishikawa e 5 Porquês para detalhes estruturados."
            # Unify header and content in ONE block to avoid HTML breakage
            section_html = f"""
            <div style="
                background: {style['gradient']};
                border-left: 4px solid {style['border_color']};
                padding: 20px;
                margin: 20px 0;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            ">
            <h3 style="color: {style['title_color']}; margin: 0 0 15px 0; font-size: 1.2em; font-weight: 600;">
                {style['emoji']} {html_lib.escape(title)}
            </h3>
            <div style="color: #F1F5F9; line-height: 1.7;">
            """
            st.markdown(section_html, unsafe_allow_html=True)
            st.markdown(content) # Use native markdown inside for better list/bold support
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            # Subtle rendering for minor sections
            if title and content.strip():
                st.markdown(f"### {title}")
                st.markdown(content)
        
        i += 2

def _get_section_style(section_title: str) -> dict:
    """Retorna o estilo apropriado simplificado para macro seções."""
    title_lower = section_title.lower()
    if "ishikawa" in title_lower:
        return SECTION_STYLES["Diagrama de Ishikawa"]
    if "porquê" in title_lower or "whys" in title_lower:
        return SECTION_STYLES["5 Porquês"]
    if "plano" in title_lower or "action plan" in title_lower:
        return SECTION_STYLES["Plano de Ação"]
    if "conclusão" in title_lower or "conclusion" in title_lower:
        return SECTION_STYLES["Conclusão Final"]
    return DEFAULT_STYLE

# Removendo funções internas agora unificadas
# _render_section_header, _render_section_content, _render_structured_response e _render_simple_response foram absorvidas
