# ui/components/__init__.py
"""
Pacote de componentes de UI reutilizáveis.

Este pacote contém componentes visuais específicos que podem ser
importados e utilizados em diferentes partes da aplicação.

Componentes disponíveis:
- IshikawaChart: Diagrama de Ishikawa (espinha de peixe)
- FiveWhysDisplay: Cards dos 5 Porquês
- RawResponseDisplay: Resposta bruta estilizada da IA
"""
from ui.components.ishikawa import plot_ishikawa
from ui.components.five_whys import display_five_whys
from ui.components.raw_response import display_raw_response

__all__ = [
    "plot_ishikawa",
    "display_five_whys", 
    "display_raw_response",
]
