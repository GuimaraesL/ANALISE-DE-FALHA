#core/excel_reader.py responsavel por ler dados do excel
from pathlib import Path
import openpyxl
import warnings
from openpyxl.utils import get_column_letter

# Suprimir avisos do openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

class ExcelReader:
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
