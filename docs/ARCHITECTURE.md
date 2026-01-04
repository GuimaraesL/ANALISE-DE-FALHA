# 🏛️ Arquitetura do Sistema ANALISE-DE-FALHA

> Documentação técnica detalhada da arquitetura interna do sistema de Análise de Causa Raiz.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Componentes Principais](#componentes-principais)
3. [Fluxo de Dados Detalhado](#fluxo-de-dados-detalhado)
4. [Sistema RAG de 2 Estágios](#sistema-rag-de-2-estágios)
5. [Engenharia de Prompts](#engenharia-de-prompts)
6. [Estratégia de Logging](#estratégia-de-logging)
7. [Padrões de Código](#padrões-de-código)

---

## Visão Geral

O sistema **ANALISE-DE-FALHA** é uma aplicação de análise automatizada que combina:

- **Processamento Multimodal**: Excel, imagens e vídeos
- **RAG (Retrieval-Augmented Generation)**: Contexto histórico enriquecido
- **IA Generativa**: Google Gemini 2.5 para análise e geração de relatórios
- **UI Premium**: Interface Streamlit com componentes estilizados

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE APRESENTAÇÃO                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │    app.py       │  │ test_ui_preview │  │    styles.css       │  │
│  │  (Streamlit)    │  │   (Mock Data)   │  │  (CSS Premium)      │  │
│  └────────┬────────┘  └─────────────────┘  └─────────────────────┘  │
│           │                                                          │
├───────────┼──────────────────────────────────────────────────────────┤
│           ▼                 CAMADA DE ORQUESTRAÇÃO                   │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                  FailureAnalysisApp                             │ │
│  │  • Descoberta de arquivos (Excel, imagens, vídeos)              │ │
│  │  • Coordenação de fluxo                                         │ │
│  │  • Barra de progresso                                           │ │
│  └─────────────────────────┬───────────────────────────────────────┘ │
│                            │                                         │
├────────────────────────────┼─────────────────────────────────────────┤
│           CAMADA DE SERVIÇOS (core/)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ExcelReader  │  │ImageAnalyzer│  │VideoAnalyzer│  │HistoryMgr  │ │
│  │ (Openpyxl)  │  │(Gemini Flash)│  │(Gemini Flash)│  │(RAG Stage1)│ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │                │         │
│         └────────────────┼────────────────┼────────────────┘         │
│                          ▼                ▼                          │
│              ┌─────────────────────────────────────┐                 │
│              │          AIProcessor                │                 │
│              │  • Montagem de prompt (prompts.py)  │                 │
│              │  • RAG Estágio 2 (refinamento)      │                 │
│              │  • Chamada Gemini 2.5 Pro           │                 │
│              │  • Parsing de resposta JSON         │                 │
│              └─────────────────────────────────────┘                 │
│                          │                                           │
│                          ▼                                           │
│              ┌─────────────────────────────────────┐                 │
│              │       ReportGenerator               │                 │
│              │  • Formatação Markdown              │                 │
│              │  • Salvamento em relatorios/        │                 │
│              └─────────────────────────────────────┘                 │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                         CAMADA DE DADOS                              │
│  ┌─────────────┐  ┌─────────────────────┐  ┌──────────────────────┐ │
│  │config.json  │  │ extracted_data.json │  │   texts.py (i18n)    │ │
│  │ (API Keys)  │  │ (Histórico 12MB)    │  │   (PT/EN)            │ │
│  └─────────────┘  └─────────────────────┘  └──────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Componentes Principais

### 1. FailureAnalysisApp (`core/failure_analysis_app.py`)

**Responsabilidade**: Orquestrador principal do pipeline de análise.

```python
class FailureAnalysisApp:
    def __init__(self, root_folder, gemini_api_key, enable_images, enable_videos, language):
        # Inicializa todas as dependências (ExcelReader, ImageAnalyzer, etc.)
    
    def process_folder(self, folder_path, progress_bar, status_text, ...):
        # Processa uma única pasta e atualiza UI em tempo real
    
    def run(self):
        # Itera todas as pastas, gerencia barra de progresso
```

**Fluxo interno**:
1. Descobre pastas no `root_folder`
2. Para cada pasta:
   - Localiza arquivo `.xlsx`
   - Localiza imagens e vídeos
   - Chama serviços de análise
   - Atualiza progresso

### 2. AIProcessor (`core/ai_processor.py`)

**Responsabilidade**: Construção de prompts e comunicação com Gemini.

**Modelos utilizados**:
| Método | Modelo | Uso |
|--------|--------|-----|
| `refine_history_with_ai()` | Gemini 2.5 Flash | RAG Estágio 2 |
| `process_with_gemini()` | Gemini 2.5 Pro | Análise RCA final |

**Parsing de resposta**:
```python
# A resposta JSON esperada da IA:
{
    "ishikawa": {
        "causes": {
            "Material": [...],
            "Máquina": [...],
            "Método": [...],
            "Mão de obra": [...],
            "Meio ambiente": [...],
            "Medição": [...]
        }
    },
    "five_whys": ["Por que...?: Porque...", ...],
    "action_plan": ["Ação 1", "Ação 2", ...],
    "conclusion": "Conclusão final..."
}
```

### 3. HistoryManager (`core/history_manager.py`)

**Responsabilidade**: RAG Estágio 1 - Filtro estruturado no histórico.

**Algoritmo**:
1. Normaliza texto (remove acentos, lowercase)
2. Filtra por: Área + Equipamento + Subgrupo
3. Retorna lista de falhas candidatas

```python
def find_related_failures(self, current_failure_data: dict) -> list:
    # Normalização:
    area_atual = self._normalize_text(data.get('area'))
    
    # Filtro:
    for entry in self.history_data:
        if (area_hist == area_atual and
            equip_hist == equip_atual and
            subgrupo_hist == subgrupo_atual):
            related_failures.append(entry)
```

### 4. ImageAnalyzer / VideoAnalyzer

**Responsabilidade**: Análise visual de mídias com descrição técnica.

**Prompt especializado**:
- Foco em sinais de falha (rachaduras, corrosão, desgaste)
- Linguagem técnica de engenharia
- Sem suposições vagas, apenas evidências visuais

---

## Fluxo de Dados Detalhado

### Sequência de Execução

```
[Usuário seleciona pasta]
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 1. COLETA DE ARQUIVOS                               │
│    FailureAnalysisApp._find_files()                 │
│    - Busca *.xlsx                                   │
│    - Busca *.jpg, *.png, *.webp, etc.              │
│    - Busca *.mp4, *.mov, *.avi, etc.              │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 2. EXTRAÇÃO EXCEL                                   │
│    ExcelReader.read_excel()                         │
│    - Lê aba "A3 Time de Resolução de Prob"         │
│    - Extrai: Área (E16), Equipamento (E17),        │
│      Subgrupo (E18), Descrição (B20)               │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 3. ANÁLISE DE MÍDIAS (Paralelo)                    │
│    ImageAnalyzer.analyze_images()                   │
│    VideoAnalyzer.analyze_videos()                   │
│    - Modelo: Gemini 2.5 Flash                       │
│    - Output: Descrição técnica das observações      │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 4. RAG ESTÁGIO 1 - FILTRO                          │
│    HistoryManager.find_related_failures()           │
│    - Input: Excel data                              │
│    - Filter: Área + Equipamento + Subgrupo          │
│    - Output: Lista ampla de falhas similares        │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 5. RAG ESTÁGIO 2 - REFINAMENTO                     │
│    AIProcessor.refine_history_with_ai()             │
│    - Input: Falha atual + Lista do Estágio 1        │
│    - Modelo: Gemini 2.5 Flash                       │
│    - Output: Top 3 casos mais relevantes            │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 6. ANÁLISE RCA FINAL                               │
│    AIProcessor.process_with_gemini()                │
│    - Input: Excel + Mídias + Histórico refinado     │
│    - Modelo: Gemini 2.5 Pro                         │
│    - Output: Ishikawa + 5 Porquês + Plano + Concl.  │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 7. RENDERIZAÇÃO UI                                  │
│    app.py (Streamlit)                               │
│    - Diagrama de Ishikawa visual (matplotlib)       │
│    - Cards de 5 Porquês com numeração               │
│    - Expanders colapsáveis                          │
│    - Botão de download .md                          │
└─────────────────────────────────────────────────────┘
```

---

## Sistema RAG de 2 Estágios

### Por que 2 estágios?

| Estágio | Método | Custo | Precisão |
|---------|--------|-------|----------|
| 1 - Filtro | Regras (Área+Equip) | Zero | Alta recall, baixa precision |
| 2 - Refinamento | IA (Gemini Flash) | Baixo | Alta precision |

### Estágio 1: Filtro Estruturado

```python
# HistoryManager.find_related_failures()
# Normalização para comparação robusta:
"Área de Saída " → "area de saida"
"ÁREA DE SAÍDA"  → "area de saida"
```

### Estágio 2: Refinamento Semântico

O prompt de refinamento (`prompts.build_history_refinement_prompt`) instrui a IA a:

1. Analisar a falha atual
2. Comparar semanticamente com candidatos
3. Selecionar os 3 mais relevantes
4. Justificar a escolha

---

## Engenharia de Prompts

O arquivo `core/prompts.py` (~18KB) contém toda a engenharia de prompts:

### Estrutura do Prompt Final

```
┌────────────────────────────────────────┐
│ 1. INTRO (Persona e contexto)          │
│    "Você é um especialista em RCA..."  │
├────────────────────────────────────────┤
│ 2. INPUT_SECTION (Dados estruturados)  │
│    - Área, Equipamento, Descrição      │
│    - Análises de mídia (imagem/vídeo)  │
├────────────────────────────────────────┤
│ 3. HISTORY_SECTION (RAG)               │
│    - Top 3 falhas históricas           │
├────────────────────────────────────────┤
│ 4. TASK_INSTRUCTIONS                   │
│    - Gerar Ishikawa                    │
│    - Gerar 5 Porquês                   │
│    - Propor Plano de Ação              │
├────────────────────────────────────────┤
│ 5. FORMAT_SPEC (JSON esperado)         │
│    - Schema exato da resposta          │
├────────────────────────────────────────┤
│ 6. EXAMPLE_RESPONSE                    │
│    - Exemplo completo para few-shot    │
├────────────────────────────────────────┤
│ 7. CRITICAL_NOTES                      │
│    - Regras de output                  │
└────────────────────────────────────────┘
```

---

## Estratégia de Logging

### Configuração

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```

### Níveis de Log

| Nível | Uso |
|-------|-----|
| `INFO` | Progresso normal (início/fim de análise) |
| `WARNING` | Arquivo não encontrado, formato não suportado |
| `ERROR` | Falha em API, exceção capturada |

### Logs importantes

```python
# HistoryManager
logging.info(f"Gerenciador de Histórico inicializado com {len(self.history_data)} registros.")
logging.info(f"Filtro encontrou {len(related_failures)} falhas relacionadas.")

# VideoAnalyzer
logging.info(f"Iniciando upload do vídeo: {video_path.name}")
logging.info(f"Arquivo deletado da API após análise.")

# AIProcessor
logging.info(f"Resposta do modelo recebida. Tokens: {token_count}")
```

---

## Padrões de Código

### 1. Uso obrigatório de Pathlib

```python
# ✅ CORRETO
from pathlib import Path
excel_path = folder_path / "analysis.xlsx"

# ❌ ERRADO
excel_path = folder_path + "/analysis.xlsx"
```

### 2. Fail Fast no Core

```python
# config_loader.py
if not config_file.exists():
    raise FileNotFoundError(f"Config file '{config_path}' not found.")
```

### 3. Graceful Degradation no Worker

```python
# image_analyzer.py
try:
    response = self.model.generate_content([prompt, image])
except Exception as e:
    return f"📷 **{image_path.name}**\n\nErro: {str(e)}"
```

### 4. Docstrings Google Style

```python
def funcao(param1: str, param2: int) -> dict:
    """
    Descrição concisa.
    
    Args:
        param1: Descrição do parâmetro.
        param2: Descrição do parâmetro.
    
    Returns:
        Descrição do retorno.
    
    Raises:
        TipoExcecao: Quando ocorre.
    """
```

---

*Documentação gerada automaticamente em Janeiro 2026*
