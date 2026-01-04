# core/prompts.py
import re

def intro(language="pt"):
    if language == "pt":
        return "Você é um especialista em análise de falhas de equipamentos metalúrgicos. Com base nas informações fornecidas, realize uma análise detalhada da falha e forneça uma conclusão final."
    else: # English version
        return "You are an expert in failure analysis of metallurgical equipment. Based on the provided information, perform a detailed failure analysis and provide a final conclusion."

def input_section(excel_data: dict, media_analyses: str, language="pt"):
    """
    Seção de entrada que agora usa a análise bruta das mídias, não o resumo.
    """
    if language == "pt":
        return f"""**Informações Fornecidas:**
- Área: {excel_data.get('area', 'N/A')}
- Equipamento: {excel_data.get('equipment', 'N/A')}
- Subgrupo: {excel_data.get('subgroup', 'N/A')}
- Descrição do Problema: {excel_data.get('description', 'N/A')}
- Análises das Mídias: {media_analyses if media_analyses else 'Nenhuma análise de mídia fornecida.'}
"""
    else:
        return f"""**Provided Information:**
- Area: {excel_data.get('area', 'N/A')}
- Equipment: {excel_data.get('equipment', 'N/A')}
- Subgroup: {excel_data.get('subgroup', 'N/A')}
- Problem Description: {excel_data.get('description', 'N/A')}
- Media Analyses: {media_analyses if media_analyses else 'No media analysis provided.'}
"""

# Funções auxiliares para formatar os dados do JSON
def format_ishikawa(ishikawa_data):
    """Função auxiliar para formatar a seção do Ishikawa."""
    if not ishikawa_data or not isinstance(ishikawa_data, dict):
        return "N/A"
    lines = []
    for category, causes in ishikawa_data.items():
        valid_causes = [str(c).strip() for c in causes if c and str(c).strip()]
        if valid_causes:
            lines.append(f"    - {category}: {', '.join(valid_causes)}")
    return "\n".join(lines) if lines else "No causes registered."

def format_5whys(whys_data):
    """Função auxiliar para formatar a seção dos 5 Porquês."""
    if not whys_data or not isinstance(whys_data, list):
        return "N/A"
    lines = []
    for item in whys_data:
        reasons = [str(p).strip() for p in item.get('Porquês', []) if p and str(p).strip()]
        if reasons:
            cause_effect = item.get('Causa ou Efeito')
            if cause_effect:
                lines.append(f"    - Cause/Effect: {cause_effect}")
            for reason in reasons:
                lines.append(f"      - Why: {reason}")
    return "\n".join(lines) if lines else "No 'why' registered."

def format_list(data_list):
    """Função auxiliar para formatar listas simples, removendo nulos."""
    if not data_list or not isinstance(data_list, list):
        return "N/A"
    valid_items = [str(item).strip() for item in data_list if item and str(item).strip()]
    return ", ".join(valid_items) if valid_items else "No actions registered."


def build_history_refinement_prompt(current_failure_description: str, broad_history: list, language: str = "pt") -> str:
    """
    Cria o prompt para a IA refinar a lista de falhas históricas, agora com todos os detalhes.
    """
    def extract_date(when_value: str) -> str:
        """Extrai a data no formato dd/mm/aaaa de uma string como '14/12/202215:45:14'"""
        match = re.match(r"(\d{2}/\d{2}/\d{4})", when_value)
        return match.group(1) if match else "N/A"

    history_texts = []
    for i, failure in enumerate(broad_history):
        # Usando as chaves EXATAS do arquivo JSON
        description = failure.get("Descrição do Problema", "N/A")
        containment_action = format_list(failure.get("Ação de Contenção"))
        five_whys = format_5whys(failure.get("5 Porquês"))
        root_cause_list = [rc.get('Causa') for rc in failure.get('Causa Raiz', []) if rc.get('Causa')]
        root_cause = ", ".join(root_cause_list) if root_cause_list else "N/A"
        ishikawa = format_ishikawa(failure.get("Ishikawa"))
        action_plan = format_list(failure.get("Plano de Ação"))
        date_failure = extract_date(failure.get("Quando",""))

        # Formatação bilíngue dos dados históricos
        if language == 'pt':
            text = f"""---
     **Falha Histórica {i+1}**
     **Data da Ocorrência:**{date_failure}
      - **Descrição do Problema:** {description}
      - **Ações de Contenção Aplicadas:** {containment_action}
      - **Análise dos 5 Porquês (Resumo):**
     {five_whys}
      - **Diagrama de Ishikawa (Resumo):**
     {ishikawa}
      - **Plano de Ação Definido:** {action_plan}
      - **Causa Raiz Concluída pelos Engenheiros:** {root_cause}
      """
        else:
            text = f"""---
     **Historical Failure {i+1}**
      - **Problem Description:** {description}
      - **Containment Actions Applied:** {containment_action}
      - **5 Whys Analysis (Summary):**
     {five_whys}
      - **Ishikawa Diagram (Summary):**
     {ishikawa}
      - **Defined Action Plan:** {action_plan}
      - **Root Cause Concluded by Engineers:** {root_cause}
      """
        history_texts.append(text)

    formatted_history = "\n".join(history_texts)

    if language == "pt":
        return f"""
    **Tarefa de Análise de Histórico:**

    **Contexto:** Estou analisando a seguinte falha: "{current_failure_description}"

    **Importante:** As falhas históricas a seguir **não são necessariamente idênticas** à falha atual. Seu papel é **identificar correlações técnicas relevantes**, como causas comuns, padrões de falha, modos de desgaste ou ações de manutenção que possam ajudar a compreender melhor o caso atual.
    caso você encontre a mesma falha com descrições identicas, aponte isso, mas não utilize como parte das 3 falhas historicas mais relevantes.

    **Dados Históricos:**  
    {formatted_history}

    ---

    **Sua Tarefa:**
    1. Analise a "Falha Atual".
    2. Compare com cada uma das "Falhas Históricas" detalhadas.
    3. Selecione até **3 falhas históricas mais relevantes**, mesmo que **não sejam iguais**.
    4. Explique por que cada uma é relevante tecnicamente.

    **Formato OBRIGATÓRIO da Resposta:**
    - **Falha Histórica [número]:** [Resumo da falha selecionada]

    - **Relevância:** [Explicação técnica da similaridade/correlação]

    - **Dados Relevantes:** [A falha historica ocorreu na data:{date_failure}]
        [causa raiz]
        [planos de ação]


    """

    else:
        return f"""
    **Historical Analysis Task:**

    **Context:** I am analyzing the following failure:
    - **Current Failure:** "{current_failure_description}"

        Important: The following historical failures are not necessarily identical to the current failure. Their purpose is to identify relevant technical correlations, such as common causes, failure patterns, wear modes, or maintenance actions that may help better understand the current case.
        If you find the same failure with identical descriptions, point it out, but do not include it as one of the three most relevant historical failures.

            **Detailed Historical Data:**  
    {formatted_history}

    ---

    **Your Task:**
    1. Analyze the "Current Failure."
    2. Compare it with each of the detailed "Historical Failures."
    3. Select up to **3 MOST RELEVANT** historical failures, even if **not identical**.
    4. Explain why each one is technically relevant to understand or anticipate the current failure.

     **CRITICAL INSTRUCTION: Despite the historical data being in Portuguese, your entire response, including the analysis and explanations, MUST be in English.**

    **MANDATORY Response Format (use this exact format):**
    - **Historical Failure [No.]:** [Description of the selected historical failure, translated if needed]
      - **Relevance:** [Brief explanation of technical similarity or insight]
    Relevant Data: [The historical failure occurred on: {date_failure}]
         [root cause]
         [action plans]
    """

def history_section(refined_history_text: str, language="pt") -> str:
    """Formata a seção de histórico refinado para o prompt final."""
    if not refined_history_text:
        return ""
        
    if language == "pt":
        header = "\n**Histórico de Falhas Correlacionadas (Análise Semântica):**\n"
        return header + refined_history_text
    else:
        header = "\n**Correlated Failure History (Semantic Analysis):**\n"
        return header + refined_history_text


def task_instructions(language="pt"):

    if language == "pt":
        return """**Tarefa:**
        - **Analise**: Avalie a "Descrição do Problema" e a "Análise Consolidada das Mídias" da falha atual.
        - **Considere o Histórico**: Use o "Histórico de Falhas Correlacionadas", se fornecido, como conhecimento prévio para guiar sua análise.
        - **Analise**: Avalie a "Descrição do Problema" e a "Análise Consolidada das Mídias" da falha atual.
        - **Considere o Histórico**: Use o "Histórico de Falhas Correlacionadas", se fornecido, como conhecimento prévio para guiar sua análise.
        - **Gere os Resultados**:
        1.  **Diagrama de Ishikawa**: Com 2 causas por categoria.
        2.  **5 Porquês**: Para a falha atual.
        3.  **Plano de Ação**: Com 3 ações práticas.
        4.  **Conclusão Final**: Resumindo a causa raiz e as recomendações.
    """
    else: # English version
        return """**Task:**
        - **Analyze**: Evaluate the "Problem Description" and the "Media Analyses" of the current failure.
        - **Consider History**: Use the "Correlated Failure History," if provided, as prior knowledge to guide your analysis. **Note: The historical context may be in Portuguese, but your entire final output must be in English.**
        - **Generate Deliverables**:
          1.  **Ishikawa Diagram**: With 2 causes per category (in English).
          2.  **5 Whys**: For the current failure (in English).
          3.  **Action Plan**: With 3 practical steps (in English).
          4.  **Final Conclusion**: Summarizing the root cause (in English).
        """

def format_spec(language="pt"):
    return (
        """**Formato da Resposta (OBRIGATÓRIO):**
        ```
        **Diagrama de Ishikawa**
        - Material: [causa1, causa2]
        - Máquina: [causa1, causa2]
        - Método: [causa1, causa2]
        - Mão de obra: [causa1, causa2]
        - Meio ambiente: [causa1, causa2]
        - Medição: [causa1, causa2]

        **5 Porquês**
        - Por que ...? ...
        - ...

        **Plano de Ação**
        - ...
        - ...

        **Conclusão Final**
        ```
    """
            if language == "pt" else
            """**Response Format (MANDATORY):**
        ```
        **Ishikawa Diagram**
        - Material: [cause1, cause2]
        - Machine: [cause1, cause2]
        - Method: [cause1, cause2]
        - Manpower: [cause1, cause2]
        - Environment: [cause1, cause2]
        - Measurement: [cause1, cause2]

        **5 Whys**
        - Why ...? ...
        - ...

        **Action Plan**
        - ...
        - ...

        **Final Conclusion**
        ```
        """
    )

def example_response(language="pt"):
    return (
            """<!-- EXEMPLO APENAS PARA REFERÊNCIA - NÃO COPIAR -->
        **Exemplo de Resposta:**
        ```
        **Diagrama de Ishikawa**
        - Material: [Componentes de baixa qualidade, Fios corroídos]
        - Máquina: [Falha no OLM, Degradação do painel]
        - Método: [Manutenção inadequada, Fiação desorganizada]
        - Mão de obra: [Falta de treinamento, Erro operacional]
        - Meio ambiente: [Exposição a poeira, Umidade elevada]
        - Medição: [Falta de sensores, Monitoramento insuficiente]

        **5 Porquês**
        - Por que o painel falhou? Falha na rede do OLM.
        - Por que a rede falhou? Fios danificados.
        - Por que os fios estavam danificados? Manutenção inadequada.
        - Por que a manutenção foi inadequada? Falta de planejamento.
        - Por que não havia planejamento? Equipe não treinada.

        **Plano de Ação**
        - Substituir fios danificados por cabos de alta qualidade.
        - Implementar um programa de manutenção preventiva.
        - Treinar a equipe em fiação e inspeção.

        **Conclusão Final**
        A falha no painel VX01 foi causada por falta de manutenção e treinamento, levando a danos nos fios e falha do OLM. Recomenda-se substituição, manutenção preventiva e treinamento.
        ```
        <!-- FIM DO EXEMPLO -->
    """
        if language == "pt" else
                """<!-- EXAMPLE FOR REFERENCE ONLY - DO NOT COPY -->
        **Example Response:**
        ```
        **Ishikawa Diagram**
        - Material: [Low-quality components, Corroded wires]
        - Machine: [OLM failure, Panel degradation]
        - Method: [Inadequate maintenance, Disorganized wiring]
        - Manpower: [Lack of training, Operational error]
        - Environment: [Dust exposure, High humidity]
        - Measurement: [Lack of sensors, Insufficient monitoring]

        **5 Whys**
        - Why did the panel fail? OLM network failure.
        - Why did the network fail? Damaged wires.
        - Why were the wires damaged? Inadequate maintenance.
        - Why was maintenance inadequate? Lack of planning.
        - Why was there no planning? Untrained staff.

        **Action Plan**
        - Replace damaged wires with high-quality cables.
        - Implement a preventive maintenance program.
        - Train the maintenance team on wiring and inspection.

        **Final Conclusion**
        The failure in the VX01 panel was caused by inadequate maintenance and training, leading to damaged wires and OLM failure. Recommended actions include replacement, preventive maintenance, and training.
        ```
        <!-- END OF EXAMPLE -->
        """
    )

def critical_notes(language="pt"):
    return (
    """ **INSTRUÇÕES CRÍTICAS**:
        - Siga EXATAMENTE o formato acima, usando títulos com asteriscos (**Título**) e marcadores (-).
        - Coloque cada seção entre crases (```) para garantir clareza.
        - Forneça EXATAMENTE duas causas por categoria no Ishikawa, cinco perguntas/respostas no 5 Porquês, e três ações no Plano de Ação.
        - Não mescle, omita ou altere a ordem das seções; cada uma deve ser distinta e completa.
        - Baseie-se estritamente na descrição do problema e nas análises das mídias (imagens e vídeos) fornecidas.
        - Use linguagem técnica e precisa, adequada ao contexto metalúrgico.

        ⚠️ IMPORTANTE: Não copie o exemplo acima. Gere uma nova resposta baseada APENAS nas informações fornecidas neste prompt.
    """
            if language == "pt" else
                """**CRITICAL INSTRUCTIONS**:
        - Follow EXACTLY the format above, using headings with asterisks (**Heading**) and bullet points (-).
        - Enclose each section in triple backticks (```) for clarity.
        - Provide EXACTLY two causes per category in the Ishikawa, five questions/answers in the 5 Whys, and three actions in the Action Plan.
        - Do not merge, omit, or change the order of sections; each must be distinct and complete.
        - Base your analysis strictly on the problem description and media analyses (images and videos).
        - Use precise, technical language suitable for a metallurgical context.

        ⚠️ IMPORTANT: Do not copy the example above. Generate a new response based ONLY on the information provided in this prompt.
        """
    )

def build_video_prompt(filename: str, language: str = "pt", context: str = "") -> str:
    if language == "en":
        prompt = f"""
    You will receive a video file named '{filename}'.

    Carefully analyze the visual content of this video, which shows metallurgical equipment in operation (or failure). Your goal is to extract technical and safety-related insights from the footage.

    Return a concise and professional summary describing:
    - **Visual Evidence of Failure or Risk**: Any leaks, deformations, missing components, improper movements, or exposure to contaminants.
    - **Machine Operation**: Irregular motions, vibrations, abnormal speeds, or noise indicators.
    - **Human Behavior (if applicable)**: Unsafe posture, incorrect interaction with the equipment, exposure to risk.
    - **Environmental Conditions**: Accumulation of dust, liquids, vibrations, lighting, or access hazards.

    ⚠️ Be as objective and engineering-oriented as possible. Do not speculate about causes — focus on what is visible and technically relevant.
    """
    else:
         prompt = f"""
    Você receberá um vídeo chamado '{filename}'.

    Analise cuidadosamente o conteúdo visual do vídeo, que mostra o funcionamento (ou falha) de um equipamento metalúrgico. Seu objetivo é extrair observações técnicas e de segurança com base nas imagens.

    Retorne um resumo profissional e conciso descrevendo:
    - **Evidências Visuais de Falha ou Risco**: Vazamentos, deformações, peças ausentes, movimentações anormais, contaminação visível.
    - **Funcionamento da Máquina**: Vibrações, ruídos, variações de velocidade, movimentos não padronizados.
    - **Comportamento Humano (se houver)**: Postura inadequada, interação incorreta com o equipamento, exposição ao risco.
    - **Condições Ambientais**: Poeira, líquidos, iluminação ruim, vibração excessiva ou riscos de acesso.

    ⚠️ Seja objetivo e técnico. Não especule sobre causas — descreva apenas o que for visivelmente relevante.
    """
    
    if context:
        context_prompt = (
            f"\n\n**CONTEXTO DO USUÁRIO:** O usuário forneceu a seguinte informação adicional sobre este vídeo: \"{context}\". "
            "Use esta informação para guiar sua análise, focando ou confirmando o que foi mencionado se for perceptível no vídeo."
            if language == "pt" else
            f"\n\n**USER CONTEXT:** The user provided the following additional information about this video: \"{context}\". "
            "Use this information to guide your analysis, focusing on or confirming what was mentioned if it is perceptible in the video."
        )
        prompt += context_prompt
        
    return prompt
