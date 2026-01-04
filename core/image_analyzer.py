# core/image_analyzer.py
"""
Módulo responsável pela análise de imagens usando IA.

Este módulo contém a classe ImageAnalyzer que utiliza o Google Gemini 2.5 Flash
para analisar imagens de equipamentos industriais e gerar descrições técnicas
de sinais de falha visíveis (rachaduras, corrosão, desgaste, etc.).

Formatos suportados: JPEG, PNG, WebP, GIF, HEIC, HEIF, BMP, TIFF, PDF.
"""
import google.generativeai as genai
from pathlib import Path
from typing import List
import logging

class ImageAnalyzer:
    def __init__(self, api_key: str, language: str = "pt"):
        """Inicializa a API do Gemini para análise de imagens."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.language = language

    def analyze_image(self, image_path: Path, context: str = "") -> str:
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            # FIX: Mapeamento expandido para novos tipos de imagem
            ext = image_path.suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".gif": "image/gif",
                ".heic": "image/heic",
                ".heif": "image/heif",
                ".bmp": "image/bmp",
                ".tiff": "image/tiff",
                ".pdf": "image/pdf"
            }
            
            mime_type = mime_map.get(ext)
            if not mime_type:
                logging.warning(f"Formato de imagem não suportado: {ext}")
                return f"**Erro em {image_path.name}**: Formato de imagem não suportado: {ext}"


            prompt = """
                Sua tarefa é atuar como um especialista em engenharia de falhas. Analise a imagem fornecida de um equipamento metalúrgico e retorne uma descrição **técnica, objetiva e concisa** dos sinais de falha visíveis.

                **Concentre-se principalmente no que pode ser observado diretamente na imagem, mas considere inferências técnicas plausíveis com base visual (ex: ausência de lubrificação visível, acúmulo excessivo de partículas metálicas, dano térmico aparente).**

                Descreva os seguintes pontos, se aplicável:
                - **Danos Visíveis**: Rachaduras, corrosão, desgaste, fraturas, descoloração, partículas metálicas, ausência de lubrificante.
                - **Localização**: Onde estão os danos (ex: rolamento, pista, parafuso, fenda).
                - **Características**: Profundidade, padrão, coloração, quantidade.

                **Instruções Importantes:**
                - **NÃO** inclua “Visão geral do equipamento”.
                - **Evite suposições vagas**, mas **pode inferir** com base em evidência visual concreta.
                - O objetivo é gerar um parecer técnico de campo.
            """ if self.language == "pt" else """
                Your task is to act as a failure analysis expert. Analyze the provided image of metallurgical equipment and return a **technical, objective, and concise** description of visible failure signs.

                **Focus primarily on what can be directly observed in the image, but consider technically plausible inferences based on visual evidence (e.g., lack of visible lubrication, excessive metal particles, apparent thermal damage).**

                Describe the following points, if applicable:
                - **Visible Damage**: Cracks, corrosion, wear, fractures, discoloration, metal particles, lack of lubricant.
                - **Location**: Where the damage is located (e.g., bearing, raceway, bolt, gap).
                - **Characteristics**: Depth, pattern, color, quantity.

                **Important Instructions:**
                - **DO NOT** include general equipment overviews.
                - **Avoid vague assumptions**, but **you may infer** based on strong visual cues.
                - The goal is to generate a technical field-style observation report.
            """

            if context:
                context_prompt = (
                    f"\n\n**CONTEXTO DO USUÁRIO:** O usuário forneceu a seguinte informação adicional sobre esta imagem: \"{context}\". "
                    "Use esta informação para guiar sua análise, confirmando ou analisando especificamente o que foi mencionado se for visível."
                    if self.language == "pt" else
                    f"\n\n**USER CONTEXT:** The user provided the following additional information about this image: \"{context}\". "
                    "Use this information to guide your analysis, confirming or specifically analyzing what was mentioned if it is visible."
                )
                prompt += context_prompt
            response = self.model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_data} # Usa a variável mime_type
            ])

            analysis = response.text.strip() if response.text else (
                "Nenhuma análise gerada" if self.language == "pt" else "No analysis generated"
            )

            # Prefixa o nome da imagem com separação clara
            return f"📷 **{image_path.name}**\n\n{analysis}"

        except Exception as e:
            return f"📷 **{image_path.name}**\n\nErro ao analisar imagem: {str(e)}"

    def analyze_images(self, image_paths: List[Path], enable_images: bool = True, contexts: dict = None) -> str:
        if not enable_images:
            return "Análise de imagens desabilitada" if self.language == "pt" else "Image analysis disabled"

        contexts = contexts or {}
        results = [self.analyze_image(img, contexts.get(img.name, "")) for img in image_paths]
        return "\n\n---\n\n".join(results) if results else (
            "Nenhuma imagem processada" if self.language == "pt" else "No images processed"
        )
