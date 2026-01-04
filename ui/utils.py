# ui/utils.py
"""
Funções utilitárias para a camada de UI.

Este módulo contém funções auxiliares usadas pelos componentes de UI,
como geração de conteúdo para download e limpeza de dados.
"""
from datetime import datetime
from typing import Dict, Any, List, Union
import logging

from ui.texts import TEXTS

logger = logging.getLogger(__name__)


def generate_markdown_result(result: Dict[str, Any], lang_code: str = "pt") -> str:
    """
    Gera o conteúdo Markdown para download do resultado da análise.
    
    Args:
        result: Dicionário com os resultados da análise, contendo:
            - folder: Nome da pasta analisada
            - status: "success" ou "error"
            - details: Dicionário com excel_data, ai_results, etc.
            - token_details: Métricas de tokens
        lang_code: Código do idioma ('pt' ou 'en').
    
    Returns:
        String formatada em Markdown pronta para download.
    
    Example:
        >>> md = generate_markdown_result(result, "pt")
        >>> with open("resultado.md", "w") as f:
        ...     f.write(md)
    """
    texts = TEXTS[lang_code]
    markdown = f"# Pasta / Folder: {result['folder']}\n\n"

    if result["status"] == "error":
        return markdown + f"**Erro / Error**: {result['details']}\n"

    details = result.get("details", {})

    # Dados do Excel
    markdown += f"## {texts['excel_data']}\n"
    if "excel_data" in details:
        excel_data = details["excel_data"]
        markdown += f"- {texts['area']}: {excel_data.get('area', 'N/A')}\n"
        markdown += f"- {texts['equipment']}: {excel_data.get('equipment', 'N/A')}\n"
        markdown += f"- {texts['subgroup']}: {excel_data.get('subgroup', 'N/A')}\n"
        markdown += f"- {texts['description']}: {excel_data.get('description', 'N/A')}\n"
    else:
        markdown += "⚠️ Dados do Excel não disponíveis.\n"

    # Análise de Mídias
    markdown += f"\n## {texts['video_analysis_title']}\n{details.get('video_results', 'N/A')}\n"
    markdown += f"\n## {texts['image_analysis']}\n{details.get('image_results', 'N/A')}\n"

    # Correlação histórica (refined_history)
    refined_history = details.get("refined_history", "").strip()
    if refined_history:
        markdown += f"\n## {texts['correlation_title_md']}\n{refined_history}\n"

    # Resposta bruta da IA
    raw_response = details.get('ai_results', {}).get('raw_response', 'N/A')
    markdown += f"\n## {texts['raw_response']}\n```markdown\n{raw_response}\n```"

    # Métricas de Tokens
    tokens = result.get("token_details", {})
    input_tokens = tokens.get("prompt_tokens", 0) + tokens.get("history_input_tokens", 0)
    output_tokens = (
        tokens.get("response_tokens", 0) +
        tokens.get("history_output_tokens", 0) +
        tokens.get("media_output_tokens", 0)
    )
    total_tokens = tokens.get("total", input_tokens + output_tokens)

    markdown += f"\n## {texts['tokens_title_md']}\n"
    markdown += f"- {texts['tokens_input']} **{input_tokens}**\n"
    markdown += f"- {texts['tokens_output']} **{output_tokens}**\n"
    markdown += f"- {texts['token_total']} **{total_tokens}**\n"
    
    # Custo estimado (baseado em preços do Gemini)
    total_cost = total_tokens / 1000 * 0.0115
    markdown += f"\n**{texts['analysis_cost']}** US$ {total_cost:.6f}\n"

    logger.debug(f"Markdown gerado para pasta '{result['folder']}' ({len(markdown)} chars)")
    return markdown


def clean_empty_values(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Remove recursivamente valores vazios de estruturas de dados.
    
    Remove chaves de dicionários e itens de listas que sejam:
    - None
    - Strings vazias ("")
    - Listas vazias ([])
    - Dicionários vazios ({})
    
    Args:
        data: Estrutura de dados a ser limpa (dict, list ou valor primitivo).
    
    Returns:
        Estrutura de dados limpa, sem valores vazios.
    
    Example:
        >>> data = {"a": "valor", "b": "", "c": None, "d": []}
        >>> clean_empty_values(data)
        {'a': 'valor'}
    """
    if isinstance(data, dict):
        cleaned_dict = {
            k: clean_empty_values(v) 
            for k, v in data.items() 
            if v is not None and v != "" and v != []
        }
        return {
            k: v 
            for k, v in cleaned_dict.items() 
            if v is not None and v != "" and v != [] and v != {}
        }
    
    if isinstance(data, list):
        cleaned_list = [
            clean_empty_values(item) 
            for item in data 
            if item is not None and item != ""
        ]
        return [
            item 
            for item in cleaned_list 
            if item is not None and item != "" and item != [] and item != {}
        ]
    
    return data
