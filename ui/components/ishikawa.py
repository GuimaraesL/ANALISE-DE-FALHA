# ui/components/ishikawa.py
"""
Componente de visualização do Diagrama de Ishikawa.

Este módulo contém a função para gerar e renderizar o diagrama de
Ishikawa (espinha de peixe) usando matplotlib, com design estilizado
incluindo cabeça de peixe e categorias coloridas dos 6Ms.
"""
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def plot_ishikawa(ishikawa_data: Dict[str, Any], texts: Dict[str, str], lang_code: str = "pt") -> None:
    """
    Renderiza o diagrama de Ishikawa (espinha de peixe) com matplotlib.
    
    Gera uma visualização gráfica das causas raiz organizadas nas 6 categorias
    dos 6Ms (Material, Máquina, Método, Mão de obra, Meio ambiente, Medição).
    
    Args:
        ishikawa_data: Dicionário com estrutura:
            {"causes": {"Material": [...], "Máquina": [...], ...}}
        texts: Dicionário de textos traduzidos (para títulos e labels).
        lang_code: Código do idioma ('pt' para português, 'en' para inglês).
    
    Example:
        >>> data = {
        ...     "causes": {
        ...         "Material": ["Fadiga do aço", "Corrosão"],
        ...         "Máquina": ["Desgaste do rolamento"],
        ...     }
        ... }
        >>> plot_ishikawa(data, TEXTS["pt"], "pt")
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 22)
    ax.set_ylim(-10, 10)
    ax.axis("off")

    # Linha central (espinha)
    ax.plot([4, 19], [0, 0], color="#FF6600", lw=3)

    # Cabeça de peixe (efeito)
    head = mpath.Path(
        [(19, -2), (21, 0), (19, 2), (19, -2)],
        [mpath.Path.MOVETO, mpath.Path.LINETO, mpath.Path.LINETO, mpath.Path.CLOSEPOLY]
    )
    patch = patches.PathPatch(head, facecolor="#FF6600", edgecolor="black", lw=2)
    ax.add_patch(patch)
    ax.text(20, 0, texts["ishikawa_effect"], va="center", ha="center", fontsize=12, fontweight="bold", color="white")

    # Categorias alternadas (cima/baixo)
    categorias = list(ishikawa_data["causes"].keys())
    y_positions = [6, 4, 2, -2, -4, -6]

    for idx, (categoria, y_cat) in enumerate(zip(categorias, y_positions)):
        y_target = 0
        x_base = 4 + (idx + 1) * 2

        # Linha da categoria conectando ao eixo central
        ax.plot([x_base, x_base], [y_target, y_cat], color="#1E3A8A", lw=2)

        # Caixa da categoria (label)
        ax.add_patch(patches.FancyBboxPatch(
            (x_base - 1.2, y_cat - 0.6), 2.4, 1.2,
            boxstyle="round,pad=0.3", fc="#1E3A8A", ec="black"
        ))
        ax.text(x_base, y_cat, categoria, va="center", ha="center", fontsize=10, color="white", fontweight="bold")

        # Causas como sub-ramos
        causas = ishikawa_data["causes"].get(categoria, [])
        for j, causa in enumerate(causas):
            offset = 0.8 * (j + 1)
            sinal = 1 if y_cat > 0 else -1
            y_causa = y_cat + sinal * offset
            x_causa = x_base + (1.5 if y_cat > 0 else -1.5)
            
            ax.plot([x_base, x_causa], [y_cat, y_causa], color="#2563EB", lw=1.5)
            ax.text(
                x_causa + (0.3 if y_cat > 0 else -0.3), 
                y_causa,
                f"- {causa}", 
                va="center",
                ha="left" if y_cat > 0 else "right",
                fontsize=9
            )

    ax.set_title(texts["ishikawa_title"], fontsize=16, pad=20)
    st.pyplot(fig)
    plt.close(fig)
    
    logger.debug(f"Diagrama de Ishikawa renderizado com {len(categorias)} categorias")
