# ui/pages/results.py
"""
Módulo responsável pela renderização dos resultados da análise.

Este módulo encapsula toda a lógica de exibição dos resultados na
interface principal, incluindo expanders para cada seção e o botão
de download do relatório em Markdown.
"""
import streamlit as st
import html as html_lib
from datetime import datetime
from typing import Dict, Any, List
import logging
import re

from ui.texts import TEXTS
from ui.components import plot_ishikawa, display_five_whys, display_raw_response
from ui.utils import generate_markdown_result, clean_empty_values

logger = logging.getLogger(__name__)


# ============================================================================
# ESTILOS PREMIUM REUTILIZÁVEIS
# ============================================================================
# Estilos em linha única para evitar problemas de interpolação HTML
STYLE_CARD = "background: linear-gradient(135deg, rgba(30, 58, 138, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%); border: 1px solid rgba(37, 99, 235, 0.3); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;"

STYLE_LABEL = "color: #60A5FA; font-weight: 600; margin-right: 8px;"

STYLE_VALUE = "color: #E2E8F0;"

STYLE_HISTORY_CARD = "background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(196, 181, 253, 0.1) 100%); border: 1px solid rgba(168, 85, 247, 0.3); border-left: 4px solid #A855F7; border-radius: 10px; padding: 15px 20px; margin-bottom: 15px;"

STYLE_REFINED_HISTORY = "background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(74, 222, 128, 0.1) 100%); border: 1px solid rgba(34, 197, 94, 0.3); border-left: 4px solid #22C55E; border-radius: 10px; padding: 15px 20px;"


# ============================================================================
# FUNÇÕES DE RENDERIZAÇÃO
# ============================================================================

def render_results(lang_code: str = "pt") -> None:
    """
    Renderiza os resultados armazenados em session_state.
    
    Exibe cada resultado da análise em um layout estruturado com
    expanders para dados do Excel, mídias, resposta da IA, Ishikawa,
    5 Porquês, histórico e métricas de tokens.
    
    Args:
        lang_code: Código do idioma ('pt' ou 'en').
    
    Note:
        Espera que st.session_state["results"] contenha uma lista
        de dicionários de resultados do FailureAnalysisApp.
    """
    if "results" not in st.session_state:
        return
    
    texts = TEXTS[lang_code]
    results = st.session_state["results"]
    
    for result in results:
        _render_single_result(result, texts, lang_code)
    
    st.success(texts["success"])
    logger.info(f"Renderizados {len(results)} resultados")


def _render_single_result(result: Dict[str, Any], texts: Dict[str, str], lang_code: str) -> None:
    """Renderiza um único resultado de análise."""
    st.subheader(f"📁 {texts['folder']}: {result['folder']}")
    
    if result["status"] == "error":
        st.error(f"❌ Erro / Error: {result['details']}")
        return
    
    details = result["details"]
    
    # Expanders principais
    _render_excel_data(details, texts)
    _render_video_analysis(details, texts)
    _render_image_analysis(details, texts)
    _render_raw_response(details, texts)
    _render_ishikawa(details, texts, lang_code)
    _render_five_whys(details, texts, lang_code)
    _render_history(details, texts, lang_code)
    _render_conclusion(details, texts)
    _render_tokens(result, texts)
    _render_download_button(result, texts, lang_code)


def _render_excel_data(details: Dict, texts: Dict) -> None:
    """Renderiza os dados extraídos do Excel com visual premium."""
    with st.expander(texts["excel_data"]):
        excel_data = details.get("excel_data", {})
        
        fields = [
            (texts['area'], excel_data.get('area', 'N/A'), "🏭"),
            (texts['equipment'], excel_data.get('equipment', 'N/A'), "⚙️"),
            (texts['subgroup'], excel_data.get('subgroup', 'N/A'), "📦"),
            (texts['description'], excel_data.get('description', 'N/A'), "📝"),
        ]
        
        for label, value, emoji in fields:
            st.markdown(f"""
            <div style="{STYLE_CARD}">
                <span style="{STYLE_LABEL}">{emoji} {html_lib.escape(label)}:</span>
                <span style="{STYLE_VALUE}">{html_lib.escape(str(value))}</span>
            </div>
            """, unsafe_allow_html=True)


def _render_video_analysis(details: Dict, texts: Dict) -> None:
    """Renderiza a análise de vídeo."""
    with st.expander(texts["video_analysis_title"]):
        video_result = details.get("video_results", "")
        if video_result and video_result.strip():
            st.markdown(f"""
            <div style="{STYLE_CARD}">
                {video_result}
            </div>
            """, unsafe_allow_html=True)
        else:
            if not st.session_state.get("enable_videos", False):
                st.info(texts["video_disabled"])
            else:
                st.info(texts["no_video_found"])


def _render_image_analysis(details: Dict, texts: Dict) -> None:
    """Renderiza a análise de imagem."""
    with st.expander(texts["image_analysis"]):
        image_result = details.get("image_results", "")
        if image_result and str(image_result).strip():
            st.markdown(f"""
            <div style="{STYLE_CARD}">
                {html_lib.escape(str(image_result))}
            </div>
            """, unsafe_allow_html=True)
        else:
            if not st.session_state.get("enable_images", False):
                st.info(texts["image_disabled"])
            else:
                st.info("Nenhuma análise de imagem encontrada.")


def _render_raw_response(details: Dict, texts: Dict) -> None:
    """Renderiza a resposta bruta da IA."""
    with st.expander(texts["raw_response"]):
        raw_response = details.get("ai_results", {}).get("raw_response", "")
        if raw_response and raw_response.strip():
            display_raw_response(raw_response)
        else:
            st.info(texts["no_raw_response"])


def _render_ishikawa(details: Dict, texts: Dict, lang_code: str) -> None:
    """Renderiza o diagrama de Ishikawa."""
    ai_results = details.get("ai_results", {})
    if "ishikawa" in ai_results:
        with st.expander(texts["ishikawa_expander"]):
            plot_ishikawa(ai_results["ishikawa"], texts, lang_code)


def _render_five_whys(details: Dict, texts: Dict, lang_code: str) -> None:
    """Renderiza os 5 Porquês."""
    ai_results = details.get("ai_results", {})
    if "five_whys" in ai_results:
        with st.expander(texts["five_whys_expander"]):
            display_five_whys(ai_results["five_whys"], "cards", texts, lang_code)


def _render_history(details: Dict, texts: Dict, lang_code: str) -> None:
    """Renderiza o histórico bruto e refinado com visual premium."""
    
    # Histórico bruto (visualização amigável + JSON)
    if details.get("broad_history_found"):
        history_count = len(details["broad_history_found"])
        expander_title = texts["broad_history_expander"].format(count=history_count)
        
        with st.expander(expander_title):
            # Tabs: Visual Amigável | JSON Técnico
            tab_visual, tab_json = st.tabs(["📋 Visualização", "🔧 JSON Técnico"])
            
            with tab_visual:
                for i, failure in enumerate(details["broad_history_found"]):
                    _render_history_card(failure, i + 1, texts)
            
            with tab_json:
                for i, failure in enumerate(details["broad_history_found"]):
                    analysis_title = texts["historical_analysis_title"].format(index=i+1)
                    st.markdown(analysis_title)
                    
                    cleaned_failure_data = clean_empty_values(failure)
                    st.json(cleaned_failure_data, expanded=True)
                    st.divider()
    
    # Histórico refinado pela IA (visual premium)
    if details.get("refined_history"):
        with st.expander(texts["history_expander"]):
            _render_refined_history_visual(details["refined_history"])


def _render_refined_history_visual(refined_history: str) -> None:
    """
    Renderiza o histórico correlacionado pela IA com visual premium estruturado.
    
    Estrutura o conteúdo da IA em cards visuais organizados, similar ao
    histórico bruto, mas adaptado para o formato de texto da IA.
    """
    # Header principal
    st.markdown(f"""
    <div style="{STYLE_REFINED_HISTORY}">
        <h4 style="color: #4ADE80; margin: 0 0 15px 0;">
            🔍 Análise de Correlação pela IA
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Processa o conteúdo da IA para extrair seções estruturadas
    correlated_failures = _parse_correlated_failures(refined_history)
    
    if correlated_failures:
        # Renderiza cada falha correlacionada como um card
        for i, failure in enumerate(correlated_failures):
            _render_correlated_failure_card(failure, i + 1)
    else:
        # Fallback: renderiza como texto simples se não conseguir parsear
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px; margin: 10px 0;">
        <div style="color: #E2E8F0; line-height: 1.6;">
        {html_lib.escape(refined_history)}
        </div>
        </div>
        """, unsafe_allow_html=True)


def _parse_correlated_failures(refined_history: str) -> List[Dict[str, str]]:
    """
    Parseia as falhas correlacionadas do texto da IA.
    
    Extrai cada falha no formato:
    - **Falha Histórica [número]:** [descrição]
    - **Relevância:** [explicação]
    - **Dados Relevantes:** [dados]
    """
    failures = []
    
    # Divide o texto em seções de falhas
    lines = refined_history.split('\n')
    current_failure = {}
    current_key = None
    
    for line in lines:
        line = line.strip()
        failures = []

        # Divide o texto em linhas para parsing robusto
        lines = refined_history.split('\n')
        current_failure = None
        current_key = None

        date_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})")

        def _start_new_failure(desc_text: str = ""):
            return {'description': desc_text.strip(), 'relevance': '', 'data': '', 'date': ''}

        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            # Início de nova falha (com ou sem marcador "- ")
            if re.search(r"\*\*Falha Histórica\s*\d+\s*:\*\*", line) or line.lower().startswith('falha histórica'):
                # salva anterior
                if current_failure and current_failure.get('description'):
                    failures.append(current_failure)

                # pega descrição após o título, se existir
                desc_match = re.search(r"\*\*Falha Histórica\s*\d+\s*:?\*\*\s*(.*)", line)
                desc = desc_match.group(1).strip() if desc_match and desc_match.group(1) else ''
                current_failure = _start_new_failure(desc)
                current_key = 'description'
                continue

            # Relevância
            if re.search(r"\*\*Relevância\s*:?\*\*", line) or line.lower().startswith('relevância'):
                current_key = 'relevance'
                # extrai conteúdo na mesma linha depois dos marcadores
                rel_match = re.search(r"\*\*Relevância\s*:?\*\*\s*(.*)", line)
                if rel_match and rel_match.group(1):
                    if current_failure:
                        current_failure['relevance'] = rel_match.group(1).strip()
                continue

            # Dados Relevantes
            if re.search(r"\*\*Dados Relevantes\s*:?\*\*", line) or line.lower().startswith('dados relevantes'):
                current_key = 'data'
                data_match = re.search(r"\*\*Dados Relevantes\s*:?\*\*\s*(.*)", line)
                if data_match and data_match.group(1):
                    if current_failure:
                        current_failure['data'] = data_match.group(1).strip()
                continue

            # Linhas de continuação: adiciona ao campo atual
            if current_key and current_failure is not None:
                # remove leading markers
                content = re.sub(r'^[-\*\s]+', '', line).strip()

                # se conteúdo contém data, extraí-la e remove do texto de dados
                date_found = date_pattern.search(content)
                if date_found:
                    current_failure['date'] = date_found.group(1)
                    # remove apenas a data da string para manter legibilidade
                    content = content.replace(date_found.group(1), '').strip(' -:')

                if current_failure.get(current_key):
                    current_failure[current_key] += '\n' + content
                else:
                    current_failure[current_key] = content
                continue

            # Caso não haja key atual, tenta capturar linhas soltas que contenham data
            if current_failure is not None:
                date_found = date_pattern.search(line)
                if date_found and not current_failure.get('date'):
                    current_failure['date'] = date_found.group(1)

        # adiciona ultima
        if current_failure and current_failure.get('description'):
            failures.append(current_failure)

        return failures
def _render_correlated_failure_card(failure: Dict[str, str], index: int) -> None:
    """
    Renderiza um card para uma falha correlacionada, seguindo o mesmo estilo do histórico bruto.
    """
    description = failure.get('description', 'N/A')
    relevance = failure.get('relevance', '')
    data = failure.get('data', '')
    
    # Escape dos valores
    description_esc = html_lib.escape(str(description)) if description else "N/A"
    relevance_esc = html_lib.escape(str(relevance)) if relevance else ""
    data_esc = html_lib.escape(str(data)) if data else ""
    
    # Constrói HTML seguindo exatamente o padrão do histórico bruto
    html_parts = []
    
    # Container principal (mesmo estilo do histórico bruto)
    html_parts.append(f'<div style="{STYLE_HISTORY_CARD}">')
    
    # Header com número (igual ao histórico bruto) e data à direita
    date_val = failure.get('date', '')
    date_esc = html_lib.escape(date_val) if date_val else ''
    html_parts.append('<div style="display: flex; align-items: center; margin-bottom: 12px;">')
    html_parts.append(f'<div style="width: 32px; height: 32px; background: linear-gradient(135deg, #22C55E 0%, #4ADE80 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; margin-right: 12px;">{index}</div>')
    html_parts.append(f'<div style="color: #4ADE80; font-weight: 600; font-size: 1.1em;">Falha Correlacionada #{index}</div>')
    if date_esc:
        html_parts.append(f'<div style="margin-left: auto; color: #9CA3AF; font-size: 0.9em;">📅 {date_esc}</div>')
    html_parts.append('</div>')
    
    # Descrição da falha (seguindo o padrão do histórico bruto)
    html_parts.append('<div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 10px; margin-top: 10px;">')
    html_parts.append('<div style="color: #4ADE80; font-weight: 600; margin-bottom: 5px;">📝 Descrição da Falha:</div>')
    # Quebra de parágrafos: preserva quebras de linha
    description_html = '<br>'.join(html_lib.escape(line.strip()) for line in str(description).split('\n') if line.strip())
    html_parts.append(f'<div style="color: #E2E8F0; line-height: 1.5;">{description_html}</div>')
    html_parts.append('</div>')
    
    # Relevância (usando o estilo verde do histórico bruto para causa raiz)
    if relevance_esc:
        relevance_html = '<br>'.join(html_lib.escape(line.strip()) for line in str(relevance).split('\n') if line.strip())
        html_parts.append('<div style="background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22C55E; border-radius: 6px; padding: 10px; margin-top: 10px;">')
        html_parts.append('<div style="color: #4ADE80; font-weight: 600; margin-bottom: 5px;">🎯 Relevância Técnica:</div>')
        html_parts.append(f'<div style="color: #E2E8F0; line-height: 1.5;">{relevance_html}</div>')
        html_parts.append('</div>')
    
    # Dados relevantes (usando o estilo laranja do histórico bruto para ações)
    if data_esc:
        # Extrai novamente a data para exibir (caso não tivesse sido capturada antes)
        if not date_esc:
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', data_esc)
            if date_match:
                date_esc = date_match.group(1)
        data_html = '<br>'.join(html_lib.escape(line.strip()) for line in str(data).split('\n') if line.strip())
        html_parts.append('<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #F59E0B; border-radius: 6px; padding: 10px; margin-top: 10px;">')
        html_parts.append('<div style="color: #FBBF24; font-weight: 600; margin-bottom: 5px;">📋 Dados Relevantes:</div>')
        html_parts.append(f'<div style="color: #E2E8F0; line-height: 1.5;">{data_html}</div>')
        html_parts.append('</div>')
    
    # Fecha container principal
    html_parts.append('</div>')
    
    # Renderiza o HTML completo
    full_html = ''.join(html_parts)
    st.markdown(full_html, unsafe_allow_html=True)


def _extract_section_from_raw_response(raw_response: str, section_title: str) -> str:
    """
    Extrai uma seção específica da resposta bruta da IA.
    
    Args:
        raw_response: Texto bruto da resposta da IA.
        section_title: Título da seção a extrair (ex: "Conclusão Final").
    
    Returns:
        Conteúdo da seção ou string vazia se não encontrada.
    """
    # Padrão para encontrar seções no formato **Título**
    sections = re.split(r'\*\*([^*]+)\*\*', raw_response)
    
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        content = sections[i + 1] if i + 1 < len(sections) else ""
        if section_title in title:
            return content.strip()
    
    return ""


def _render_conclusion(details: Dict, texts: Dict) -> None:
    """
    Renderiza a seção 'Conclusão Final' extraída da resposta bruta da IA.
    
    Extrai e exibe a conclusão final do raw_response com visual premium,
    mantendo consistência com o estilo das outras seções.
    """
    raw_response = details.get("ai_results", {}).get("raw_response", "")
    if not raw_response:
        return
    
    # Extrair a seção "Conclusão Final" do raw_response
    conclusion_section = _extract_section_from_raw_response(raw_response, "Conclusão Final")
    if not conclusion_section:
        return
    
    # Estilo premium para conclusão do raw response (roxo, como definido em raw_response.py)
    style_conclusion_raw = "background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(196, 181, 253, 0.1) 100%); border: 1px solid rgba(168, 85, 247, 0.3); border-left: 4px solid #A855F7; border-radius: 10px; padding: 20px 25px;"
    
    with st.expander("🏁 Conclusão Final"):
        # Header estilizado
        st.markdown(f'''
        <div style="{style_conclusion_raw}">
            <h4 style="color: #C4B5FD; margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                🏁 Conclusão Final da Análise
            </h4>
            <div style="color: #E2E8F0; line-height: 1.7; font-size: 1.05em;">
                {html_lib.escape(conclusion_section)}
            </div>
        </div>
        ''', unsafe_allow_html=True)


def _get_field(data: Dict, *keys, default: str = "N/A") -> str:
    """
    Extrai um campo do dicionário tentando múltiplas chaves.
    
    Lida com valores que podem ser strings, listas ou dicts,
    convertendo para uma representação legível.
    """
    for key in keys:
        value = data.get(key)
        if value is not None and value != "":
            # Se for lista, formata como itens
            if isinstance(value, list):
                # Filtra itens vazios/None
                items = []
                for item in value:
                    if isinstance(item, dict):
                        # Para dicts dentro de lista (ex: 5 Porquês)
                        # Extrai campos relevantes
                        causa = item.get("Causa", item.get("causa", ""))
                        tipo = item.get("Tipo", item.get("tipo", ""))
                        if causa and causa != "None":
                            if tipo and tipo != "None":
                                items.append(f"{tipo}: {causa}")
                            else:
                                items.append(str(causa))
                    elif item and str(item).strip() and str(item) != "None":
                        items.append(str(item))
                
                if items:
                    return " | ".join(items[:3])  # Limita a 3 itens
                continue
            
            # Se for dict, tenta extrair valor principal
            if isinstance(value, dict):
                for sub_key in ["valor", "value", "texto", "text", "descricao"]:
                    if sub_key in value:
                        return str(value[sub_key])
                continue
            
            return str(value)
    
    return default


def _render_history_card(failure: Dict, index: int, texts: Dict) -> None:
    """Renderiza um card visual para uma falha histórica."""
    
    # Extrai campos com múltiplas alternativas de nomes
    area = _get_field(failure, "Área", "area", "Area")
    equipment = _get_field(failure, "Equipamento", "equipamento", "Equipment")
    subgroup = _get_field(failure, "Subgrupo", "subgrupo", "Subgroup")
    
    # Descrição pode ter vários nomes
    description = _get_field(
        failure, 
        "Descrição do Problema", "O que", "descricao_falha", 
        "Descrição", "description", "Problema"
    )
    
    # Data
    date = _get_field(failure, "Quando", "data", "Data", "Date")
    
    # Causa raiz - pode ser string ou extraído de 5 Porquês
    root_cause = _get_field(failure, "Causa Raiz", "causa_raiz", "Root Cause", default="")
    if not root_cause or root_cause == "N/A":
        # Tenta extrair de 5 Porquês se existir
        five_whys = failure.get("5 Porquês", failure.get("5_porques", []))
        if isinstance(five_whys, list) and five_whys:
            first_why = five_whys[0] if five_whys else {}
            if isinstance(first_why, dict):
                root_cause = first_why.get("Causa ou Efeito", first_why.get("causa", ""))
    
    # Ação corretiva - pode ser lista
    action = _get_field(
        failure, 
        "Ação de Contenção", "acao_corretiva", "Ação", 
        "Ações Corretivas", "Action", default=""
    )
    
    # Escape dos valores
    area_esc = html_lib.escape(str(area)) if area else "N/A"
    equipment_esc = html_lib.escape(str(equipment)) if equipment else "N/A"
    subgroup_esc = html_lib.escape(str(subgroup)) if subgroup else "N/A"
    description_esc = html_lib.escape(str(description)) if description else "N/A"
    date_esc = html_lib.escape(str(date)) if date else "N/A"
    root_cause_esc = html_lib.escape(str(root_cause)) if root_cause and root_cause != "N/A" else ""
    action_esc = html_lib.escape(str(action)) if action and action != "N/A" else ""
    
    # Constrói HTML de forma limpa
    html_parts = []
    
    # Container principal
    html_parts.append(f'<div style="{STYLE_HISTORY_CARD}">')
    
    # Header com número e data
    html_parts.append('<div style="display: flex; align-items: center; margin-bottom: 12px;">')
    html_parts.append(f'<div style="width: 32px; height: 32px; background: linear-gradient(135deg, #A855F7 0%, #C4B5FD 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; margin-right: 12px;">{index}</div>')
    html_parts.append(f'<div style="color: #C4B5FD; font-weight: 600; font-size: 1.1em;">Falha Histórica #{index}</div>')
    html_parts.append(f'<div style="margin-left: auto; color: #9CA3AF; font-size: 0.9em;">📅 {date_esc}</div>')
    html_parts.append('</div>')
    
    # Grid com Área e Equipamento
    html_parts.append('<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">')
    html_parts.append(f'<div><span style="color: #A855F7; font-weight: 600;">🏭 Área:</span> <span style="color: #E2E8F0;">{area_esc}</span></div>')
    html_parts.append(f'<div><span style="color: #A855F7; font-weight: 600;">⚙️ Equipamento:</span> <span style="color: #E2E8F0;">{equipment_esc}</span></div>')
    html_parts.append('</div>')
    
    # Subgrupo
    html_parts.append('<div style="margin-bottom: 10px;">')
    html_parts.append(f'<span style="color: #A855F7; font-weight: 600;">📦 Subgrupo:</span> <span style="color: #E2E8F0;">{subgroup_esc}</span>')
    html_parts.append('</div>')
    
    # Descrição
    html_parts.append('<div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 10px; margin-top: 10px;">')
    html_parts.append('<div style="color: #A855F7; font-weight: 600; margin-bottom: 5px;">📝 Descrição:</div>')
    html_parts.append(f'<div style="color: #E2E8F0; line-height: 1.5;">{description_esc}</div>')
    html_parts.append('</div>')
    
    # Causa Raiz (opcional)
    if root_cause_esc:
        html_parts.append('<div style="background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22C55E; border-radius: 6px; padding: 10px; margin-top: 10px;">')
        html_parts.append('<div style="color: #4ADE80; font-weight: 600; margin-bottom: 5px;">🎯 Causa Raiz:</div>')
        html_parts.append(f'<div style="color: #E2E8F0; line-height: 1.5;">{root_cause_esc}</div>')
        html_parts.append('</div>')
    
    # Ação Corretiva (opcional)
    if action_esc:
        html_parts.append('<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #F59E0B; border-radius: 6px; padding: 10px; margin-top: 10px;">')
        html_parts.append('<div style="color: #FBBF24; font-weight: 600; margin-bottom: 5px;">🔧 Ação Corretiva:</div>')
        html_parts.append(f'<div style="color: #E2E8F0; line-height: 1.5;">{action_esc}</div>')
        html_parts.append('</div>')
    
    # Fecha container principal
    html_parts.append('</div>')
    
    # Renderiza o HTML completo
    full_html = ''.join(html_parts)
    st.markdown(full_html, unsafe_allow_html=True)


def _render_tokens(result: Dict, texts: Dict) -> None:
    """Renderiza as métricas de tokens e custo com visual premium."""
    with st.expander("📏 Tokens"):
        token_details = result.get("token_details", {})
        
        # Cálculo de totais
        input_tokens = (
            token_details.get("prompt_tokens", 0) + 
            token_details.get("history_input_tokens", 0)
        )
        output_tokens = (
            token_details.get("response_tokens", 0) +
            token_details.get("history_output_tokens", 0) +
            token_details.get("media_output_tokens", 0)
        )
        total_tokens = input_tokens + output_tokens

        # Custo estimado (baseado em preços do Gemini)
        input_cost = input_tokens / 1000 * 0.0115
        output_cost = output_tokens / 1000 * 0.0115
        total_cost = input_cost + output_cost

        # Layout em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="{STYLE_CARD}; text-align: center;">
                <div style="color: #60A5FA; font-size: 0.9em;">📥 Input</div>
                <div style="color: #E2E8F0; font-size: 1.3em; font-weight: bold;">{input_tokens:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="{STYLE_CARD}; text-align: center;">
                <div style="color: #4ADE80; font-size: 0.9em;">📤 Output</div>
                <div style="color: #E2E8F0; font-size: 1.3em; font-weight: bold;">{output_tokens:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="{STYLE_CARD}; text-align: center;">
                <div style="color: #FBBF24; font-size: 0.9em;">💰 Custo</div>
                <div style="color: #E2E8F0; font-size: 1.3em; font-weight: bold;">US$ {total_cost:.4f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Verificação do limite de tokens
        if token_details.get("prompt_tokens", 0) <= 30000:
            st.success(texts["token_ok"])
        else:
            st.warning(texts["token_exceeded"])


def _render_download_button(result: Dict, texts: Dict, lang_code: str) -> None:
    """Renderiza o botão de download do relatório."""
    markdown_content = generate_markdown_result(result, lang_code)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"resultado_{result['folder'].replace('/', '_')}_{timestamp}.md"
    
    st.download_button(
        label=texts["download_button"],
        data=markdown_content,
        file_name=filename,
        mime="text/markdown"
    )
