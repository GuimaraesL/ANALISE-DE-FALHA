# ui/components/five_whys.py
"""
Componente de visualização dos 5 Porquês.

Este módulo contém a função para renderizar a análise dos 5 Porquês
em diferentes formatos: cards verticais modernos, colunas lado a lado
ou lista simples.
"""
import streamlit as st
import html as html_lib
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def display_five_whys(
    five_whys: List[str], 
    display_mode: str = "cards", 
    texts: Optional[Dict[str, str]] = None, 
    lang_code: str = "pt"
) -> None:
    """
    Exibe os 5 Porquês com layout moderno em cards verticais.
    
    Args:
        five_whys: Lista de strings no formato "Pergunta: Resposta".
        display_mode: Modo de exibição:
            - "cards": Cards verticais com numeração (padrão)
            - "columns": Layout em colunas lado a lado
            - "list": Lista simples
        texts: Dicionário de textos traduzidos.
        lang_code: Código do idioma ('pt' ou 'en').
    
    Example:
        >>> whys = [
        ...     "Por que o motor parou?: Superaquecimento",
        ...     "Por que houve superaquecimento?: Falta de lubrificação",
        ... ]
        >>> display_five_whys(whys, "cards", TEXTS["pt"])
    """
    if not five_whys:
        if texts:
            st.write(texts.get("no_five_whys", "Nenhuma análise disponível"))
        else:
            st.write("Nenhuma análise disponível")
        return

    if display_mode == "cards":
        _render_cards_mode(five_whys)
    elif display_mode == "columns":
        _render_columns_mode(five_whys)
    else:
        _render_list_mode(five_whys, texts)
    
    logger.debug(f"5 Porquês renderizados: {len(five_whys)} itens no modo '{display_mode}'")


def _render_cards_mode(five_whys: List[str]) -> None:
    """Renderiza os 5 Porquês em cards verticais modernos."""
    for i, why in enumerate(five_whys[:5]):
        parts = why.split(":", 1)
        pergunta = html_lib.escape(parts[0].strip())
        resposta = html_lib.escape(parts[1].strip()) if len(parts) > 1 else ""
        
        card_html = f'''
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 15px;
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
            border: 1px solid rgba(37, 99, 235, 0.3);
            border-radius: 10px;
            padding: 15px 18px;
            margin-bottom: 12px;
        ">
            <div style="
                flex-shrink: 0;
                width: 36px;
                height: 36px;
                background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 16px;
                color: #FFFFFF;
                box-shadow: 0 2px 8px rgba(30, 58, 138, 0.4);
            ">{i + 1}</div>
            <div style="flex: 1; line-height: 1.6;">
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 6px; font-size: 1rem;">{pergunta}</div>
                <div style="opacity: 0.9; font-size: 0.95rem;">{resposta}</div>
            </div>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)


def _render_columns_mode(five_whys: List[str]) -> None:
    """Renderiza os 5 Porquês em colunas lado a lado (layout legado)."""
    cols = st.columns(min(len(five_whys), 5))
    for i, why in enumerate(five_whys[:5]):
        parts = why.split(":", 1)
        pergunta = parts[0].strip()
        resposta = parts[1].strip() if len(parts) > 1 else ""
        with cols[i]:
            st.markdown(
                f"<div style='background-color: rgba(255, 255, 255, 0.05); "
                f"border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 5px; "
                f"padding: 10px; margin: 5px;'><strong>{pergunta}</strong><br>{resposta}</div>",
                unsafe_allow_html=True
            )


def _render_list_mode(five_whys: List[str], texts: Optional[Dict[str, str]]) -> None:
    """Renderiza os 5 Porquês como lista simples (fallback)."""
    if texts:
        st.write(texts.get("five_whys_title", "5 Porquês"))
    for why in five_whys[:5]:
        st.write(f"- {why}")
