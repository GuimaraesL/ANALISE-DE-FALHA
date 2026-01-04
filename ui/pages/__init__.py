# ui/pages/__init__.py
"""
Pacote de páginas da aplicação Streamlit.

Este pacote contém módulos que encapsulam a lógica de renderização
de diferentes seções da interface: sidebar e área de resultados.
"""
from ui.pages.sidebar import render_sidebar
from ui.pages.results import render_results

__all__ = [
    "render_sidebar",
    "render_results",
]
