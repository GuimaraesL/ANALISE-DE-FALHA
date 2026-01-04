# 📝 Guia de Engenharia de Prompts

> Documentação técnica sobre a construção de prompts no sistema ANALISE-DE-FALHA.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura do Prompt Final](#estrutura-do-prompt-final)
3. [Funções de Construção](#funções-de-construção)
4. [Prompt de Refinamento de Histórico](#prompt-de-refinamento-de-histórico)
5. [Prompt de Análise de Vídeo](#prompt-de-análise-de-vídeo)
6. [Boas Práticas](#boas-práticas)

---

## Visão Geral

O arquivo `core/prompts.py` é o coração da engenharia de prompts do sistema. Ele contém:

- **~380 linhas** de código
- **15 funções** especializadas
- Suporte bilíngue (**PT/EN**)
- Exemplos few-shot para melhorar a qualidade das respostas

### Filosofia de Design

1. **Modularidade**: Cada seção do prompt é uma função separada
2. **Flexibilidade de Idioma**: Todas as funções aceitam `language` como parâmetro
3. **Exemplos Claros**: Uso extensivo de few-shot learning
4. **Formato Estruturado**: Output esperado em JSON parseável

---

## Estrutura do Prompt Final

O prompt final enviado ao Gemini Pro segue esta estrutura:

```
┌────────────────────────────────────────────────────────────────┐
│ 1. INTRO                                                        │
│    Função: intro(language)                                      │
│    Conteúdo:                                                    │
│    - Define a persona (especialista em RCA)                     │
│    - Estabelece o contexto industrial                           │
│    - Define o tom técnico esperado                              │
├────────────────────────────────────────────────────────────────┤
│ 2. INPUT_SECTION                                                │
│    Função: input_section(excel_data, media_analyses, language)  │
│    Conteúdo:                                                    │
│    - Dados extraídos do Excel (Área, Equipamento, etc.)         │
│    - Análises de imagens (laudo técnico visual)                 │
│    - Análises de vídeos (observações de movimento)              │
├────────────────────────────────────────────────────────────────┤
│ 3. HISTORY_SECTION                                              │
│    Função: history_section(refined_history, language)           │
│    Conteúdo:                                                    │
│    - Top 3 falhas históricas relevantes (do RAG)                │
│    - Contexto de como usar o histórico na análise               │
├────────────────────────────────────────────────────────────────┤
│ 4. TASK_INSTRUCTIONS                                            │
│    Função: task_instructions(language)                          │
│    Conteúdo:                                                    │
│    - O que a IA deve gerar (Ishikawa, 5 Porquês, etc.)          │
│    - Regras de quantidade (2 causas por M, 5 porquês, etc.)     │
├────────────────────────────────────────────────────────────────┤
│ 5. FORMAT_SPEC                                                  │
│    Função: format_spec(language)                                │
│    Conteúdo:                                                    │
│    - Schema exato do JSON esperado                              │
│    - Nomes das chaves e estrutura                               │
├────────────────────────────────────────────────────────────────┤
│ 6. EXAMPLE_RESPONSE                                             │
│    Função: example_response(language)                           │
│    Conteúdo:                                                    │
│    - Exemplo completo de resposta                               │
│    - Few-shot learning para melhor qualidade                    │
├────────────────────────────────────────────────────────────────┤
│ 7. CRITICAL_NOTES                                               │
│    Função: critical_notes(language)                             │
│    Conteúdo:                                                    │
│    - Regras absolutas (NUNCA fazer X, SEMPRE fazer Y)           │
│    - Lembretes de formato                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Funções de Construção

### intro(language)

Define a persona e contexto:

```python
def intro(language="pt"):
    if language == "pt":
        return """
        Você é um engenheiro especialista em análise de causa raiz (RCA) 
        em ambiente industrial metalúrgico...
        """
```

### input_section(excel_data, media_analyses, language)

Formata os dados de entrada:

```python
def input_section(excel_data: dict, media_analyses: str, language="pt"):
    # Extrai dados do Excel
    area = excel_data.get('area', 'N/A')
    equipment = excel_data.get('equipment', 'N/A')
    # ...
    
    return f"""
    ## Dados da Ocorrência
    - **Área**: {area}
    - **Equipamento**: {equipment}
    - **Descrição**: {description}
    
    ## Análise de Mídias
    {media_analyses}
    """
```

### format_spec(language)

Define o schema JSON esperado:

```python
def format_spec(language="pt"):
    return """
    ## Formato de Saída Esperado
    
    **Diagrama de Ishikawa**
    - Material: [causa1, causa2]
    - Máquina: [causa1, causa2]
    - Método: [causa1, causa2]
    - Mão de obra: [causa1, causa2]
    - Meio ambiente: [causa1, causa2]
    - Medição: [causa1, causa2]
    
    **5 Porquês**
    - Por que 1: Resposta
    - Por que 2: Resposta
    ...
    
    **Plano de Ação**
    - Ação 1
    - Ação 2
    - Ação 3
    
    **Conclusão Final**
    Texto conclusivo...
    """
```

---

## Prompt de Refinamento de Histórico

A função `build_history_refinement_prompt` é usada no RAG Estágio 2:

```python
def build_history_refinement_prompt(
    current_failure_description: str, 
    broad_history: list, 
    language: str = "pt"
) -> str:
    """
    Cria o prompt para a IA refinar a lista de falhas históricas.
    
    Args:
        current_failure_description: Descrição da falha atual
        broad_history: Lista de falhas do RAG Estágio 1
        language: Idioma ('pt' ou 'en')
    
    Returns:
        Prompt formatado para refinamento semântico
    """
```

### Estrutura do Prompt de Refinamento

```
┌────────────────────────────────────────────┐
│ CONTEXTO                                    │
│ - Falha atual (descrição, área, equip.)    │
├────────────────────────────────────────────┤
│ CANDIDATOS                                  │
│ - Lista de falhas do RAG Estágio 1         │
│ - Cada uma com: data, descrição, causa     │
├────────────────────────────────────────────┤
│ INSTRUÇÃO                                   │
│ - Selecionar as 3 mais relevantes          │
│ - Justificar a escolha                     │
│ - Formato de saída                         │
└────────────────────────────────────────────┘
```

---

## Prompt de Análise de Vídeo

A função `build_video_prompt` gera prompts para análise de vídeos:

```python
def build_video_prompt(filename: str, language: str = "pt") -> str:
    """
    Gera prompt para análise técnica de vídeo industrial.
    
    Args:
        filename: Nome do arquivo de vídeo
        language: Idioma ('pt' ou 'en')
    
    Returns:
        Prompt formatado para análise de vídeo
    """
```

### Foco da Análise de Vídeo

- **Movimento**: Vibrações anormais, oscilações
- **Padrões**: Ciclos, intervalos, repetições
- **Anomalias**: Ruídos, faíscas, vazamentos
- **Condições**: Estado geral do equipamento

---

## Boas Práticas

### 1. Mantenha os Prompts Modulares

Cada função deve ter uma responsabilidade única:

```python
# ✅ BOM - Funções pequenas e focadas
def intro(language):
    ...

def input_section(data, media, language):
    ...

# ❌ RUIM - Função gigante que faz tudo
def build_everything(all_params):
    ...
```

### 2. Use Exemplos (Few-Shot Learning)

Sempre forneça um exemplo completo do output esperado:

```python
def example_response(language):
    return """
    **Diagrama de Ishikawa**
    - Material: Fadiga do material, Corrosão interna
    - Máquina: Desgaste do rolamento, Falta de lubrificação
    ...
    """
```

### 3. Seja Específico nas Instruções

Evite instruções vagas:

```python
# ❌ RUIM
"Faça uma análise"

# ✅ BOM
"Gere exatamente 2 causas para cada categoria do Ishikawa"
"Liste exatamente 5 perguntas 'Por quê?' com suas respostas"
```

### 4. Teste Bilíngue

Sempre implemente ambos os idiomas:

```python
def funcao(language="pt"):
    if language == "pt":
        return "Texto em português"
    else:
        return "Text in English"
```

### 5. Limite o Tamanho do Contexto

Mantenha o prompt abaixo de 30.000 tokens para otimizar custo:

```python
# Em ai_processor.py
if estimate_tokens(prompt) > 30000:
    logging.warning("Prompt muito grande, considere reduzir mídias")
```

---

## Métricas de Tokens

### Distribuição Típica de Tokens

| Seção | Tokens Médios |
|-------|---------------|
| Intro | ~300 |
| Input Section | ~500-2000 |
| History Section | ~1000-3000 |
| Task Instructions | ~500 |
| Format Spec | ~300 |
| Example Response | ~800 |
| Critical Notes | ~200 |
| **Total Base** | **~3000-7000** |

### Variáveis que Aumentam Tokens

- **Análise de Imagens**: +200-500 por imagem
- **Análise de Vídeo**: +300-800 por vídeo
- **Histórico Refinado**: +500-1500 (depende da riqueza)

---

*Documentação gerada automaticamente em Janeiro 2026*
