# core/agents/analyst_agent.py
"""
Agente Analista de RCA utilizando o framework Agno.
Este agente orquestra a análise de causa raiz de forma autônoma,
utilizando ferramentas especializadas para inspeção visual e consulta histórica.
"""
import logging
import json
import re
from typing import Dict, Any, List, Optional
from agno.agent import Agent
from agno.models.google import Gemini
from core.agents.tools import FailureAnalysisTools
from core.database import DatabaseManager

logger = logging.getLogger(__name__)

from core.prompts import (intro, task_instructions, format_spec, critical_notes)

class LeadAnalysisAgent:
    """
    Agente líder responsável pela orquestração do RCA.
    Utiliza engenharia de prompt avançada sincronizada com a Engine V1.
    """
    
    def __init__(self, api_key: str, history_data: Optional[List[dict]] = None, language: str = "pt"):
        self.api_key = api_key
        self.language = language
        self.db = DatabaseManager()
        self.tools = FailureAnalysisTools(api_key, self.db, language)
        
        # Construção da Persona e Instruções (Sincronizado com V1)
        expert_intro = intro(language)
        expert_tasks = task_instructions(language)
        expert_notes = critical_notes(language)
        
        # Configuração do Agente Agno
        self.agent = Agent(
            name="RCA Expert Agent",
            model=Gemini(id="gemini-2.5-pro", api_key=api_key),
            description=expert_intro,
            instructions=[
                f"Sua missão é atuar como: {expert_intro}",
                "DIRETRIZES DE TRABALHO:",
                expert_tasks,
                "REGRAS DE OURO TÉCNICAS:",
                expert_notes,
                "FLUXO OBRIGATÓRIO:",
                "1. Verifique se há fotos ou vídeos. Se sim, use OBRIGATORIAMENTE as ferramentas analyze_images_tool ou analyze_videos_tool.",
                "2. Use search_similar_failures para embasamento histórico no banco de dados.",
                "3. Sintetize as evidências visuais + histórico + descrição do problema.",
                "4. Gere a Conclusão Final rica em detalhes técnicos (mencione evidências das imagens, ex: cores de oxidação, fraturas, contaminação).",
                "Ao final, inclua OBRIGATORIAMENTE o bloco JSON no formato abaixo:",
                format_spec(language)
            ],
            tools=[
                self.tools.analyze_images_tool,
                self.tools.analyze_videos_tool,
                self.tools.search_similar_failures
            ],
            markdown=True
        )

    def run_analysis(self, excel_data: Dict[str, Any], media_paths: Dict[str, List[str]], context: str = "") -> Dict[str, Any]:
        """
        Executa a análise agêntica completa.
        """
        # Busca exemplos Ouro no banco para Few-Shot
        gold_standards = self.db.get_gold_standards(limit=2)
        gold_context = "\n".join([f"Exemplo Referência:\n{gs['expert_notes']}\nConclusão Esperada: {gs['corrected_conclusion']}" for gs in gold_standards])
        
        # Constrói a mensagem de entrada para o agente
        prompt = f"""
        INFORMAÇÕES DA FALHA ATUAL:
        - Área: {excel_data.get('area')}
        - Equipamento: {excel_data.get('equipment')}
        - Descrição: {excel_data.get('description')}
        
        MÍDIAS DISPONÍVEIS:
        - Fotos: {media_paths.get('images', [])}
        - Vídeos: {media_paths.get('videos', [])}
        
        CONTEXTO ADICIONAL DO USUÁRIO:
        {context}
        
        REFERÊNCIAS TÉCNICAS (GOLD STANDARDS):
        {gold_context}
        
        TAREFA:
        Realize a análise RCA completa. Utilize as ferramentas para olhar as mídias e o histórico.
        Retorne um objeto JSON contendo: 'ishikawa', 'five_whys', 'root_cause' e 'action_plan'.
        """
        
        logger.info("Iniciando análise agêntica via Agno...")
        response = self.agent.run(prompt)
        
        # Tenta extrair conteúdo da resposta de várias formas (Agno RunResponse)
        raw_content = ""
        if hasattr(response, 'content') and response.content:
            raw_content = str(response.content)
        elif hasattr(response, 'content_text') and response.content_text:
            raw_content = str(response.content_text)
        
        # Se ainda vazio, tenta pegar das mensagens
        if not raw_content and hasattr(response, 'messages'):
            for msg in reversed(response.messages):
                if msg.role == "assistant" and msg.content:
                    raw_content = str(msg.content)
                    break

        default_ishikawa = {
            "causes": {
                "Material": [], 
                "Máquina" if self.language == "pt" else "Machine": [],
                "Método" if self.language == "pt" else "Method": [],
                "Mão de obra" if self.language == "pt" else "Manpower": [],
                "Meio ambiente" if self.language == "pt" else "Environment": [],
                "Medição" if self.language == "pt" else "Measurement": []
            }
        }
        
        ai_results = {
            "raw_response": raw_content,
            "ishikawa": default_ishikawa,
            "five_whys": [],
            "root_cause": "",
            "action_plan": []
        }
        
        try:
            # Busca por blocos de código JSON ou string JSON direta
            json_match = re.search(r'```json\s*(.*?)\s*```', raw_content or "", re.DOTALL)
            json_str = json_match.group(1) if json_match else (raw_content or "")
            
            # Limpeza básica se não for bloco de código e tiver conteúdo
            if not json_match and json_str.strip():
                clean_match = re.search(r'(\{.*\})', json_str, re.DOTALL)
                if clean_match:
                    json_str = clean_match.group(1)
                
            json_str = json_str.strip()
            parsed_json = json.loads(json_str) if json_str.startswith("{") else {}
                
            # Se extraído com sucesso, removemos o JSON do raw_response para não poluir a visualização textual
            if json_match:
                # Remove o bloco JSON do conteúdo textual
                clean_text = raw_content.replace(json_match.group(0), "").strip()
                ai_results["raw_response"] = clean_text
            elif json_str.startswith("{") and "}" in json_str:
                # Caso a IA tenha retornado apenas JSON ou JSON limpo
                # Mantemos o original se houver texto antes
                pass

            # Mapeia campos do JSON para a estrutura esperada pela UI com fallbacks individuais
            if parsed_json.get("ishikawa"):
                ai_results["ishikawa"] = parsed_json["ishikawa"]
                
            if parsed_json.get("five_whys"):
                ai_results["five_whys"] = parsed_json["five_whys"]
                
            ai_results["root_cause"] = parsed_json.get("root_cause", "")
            ai_results["action_plan"] = parsed_json.get("action_plan", [])
            
            logger.info("JSON extraído e parseado com sucesso da resposta agêntica.")
        except Exception as e:
            logger.warning(f"Não foi possível parsear JSON da resposta do agente: {e}. Usando fallback de texto bruto.")

        return {
            "ai_results": ai_results,
            "engine": "V2 (Agêntico)"
        }
