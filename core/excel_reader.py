#core/excel_reader.py
"""
Módulo responsável pela extração de dados de arquivos Excel.

Este módulo contém a classe ExcelReader que extrai informações
específicas de planilhas de análise de falhas no formato A3,
utilizado na metodologia de resolução de problemas.
"""
from pathlib import Path
import openpyxl
import warnings
from openpyxl.utils import get_column_letter

# Suprimir avisos do openpyxl (relacionados a estilos não suportados)
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


class ExcelReader:
    """
    Leitor de dados de planilhas Excel no formato A3 de Análise de Falhas.
    
    Esta classe extrai informações estruturadas de planilhas que seguem
    o template padrão da metodologia A3 para resolução de problemas,
    especificamente da aba 'A3 Time de Resolução de Prob'.
    
    Attributes:
        Nenhum atributo de instância é armazenado. A classe opera de
        forma stateless, processando cada arquivo independentemente.
    
    Example:
        >>> reader = ExcelReader()
        >>> resultado = reader.read_excel(Path("analise.xlsx"))
        >>> if resultado["status"] == "success":
        ...     dados = resultado["data"]
    """
    
    def read_excel(self, excel_path: Path) -> dict:
        """Lê as células específicas da aba 'A3 Time de Resolução de Prob'."""
        try:
            workbook = openpyxl.load_workbook(excel_path, data_only=True)
            sheet = workbook["A3 Time de Resolução de Prob"]

            def get_cell_value(cell_ref: str) -> str:
                """Obtém o valor de uma célula, considerando células mescladas."""
                cell = sheet[cell_ref]
                for merged_range in sheet.merged_cells.ranges:
                    if cell.coordinate in merged_range:
                        return str(sheet[merged_range.start_cell.coordinate].value or "Não informado")
                return str(cell.value or "Não informado")

            data = {
                "area": get_cell_value("E16"),
                "equipment": get_cell_value("E17"),
                "subgroup": get_cell_value("E18"),
                "description": get_cell_value("B20")
            }
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "error": f"Erro ao ler Excel: {str(e)}"}
