# core/failure_analysis_app.py
from asyncio.log import logger
import os
from pathlib import Path
from core.excel_reader import ExcelReader
from core.image_analyzer import ImageAnalyzer
from core.ai_processor import AIProcessor, estimate_tokens
from core.report_generator import ReportGenerator
from core.video_analyzer import VideoAnalyzer
import streamlit as st
from core.config_loader import load_config
from ui.texts import TEXTS
from core.history_manager import HistoryManager
from core.prompts import history_section
import re
import time
from datetime import datetime

config = load_config()

# FIX: Listas de extensões para facilitar a manutenção
IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.gif", "*.heic", "*.heif", "*.bmp", "*.tiff"]
VIDEO_EXTENSIONS = ["*.mp4", "*.mov", "*.avi", "*.wmv", "*.mkv", "*.webm"]


class FailureAnalysisApp:
    def __init__(self, root_folder: str, gemini_api_key: str, enable_images: bool = True, enable_videos: bool = True, language: str = "pt"):
        """Inicializa a aplicação de análise de falhas com todas as suas dependências."""
        self.root_folder = Path(root_folder)
        self.enable_images = enable_images
        self.enable_videos = enable_videos
        self.history_manager = HistoryManager("extracted_data.json")
        self.language = language
        self.excel_reader = ExcelReader()
        self.image_analyzer = ImageAnalyzer(gemini_api_key, language)
        self.video_analyzer = VideoAnalyzer(gemini_api_key, language)
        self.ai_processor = AIProcessor(gemini_api_key, language)
        self.report_generator = ReportGenerator(language)
        self.results = []

    def _find_files(self, folder_path: Path, extensions: list) -> list:
        """Função auxiliar para encontrar todos os arquivos com as extensões dadas."""
        files = []
        for ext in extensions:
            files.extend(folder_path.glob(ext))
        return files


    def _log_prompt(self, folder_name: str, final_prompt: str, refined_history: str):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        safe_folder_name = re.sub(r'[^\w\-_.]', '_', folder_name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"prompt_{safe_folder_name}_{timestamp}.txt"
        log_path = log_dir / log_filename
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                if refined_history:
                    f.write("--- INÍCIO DO HISTÓRICO REFINADO PELA IA ---\n")
                    f.write(refined_history + "\n")
                    f.write("--- FIM DO HISTÓRICO REFINADO ---\n\n")
                
                f.write("--- INÍCIO DO PROMPT FINAL ENVIADO ---\n")
                f.write(f"📁 Pasta: {folder_name}\n")
                f.write(f"📅 Data: {datetime.now().isoformat()}\n")
                f.write(f"🔢 Tokens: {self.ai_processor.get_last_token_count()}\n\n")
                f.write(final_prompt)
                f.write("\n--- FIM DO PROMPT FINAL ENVIADO ---")
            logger.info(f"Log do prompt salvo em: {log_path}")
        except Exception as e:
            logger.error(f"Falha ao salvar log do prompt para a pasta {folder_name}: {e}")


    def process_folder(self, folder_path: Path, progress_bar, status_text, processed_count, total_items) -> tuple[dict, int]:
        """
        Processa uma única pasta, atualizando a UI em tempo real.
        Retorna o dicionário de resultado e o novo contador de itens processados.
        """
        folder_name = folder_path.name
        texts = TEXTS[self.language]

        # --- Processa Excel ---
        excel_files = list(folder_path.glob("*.xlsx"))
        if not excel_files:
            return {"folder": folder_name, "status": "error", "details": "Nenhum arquivo Excel encontrado."}, processed_count
        
        status_text.info(f"Lendo Excel em: {folder_name}")
        excel_result = self.excel_reader.read_excel(excel_files[0])
        processed_count += 1
        progress_bar.progress(processed_count / total_items)
        if excel_result["status"] == "error":
            return {"folder": folder_name, "status": "error", "details": excel_result["error"]}, processed_count

        # --- Processa Vídeos ---
        video_results = ""
        if self.enable_videos:
            video_files = self._find_files(folder_path, VIDEO_EXTENSIONS)
            if video_files:
                status_text.info(f"Analisando {len(video_files)} vídeo(s) em: {folder_name}")
                video_results = self.video_analyzer.analyze_videos(video_files)
                processed_count += len(video_files)
                progress_bar.progress(processed_count / total_items)

        # --- Processa Imagens ---
        
        image_results = ""
        if self.enable_images:
            image_files = self._find_files(folder_path, IMAGE_EXTENSIONS)
            if image_files:
                status_text.info(f"Analisando {len(image_files)} imagem(ns) em: {folder_name}")
                image_results = self.image_analyzer.analyze_images(image_files)
                processed_count += len(image_files)
                progress_bar.progress(processed_count / total_items)

        
        raw_media_analyses = f"{image_results}\n\n{video_results}".strip()
        media_tokens = estimate_tokens(raw_media_analyses)


        # Etapa 3: RAG - Estágio 1 (Filtro por Código)
        status_text.info(texts["history_searching"].format(folder_name=folder_name))
        broad_historical_failures = self.history_manager.find_related_failures(excel_result["data"])

        # Etapa 4: RAG - Estágio 2 (Refinamento Semântico com IA)
        refined_history_text = ""
        refined_history_tokens = 0
        if broad_historical_failures:
            status_text.info(
                texts["history_refining"].format(count=len(broad_historical_failures))
            )
            refined_history_text, history_tokens_data = self.ai_processor.refine_history_with_ai(
                excel_result["data"].get("description", ""),
                broad_historical_failures
            )

            
        
        # Etapa 5: Análise Final com IA
        status_text.info(texts["generating_rca"].format(folder_name=folder_name))
        final_prompt = self.ai_processor.build_prompt(
            excel_data=excel_result["data"],
            media_analyses=raw_media_analyses,
            refined_history=refined_history_text
        )
        ai_results = self.ai_processor.process_with_gemini(final_prompt)

               # FIX: Contabiliza a etapa de análise da IA como uma unidade de trabalho
        processed_count += 1
        progress_bar.progress(processed_count / total_items)
        
        self._log_prompt(folder_name, final_prompt, refined_history_text)
        print("📊 TOKENS DEBUG >>>", media_tokens, refined_history_tokens, ai_results.get("token_count", 0))


        # --- Etapa 6: Empacotar Resultados ---
        result_data = {
            "folder": folder_name,
            "status": "success",
            "details": {
                "excel_data": excel_result["data"],
                "image_results": image_results,
                "video_results": video_results,
                "ai_results": ai_results,
               "broad_history_found": broad_historical_failures, 
               "refined_history": refined_history_text 
            },
            "token_details": {
                "media_tokens": media_tokens,
                "history_input_tokens": history_tokens_data["input_tokens"],
                "history_output_tokens": history_tokens_data["output_tokens"],
                "history_total": history_tokens_data["total_tokens"],
                "prompt_tokens": ai_results.get("token_details", {}).get("input_tokens", 0),
                "response_tokens": ai_results.get("token_details", {}).get("output_tokens", 0),
                "total": media_tokens + history_tokens_data["total_tokens"] + ai_results.get("token_details", {}).get("total_tokens", 0)
            }

            }

        
        return result_data, processed_count
        

    def run(self):
        """
        Orquestra a análise de todas as pastas, gerenciando a interface
        do usuário com uma barra de progresso granular.
        """
        texts = TEXTS[self.language]
        logger.info(f"Iniciando varredura na pasta: {self.root_folder}")

        if not self.root_folder.exists() or not self.root_folder.is_dir():
            st.error(f"Pasta '{self.root_folder}' não encontrada ou é inválida.")
            return

        folders_to_process = [f for f in self.root_folder.rglob("*") if f.is_dir() and list(f.glob("*.xlsx"))]

        if not folders_to_process:
            st.warning("Nenhuma subpasta com arquivos Excel (.xlsx) foi encontrada para processar.")
            return

        # FIX: Cálculo do total de itens agora usa as listas de extensões
        total_items = 0
        for folder in folders_to_process:
            total_items += len(list(folder.glob("*.xlsx")))
            if self.enable_images:
                total_items += len(self._find_files(folder, IMAGE_EXTENSIONS))
            if self.enable_videos:
                total_items += len(self._find_files(folder, VIDEO_EXTENSIONS))
            total_items += 1 

        st.info(texts["total_items"].format(total=total_items))
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        processed_items_count = 0

        for folder in folders_to_process:
            result, processed_items_count = self.process_folder(
                folder, progress_bar, status_text, processed_items_count, total_items
            )
            self.results.append(result)

        # Garante que a barra chegue a 100% no final
        progress_bar.progress(1.0)
        status_text.success(texts["analysis_complete"])
        time.sleep(2)
        progress_bar.empty()

        self.report_generator.generate_report(self.results)
        logger.info("✅ Processamento geral concluído.")