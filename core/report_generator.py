# core/report_generator.py
from pathlib import Path
import os
from datetime import datetime
import logging
from ui.texts import TEXTS # Importa o dicionário de textos

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, language: str = "pt"):
        self.language = language
        self.texts = TEXTS.get(self.language, TEXTS['en'])

    def generate_report(self, results: list) -> None:
        """Gera relatórios em Markdown para cada resultado no idioma definido."""
        output_dir = Path("relatorios")
        output_dir.mkdir(exist_ok=True)

        for result in results:
            folder_name = result.get("folder", "sem_nome")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            safe_folder_name = "".join(c if c.isalnum() else "_" for c in folder_name)
            filename = output_dir / f"relatorio_{safe_folder_name}_{timestamp}.md"

            content = self._generate_report_content(result, folder_name, timestamp)

            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Relatório gerado: {filename}")
            except Exception as e:
                logger.error(f"Erro ao gerar relatório {filename}: {str(e)}")

    def _generate_report_content(self, result: dict, folder_name: str, timestamp: str) -> str:
        """Gera o conteúdo do relatório com base no idioma."""
        
        t = self.texts 
        content = f"# Relatório de Análise de Falha - {folder_name} - {timestamp}\n\n"
        
        content += f"## {t['excel_data']}\n"
        if result.get("status") == "error":
            content += f"- Erro: {result.get('details', 'Detalhes não disponíveis')}\n"
            return content

        details = result.get("details", {})
        excel_data = details.get('excel_data', {})
        content += f"- {t['area']}: {excel_data.get('area', 'N/A')}\n"
        content += f"- {t['equipment']}: {excel_data.get('equipment', 'N/A')}\n"
        content += f"- {t['subgroup']}: {excel_data.get('subgroup', 'N/A')}\n"
        content += f"- {t['description']}: {excel_data.get('description', 'N/A')}\n\n"

        if details.get("video_results"):
            content += f"## {t['video_analysis_title']}\n{details['video_results']}\n\n"

        if details.get("image_results"):
            content += f"## {t['image_analysis']}\n{details['image_results']}\n\n"
        
        if details.get("refined_history"):
            content += f"## {t['history_expander']}\n"
            content += f"{details['refined_history']}\n\n"

        ai_results = details.get('ai_results', {})
        if ai_results.get("raw_response"):
            content += f"## {t['raw_response']}\n"
            content += f"```markdown\n{ai_results['raw_response']}\n```\n\n"
        
        # --- FIX: Acessa a estrutura aninhada de forma segura ---
        token_details = ai_results.get('token_details', {})
        total_tokens = token_details.get('total_tokens', 0)
        
        if total_tokens > 0:
            content += f"## {t['tokens_title_md']}\n"
            content += f"- {t['tokens_used_md']}: **{total_tokens}**\n\n"
        # --- FIM DO FIX ---

        return content