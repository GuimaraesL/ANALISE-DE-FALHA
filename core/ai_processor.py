# core/ai_processor.py
import google.generativeai as genai
from core.prompts import (intro, input_section, history_section, 
                          task_instructions, format_spec, example_response, 
                          critical_notes, build_history_refinement_prompt)
from typing import Dict, List
import re
import logging


# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def estimate_tokens(text: str) -> int:
    return len(text) // 4  # Estimativa conservadora de tokens

class AIProcessor:
    def __init__(self, api_key: str, language: str = "pt"):
        """Inicializa a API do Gemini."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")
        # Usamos o Flash para a tarefa de refinamento por ser mais rápido e barato
        self.refinement_model = genai.GenerativeModel("gemini-2.5-flash")
        # Usamos o Pro para a análise final por ser mais robusto
        self.analysis_model = genai.GenerativeModel("gemini-2.5-pro")
        self.cache = {}
        self.language = language
        self.last_prompt = ""
        self.last_prompt_token_count = 0

    def refine_history_with_ai(self, current_failure_description: str, broad_history: List[dict]) -> tuple[str, dict]:
        """Usa a IA para analisar uma lista de falhas e retornar as mais relevantes."""
        if not broad_history:
            return "", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

        refinement_prompt = build_history_refinement_prompt(
            current_failure_description, broad_history, self.language
        )

        try:
            input_token_info = self.refinement_model.count_tokens(refinement_prompt)
            input_tokens = input_token_info.total_tokens

            response = self.refinement_model.generate_content(refinement_prompt)
            refined_text = response.text.strip()

            output_token_info = self.refinement_model.count_tokens(refined_text)
            output_tokens = output_token_info.total_tokens

            total_tokens = input_tokens + output_tokens

            logging.info(f"Histórico refinado pela IA:\n{refined_text}")
            return refined_text, {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

        except Exception as e:
            logging.error(f"Erro ao refinar histórico com IA: {e}")
            return "Não foi possível refinar o histórico de falhas.", {
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0
            }


    def build_prompt(self, excel_data, media_analyses, refined_history):
        history_context = history_section(refined_history, self.language)
        parts = [
            intro(self.language),
            input_section(excel_data, media_analyses, self.language),
            history_context,
            task_instructions(self.language),
            format_spec(self.language),
            example_response(self.language),
            critical_notes(self.language)
        ]
        full_prompt = "\n\n".join(filter(None, parts))
        self.last_prompt = full_prompt
        self.last_prompt_token_count = estimate_tokens(full_prompt)
        return full_prompt

    def get_last_token_count(self):
        return getattr(self, "last_prompt_token_count", 0)

    def process_with_gemini(self, prompt: str) -> Dict:
        if prompt in self.cache:
            logger.info("Retornando resultado do cache")
            return self.cache[prompt]

        try:
            response = self.model.generate_content(prompt)
            output_text = response.text.strip() if response.text else ""
            output_tokens = self.model.count_tokens(output_text).total_tokens
            input_tokens = self.model.count_tokens(prompt).total_tokens
            total_tokens = input_tokens + output_tokens

            response_text = response.text.strip() if response.text else ""
            logger.info(f"Resposta bruta do Gemini:\n{response_text}")

            ishikawa = {"causes": {
                "Material": [], "Máquina" if self.language == "pt" else "Machine": [],
                "Método" if self.language == "pt" else "Method": [],
                "Mão de obra" if self.language == "pt" else "Manpower": [],
                "Meio ambiente" if self.language == "pt" else "Environment": [],
                "Medição" if self.language == "pt" else "Measurement": []
            }}
            five_whys = []
            action_plan = []
            conclusion = ""

            cleaned_response = re.sub(r"```.*?```", lambda m: m.group(0).replace("```", ""), response_text, flags=re.DOTALL)
            sections = re.split(r"\*\*(.*?)\*\*\n", cleaned_response, flags=re.MULTILINE)
            sections = [s.strip() for s in sections if s.strip()]
            current_section = None

            for i in range(0, len(sections), 2):
                if i + 1 >= len(sections):
                    break
                title = sections[i].strip().lower()
                content = sections[i + 1].strip()

                if "ishikawa" in title:
                    current_section = "ishikawa"
                    lines = content.split("\n")
                    for line in lines:
                        match = re.match(r"-\s*([^:]+):\s*(.*)", line.strip())
                        if match:
                            category, causes = match.groups()
                            category = category.strip()
                            if category in ishikawa["causes"]:
                                causes_list = [c.strip() for c in causes.split(",") if c.strip()]
                                ishikawa["causes"][category] = causes_list[:2]
                                if len(causes_list) < 2:
                                    logger.warning(f"Categoria {category} tem menos de 2 causas: {causes_list}")
                elif "5 porquês" in title.lower() or "5 whys" in title.lower():
                    current_section = "five_whys"
                    lines = content.split("\n")
                    for line in lines:
                        match = re.match(r"^- (Por que.*?|Why.*?)\?\s*(.*)", line.strip())
                        if match:
                            pergunta, resposta = match.groups()
                            five_whys.append(f"{pergunta.strip()}? {resposta.strip()}")

                    five_whys = five_whys[:5]
                    if len(five_whys) < 5:
                        logger.warning(f"5 Porquês tem menos de 5 entradas: {five_whys}")
                elif "plano de ação" in title.lower() or "action plan" in title.lower():
                    current_section = "action_plan"
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("-"):
                            action_plan.append(line.lstrip("- ").strip())
                    action_plan = action_plan[:3]
                    if len(action_plan) < 3:
                        logger.warning(f"Plano de Ação tem menos de 3 ações: {action_plan}")
                elif "conclusão final" in title.lower() or "final conclusion" in title.lower():
                    current_section = "conclusion"
                    conclusion = content.strip()

            if not any(ishikawa["causes"].values()) or not five_whys or not action_plan or not conclusion:
                logger.warning("Seções incompletas. Aplicando fallback baseado no prompt.")
                prompt_lines = prompt.split("\n")
                description = next((line for line in prompt_lines if "Descrição do problema" in line or "Problem description" in line), "N/A")
                description = description.split(":")[-1].strip() if ":" in description else "N/A"

                if not any(ishikawa["causes"].values()):
                    default_causes = {
                        "Material": ["Material de baixa qualidade", "Corrosão detectada"],
                        "Máquina" if self.language == "pt" else "Machine": ["Falha mecânica", "Desgaste excessivo"],
                        "Método" if self.language == "pt" else "Method": ["Procedimento inadequado", "Falta de inspeção"],
                        "Mão de obra" if self.language == "pt" else "Manpower": ["Erro humano", "Falta de treinamento"],
                        "Meio ambiente" if self.language == "pt" else "Environment": ["Condições adversas", "Exposição a umidade"],
                        "Medição" if self.language == "pt" else "Measurement": ["Falta de monitoramento", "Sensores imprecisos"]
                    }
                    for category in ishikawa["causes"]:
                        ishikawa["causes"][category] = [f"{cause} ({description})" for cause in default_causes[category]][:2]

                if len(five_whys) < 5:
                    five_whys = [
                        f"Por que ocorreu a falha? {description}." if self.language == "pt" else f"Why did the failure occur? {description}.",
                        f"Por que {description}? Condição não identificada." if self.language == "pt" else f"Why {description}? Condition not identified.",
                        "Por que não identificada? Inspeção insuficiente." if self.language == "pt" else "Why not identified? Insufficient inspection.",
                        "Por que inspeção insuficiente? Falta de procedimento." if self.language == "pt" else "Why insufficient inspection? Lack of procedure.",
                        "Por que falta de procedimento? Treinamento inadequado." if self.language == "pt" else "Why lack of procedure? Inadequate training."
                    ][:5]

                if len(action_plan) < 3:
                    action_plan = [
                        "Revisar e substituir componentes defeituosos." if self.language == "pt" else "Review and replace defective components.",
                        "Implementar inspeções regulares." if self.language == "pt" else "Implement regular inspections.",
                        "Treinar a equipe em procedimentos de manutenção." if self.language == "pt" else "Train the team on maintenance procedures."
                    ][:3]

                if not conclusion:
                    conclusion = (
                        f"A falha foi causada por {description.lower()}. Recomenda-se revisar componentes e treinar a equipe."
                        if self.language == "pt" else
                        f"The failure was caused by {description.lower()}. It is recommended to review components and train the team."
                    )

  
            input_tokens = self.get_last_token_count()
            output_tokens = self.model.count_tokens(output_text).total_tokens
            total_tokens = input_tokens + output_tokens

            result = {
                "raw_response": response_text,
                "ishikawa": ishikawa,
                "five_whys": five_whys,
                "action_plan": action_plan,
                "conclusion": conclusion,
                "token_details": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens
                }
            }
         

            self.cache[prompt] = result
            logger.info(f"Resultado parseado: {result}")
            return result

        except Exception as e:
            logger.error(f"Erro ao chamar Gemini API: {str(e)}")
            return {"error": f"Erro ao chamar Gemini API: {str(e)}"}
