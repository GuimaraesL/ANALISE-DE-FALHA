# 🏛️ Arquitetura do Sistema ANALISE-DE-FALHA

> Documentação técnica detalhada da arquitetura interna do sistema de Análise de Causa Raiz.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Componentes Principais](#componentes-principais)
3. [Arquitetura da UI Modular](#arquitetura-da-ui-modular) *(NOVO)*
4. [Fluxo de Dados Detalhado](#fluxo-de-dados-detalhado)
5. [Sistema RAG de 2 Estágios](#sistema-rag-de-2-estágios)
6. [Engenharia de Prompts](#engenharia-de-prompts)
7. [Estratégia de Logging](#estratégia-de-logging)
8. [Padrões de Código](#padrões-de-código)

---

## Visão Geral

O sistema **ANALISE-DE-FALHA** é uma aplicação de análise automatizada que combina:

- **Processamento Multimodal**: Excel, imagens e vídeos
- **RAG (Retrieval-Augmented Generation)**: Contexto histórico enriquecido
- **IA Generativa**: Google Gemini 2.5 para análise e geração de relatórios
- **UI Premium Modular**: Interface Streamlit com componentes reutilizáveis

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE APRESENTAÇÃO (ui/)                     │
│  ┌───────────────┐  ┌───────────────────────────────────────────────┐   │
│  │   app.py      │  │                   ui/                          │   │
│  │ (Entry Point) │  │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │   │
│  │   ~140 lines  │──▶│  │  pages/     │ │ components/ │ │ utils.py │ │   │
│  └───────────────┘  │  │ ├─sidebar   │ │ ├─ishikawa  │ │          │ │   │
│                      │  │ └─results   │ │ ├─five_whys │ └──────────┘ │   │
│  ┌───────────────┐  │  └─────────────┘ │ └─raw_resp  │ ┌──────────┐ │   │
│  │test_ui_preview│  │                   └─────────────┘ │ texts.py │ │   │
│  │  (Mock Data)  │  │  ┌─────────────┐ ┌─────────────┐ │  (i18n)  │ │   │
│  └───────────────┘  │  │  styles.py  │ │ styles.css  │ └──────────┘ │   │
│                      │  └─────────────┘ └─────────────┘               │   │
│                      └───────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│                         CAMADA DE ORQUESTRAÇÃO                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                  FailureAnalysisApp                                 │ │
│  │  • Descoberta de arquivos (Excel, imagens, vídeos)                  │ │
│  │  • Coordenação de fluxo                                             │ │
│  │  • Barra de progresso                                               │ │
│  └─────────────────────────┬───────────────────────────────────────────┘ │
│                            │                                             │
├────────────────────────────┼─────────────────────────────────────────────┤
│           CAMADA DE SERVIÇOS (core/)                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ExcelReader  │  │ImageAnalyzer│  │VideoAnalyzer│  │HistoryMgr  │     │
│  │ (Openpyxl)  │  │(Gemini Flash)│ │(Gemini Flash)│ │(RAG Stage1)│     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │                │             │
│         └────────────────┼────────────────┼────────────────┘             │
│                          ▼                ▼                              │
│              ┌─────────────────────────────────────┐                     │
│              │          AIProcessor                │                     │
│              │  • Montagem de prompt (prompts.py)  │                     │
│              │  • RAG Estágio 2 (refinamento)      │                     │
│              │  • Chamada Gemini 2.5 Pro           │                     │
│              │  • Parsing de resposta JSON         │                     │
│              └─────────────────────────────────────┘                     │
│                          │                                               │
│                          ▼                                               │
│              ┌─────────────────────────────────────┐                     │
│              │       ReportGenerator               │                     │
│              │  • Formatação Markdown              │                     │
│              │  • Salvamento em relatorios/        │                     │
│              └─────────────────────────────────────┘                     │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                         CAMADA DE DADOS                                  │
│  ┌─────────────┐  ┌─────────────────────┐  ┌──────────────────────┐     │
│  │config.json  │  │ extracted_data.json │  │   texts.py (i18n)    │     │
│  │ (API Keys)  │  │ (Histórico 12MB)    │  │   (PT/EN)            │     │
│  └─────────────┘  └─────────────────────┘  └──────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────┘
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

## Arquitetura da UI Modular

> Refatoração realizada em Janeiro/2026: O `app.py` monolítico (~565 linhas) foi dividido em módulos especializados.

### Estrutura de Diretórios

```
ui/
├── __init__.py           # Exporta todos os módulos
├── styles.py             # Carregamento de CSS via pathlib
├── utils.py              # Funções auxiliares (markdown, limpeza)
├── texts.py              # Internacionalização (PT/EN)
│
├── components/           # Componentes visuais reutilizáveis
│   ├── __init__.py
│   ├── ishikawa.py       # Diagrama de Ishikawa (matplotlib)
│   ├── five_whys.py      # Visualização dos 5 Porquês (cards/lista)
│   └── raw_response.py   # Resposta bruta formatada (seções)
│
└── pages/                # Páginas da aplicação
    ├── __init__.py
    ├── sidebar.py        # Configurações e inputs do usuário
    └── results.py        # Renderização dos resultados da análise
```

### Componentes Reutilizáveis (`ui/components/`)

| Componente | Arquivo | Função Principal | Descrição |
|------------|---------|------------------|-----------|
| **Ishikawa** | `ishikawa.py` | `plot_ishikawa()` | Diagrama de causa-efeito com 6 categorias |
| **5 Porquês** | `five_whys.py` | `display_five_whys()` | Múltiplos modos: cards, colunas, lista |
| **Resposta Bruta** | `raw_response.py` | `display_raw_response()` | Seções colorizadas com tabs |

#### 1. Ishikawa (`ishikawa.py`)

```python
def plot_ishikawa(causes: dict, effect: str) -> None:
    """
    Renderiza diagrama de Ishikawa usando matplotlib.
    
    Categorias:
    - Máquina, Material, Método
    - Mão de obra, Meio ambiente, Medição
    """
```

#### 2. Five Whys (`five_whys.py`)

```python
def display_five_whys(
    five_whys_data: list,
    mode: str = "cards"  # "cards", "columns", "list"
) -> None:
    """
    Renderiza a análise dos 5 Porquês.
    
    Modos:
    - cards: Cards visuais com gradiente
    - columns: Layout em 5 colunas
    - list: Lista numerada simples
    """
```

#### 3. Raw Response (`raw_response.py`)

```python
def display_raw_response(
    raw_response: str,
    show_source: bool = True
) -> None:
    """
    Renderiza resposta bruta da IA com formatação.
    
    Funcionalidades:
    - Tabs: Renderizado vs Código Fonte
    - Seções coloridas (Ishikawa=azul, Porquês=roxo, etc.)
    - Remoção automática de backticks/blocos vazios
    """

# Função auxiliar para limpeza:
def _clean_response(text: str) -> str:
    """Remove backticks e blocos de código vazios."""
```

### Páginas (`ui/pages/`)

#### 1. Sidebar (`sidebar.py`)

```python
def render_sidebar(texts: dict) -> dict:
    """
    Renderiza a sidebar com todas as configurações.
    
    Returns:
        dict com chaves:
        - root_folder: Pasta selecionada
        - enable_images: bool
        - enable_videos: bool
        - language: "pt" ou "en"
    """

def validate_config(config: dict) -> tuple[bool, str]:
    """
    Validação Fail Fast das configurações.
    
    Returns:
        (is_valid, error_message)
    """
```

#### 2. Results (`results.py`)

```python
def render_results(result: dict, texts: dict) -> None:
    """
    Orquestra a renderização de todos os resultados.
    
    Seções renderizadas:
    1. Dados do Excel (cards azuis)
    2. Diagrama de Ishikawa
    3. 5 Porquês (cards roxos)
    4. Resposta Bruta (tabs)
    5. Histórico Bruto (tabs: Visual + JSON)
    6. Histórico Correlacionado (card verde)
    7. Métricas de Tokens (3 colunas)
    """

# Funções auxiliares:
def _get_field(data: dict, *keys, default="N/A") -> str:
    """Extrai campo tentando múltiplas chaves."""

def _render_history_card(failure: dict, index: int, texts: dict) -> None:
    """Renderiza card visual para falha histórica."""

def _render_tokens(result: dict, texts: dict) -> None:
    """Renderiza métricas de tokens com visual premium."""
```

### Fluxo de Renderização

```
┌─────────────────────────────────────────────────────────────────┐
│                         app.py (Entry Point)                     │
│  1. Configura logging                                            │
│  2. Carrega credenciais (config.json)                           │
│  3. Aplica CSS (styles.py → styles.css)                         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     sidebar.py → render_sidebar()                │
│  • Seleção de pasta                                             │
│  • Toggle: imagens, vídeos                                      │
│  • Seleção de idioma                                            │
│  • Botão "Analisar"                                             │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FailureAnalysisApp.run()                         │
│  • Processa pasta selecionada                                    │
│  • Atualiza barra de progresso                                   │
│  • Retorna: result dict                                          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    results.py → render_results()                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ _render_excel_data()    → Cards com dados do Excel          ││
│  │ plot_ishikawa()         → Diagrama de causa-efeito          ││
│  │ display_five_whys()     → Cards dos 5 Porquês               ││
│  │ display_raw_response()  → Resposta bruta formatada          ││
│  │ _render_history()       → Tabs: Visual + JSON               ││
│  │ _render_tokens()        → Métricas de consumo               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Constantes de Estilo (`results.py`)

```python
# Estilos reutilizáveis para cards (inline CSS)
STYLE_CARD = "background: linear-gradient(135deg, ...); ..."
STYLE_HISTORY_CARD = "background: linear-gradient(135deg, #2D1B4E ...); ..."
STYLE_REFINED_HISTORY = "background: rgba(34, 197, 94, 0.1); ..."
```

### Benefícios da Modularização

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Linhas app.py** | ~565 | ~140 |
| **Testabilidade** | Difícil | Fácil (componentes isolados) |
| **Manutenção** | Tudo junto | Separação de responsabilidades |
| **Reutilização** | Nenhuma | Componentes importáveis |
| **Preview** | Dependia de API | `test_ui_preview.py` com mocks |

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
