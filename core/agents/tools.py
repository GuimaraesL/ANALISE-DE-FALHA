# core/agents/tools.py
"""
Conjunto de ferramentas (Tools) para os agentes da Agno.
Este módulo encapsula os analisadores lineares existentes para que possam
ser chamados autonomamente pelos agentes.
"""
from pathlib import Path
from typing import List, Optional
from core.image_analyzer import ImageAnalyzer
from core.video_analyzer import VideoAnalyzer
from core.database import DatabaseManager

class FailureAnalysisTools:
    """
    Classe que agrupa as ferramentas de análise para os agentes.
    """
    
    def __init__(self, api_key: str, db: DatabaseManager, language: str = "pt"):
        self.api_key = api_key
        self.language = language
        self.db = db
        self.image_analyzer = ImageAnalyzer(api_key)
        self.video_analyzer = VideoAnalyzer(api_key, language=language)

    def analyze_images_tool(self, image_paths: List[str], context: Optional[str] = None) -> str:
        """
        Analisa um conjunto de imagens de falhas.
        
        Args:
            image_paths: Lista de caminhos para os arquivos de imagem.
            context: Contexto adicional fornecido pelo usuário para guiar a análise.
        """
        paths = [Path(p) for p in image_paths]
        # Adaptamos para passar o contexto se disponível
        # No código atual, analyze_images aceita um dicionário de contextos {filename: context}
        contexts = {}
        if context:
            for p in paths:
                contexts[p.name] = context
                
        return self.image_analyzer.analyze_images(paths, media_contexts=contexts)

    def analyze_videos_tool(self, video_paths: List[str], context: Optional[str] = None) -> str:
        """
        Analisa um conjunto de vídeos de falhas.
        
        Args:
            video_paths: Lista de caminhos para os arquivos de vídeo.
            context: Contexto adicional fornecido pelo usuário.
        """
        paths = [Path(p) for p in video_paths]
        contexts = {}
        if context:
            for p in paths:
                contexts[p.name] = context
                
        return self.video_analyzer.analyze_videos(paths, media_contexts=contexts)

    def search_similar_failures(self, area: str = "", equipment: str = "", subgroup: str = "", description_keyword: str = "") -> List[dict]:
        """
        Busca falhas históricas similares e análises anteriores da IA no SQLite.
        
        Args:
            area: Nome da planta/área (ex: LF, CM).
            equipment: Nome do equipamento (ex: CM_2).
            subgroup: Subgrupo ou componente específico.
            description_keyword: Termo técnico para busca na descrição (ex: 'travamento', 'vibração').
        """
        return self.db.search_unified_history(area, equipment, subgroup, description_keyword)
