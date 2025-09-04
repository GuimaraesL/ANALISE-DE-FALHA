# core/video_analyzer.py
from pathlib import Path
from typing import List
import time
import google.generativeai as genai # Usando a biblioteca padrão do Gemini
from core.prompts import build_video_prompt
from ui.texts import TEXTS
import logging

# Carrega a configuração para obter a chave da API
from core.config_loader import load_config
config = load_config()

# Configura a API do Gemini. 
# Isso garante que estamos usando a mesma autenticação dos outros módulos.
gemini_api_key = config.get("gemini_api_key")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    logging.error("Chave da API do Gemini não encontrada no config.json.")


class VideoAnalyzer:
    def __init__(self, api_key: str, language: str = "pt"):
        """
        Inicializa o analisador de vídeo usando o modelo multimodal padrão do Gemini.
        A 'api_key' do __init__ não é mais necessária aqui, mas mantemos para consistência.
        """
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")
        self.language = language

    def analyze_video(self, video_path: Path) -> str:
        """
        Analisa um único arquivo de vídeo usando a API do Gemini.
        Este método agora faz o upload do arquivo primeiro, que é a prática recomendada.
        """
        try:
            logging.info(f"Iniciando upload do vídeo: {video_path.name}")
            # Faz o upload do arquivo para a API do Gemini. Isso é mais robusto para vídeos.
            video_file = genai.upload_file(path=str(video_path))
            logging.info(f"Upload do vídeo '{video_path.name}' concluído. Estado: {video_file.state}")

            # Espera o vídeo ser processado pela API
            while video_file.state.name == "PROCESSING":
                time.sleep(5) # Espera 5 segundos
                video_file = genai.get_file(video_file.name)
                logging.info(f"Aguardando processamento do vídeo '{video_path.name}'. Estado: {video_file.state}")

            if video_file.state.name == "FAILED":
                raise ValueError(f"Processamento do arquivo de vídeo falhou: {video_file.name}")

            # Gera o conteúdo usando o arquivo processado e o prompt
            prompt = build_video_prompt(video_path.name, self.language)
            response = self.model.generate_content([prompt, video_file])
            
            # Limpa o arquivo da API após o uso para não acumular dados
            genai.delete_file(video_file.name)
            logging.info(f"Arquivo de vídeo '{video_file.name}' deletado da API após análise.")

            return f"📹 **{video_path.name}**\n\n{response.text}"

        except Exception as e:
            error_message = f"Erro ao analisar vídeo com a API Gemini: {str(e)}"
            logging.error(error_message)
            return f"📹 **{video_path.name}**\n\n{error_message}"

    def analyze_videos(self, video_paths: List[Path]) -> str:
        """Analisa uma lista de caminhos de vídeo."""
        if not video_paths:
            lang_texts = TEXTS.get(self.language, TEXTS.get('en', {}))
            return lang_texts.get("no_video_found", "No videos found")
            
        results = [self.analyze_video(path) for path in video_paths]
        return "\n\n---\n\n".join(results)
