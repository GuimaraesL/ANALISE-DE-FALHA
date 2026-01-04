# ui/__init__.py
"""
Pacote de interface do usuário (UI) da aplicação de Análise de Falhas.

Este pacote contém todos os módulos relacionados à interface Streamlit,
organizados em subpacotes para melhor manutenibilidade:

Módulos:
    texts: Internacionalização (i18n) com textos em PT/EN
    styles: Carregamento e gerenciamento de CSS
    utils: Funções utilitárias (geração de markdown, limpeza de dados)

Subpacotes:
    components: Componentes visuais reutilizáveis (Ishikawa, 5 Porquês)
    pages: Módulos de páginas (sidebar, resultados)

Example:
    >>> from ui.styles import load_css
    >>> from ui.pages import render_sidebar, render_results
    >>> from ui.components import plot_ishikawa
"""
from ui.texts import TEXTS
from ui.styles import load_css
from ui.utils import generate_markdown_result, clean_empty_values

__all__ = [
    "TEXTS",
    "load_css",
    "generate_markdown_result",
    "clean_empty_values",
]
