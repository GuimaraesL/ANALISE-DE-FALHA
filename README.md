# 🔍 Sistema Inteligente de Análise de Causa Raiz (RCA) com IA — V2 Agêntico

![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5-purple.svg)
![Framework](https://img.shields.io/badge/Framework-Agno-orange.svg)
![Database](https://img.shields.io/badge/Database-SQLite-blue.svg)

> **Orquestração agêntica autônoma para análise de causa raiz de falhas industriais usando o framework Agno, IA multimodal (Gemini 2.5) e busca dinâmica no banco de dados SQLite.**

---

## 📖 Sobre o Projeto

Este projeto é uma aplicação de nível corporativo voltada para a **Análise de Causa Raiz (RCA)** de falhas em equipamentos industriais. Em sua **versão V2**, o sistema foi redefinido para adotar uma arquitetura baseada em **Agentes de IA Autônomos (framework Agno)** e persistência em **SQLite (Padrão Repository)**, substituindo análises lineares tradicionais por tomadas de decisões inteligentes.

O agente especialista correlaciona dados multimodais (tabelas, imagens e vídeos) com mais de 2.300 registros históricos e calibrações de especialistas anteriores (**Gold Standards**), produzindo laudos altamente precisos e estruturados em metodologias como **Diagrama de Ishikawa**, **5 Porquês** e **Plano de Ação (5W2H)**.

---

## ✨ Funcionalidades Principais (V2 Agêntico)

| Funcionalidade | Descrição |
|----------------|-----------|
| 🤖 **Agente Autônomo Agno** | Orquestrador inteligente baseado em `Gemini-2.5-Pro` que decide quando consultar o histórico e quando inspecionar as mídias. |
| 🗄️ **Persistência SQLite** | Banco de dados relacional unificado (`analyses`, `expert_feedback`, `historical_failures`) com criação automática (*Fail Fast*). |
| 👁️ **Ferramentas Multimodais** | Detecção visual de anomalias em fotos e análise temporal de vibrações/movimentos em vídeos com `Gemini-2.5-Flash`. |
| 🔍 **Busca Dinâmica "Human-Like"** | Estratégia adaptativa de busca histórica em múltiplos níveis com fallback automático caso filtros estritos falhem. |
| 🏆 **Memória de Calibração (Gold Standards)** | Injeção dinámica de exemplos "Ouro" validados por especialistas no prompt do agente (*Few-Shot Learning*). |
| 🐟 **Diagrama de Ishikawa** | Geração automática do diagrama de causa e efeito estruturado nas categorias clássicas de manufatura. |
| ❓ **Análise Interativa de 5 Porquês** | Decomposição lógica em profundidade até a causa raiz. |
| 📋 **Plano de Ação Inteligente** | Recomendações e medidas preventivas baseadas no diagnóstico e nos precedentes. |
| 🌐 **Suporte Bilíngue** | Interface e relatórios traduzidos dinamicamente (Português e Inglês). |

---

## 🏗️ Arquitetura do Sistema

### Fluxo de Dados Agêntico

O pipeline linear da V1 foi substituído por um fluxo dinâmico em que o **Agente Líder (Agno Framework)** tem acesso a ferramentas de visão e busca persistente para resolver a causa de forma iterativa:

```
┌──────────────────────────────────────────────────────────────────────────┐
┌──────────────────────────────────────────────────────────────────────────┐
│                           ARQUITETURA V2 AGÊNTICA                        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                       ┌────────────────────────┐                         │
│                       │    Interface Streamlit │                         │
│                       └───────────┬────────────┘                         │
│                                   │                                      │
│                                   ▼                                      │
│                     ┌───────────────────────────┐                        │
│                     │   LeadAnalysisAgent (V2)  │                        │
│                     │  (Gemini-2.5-Pro + Agno)  │                        │
│                     └──────┬──────────────┬─────┘                        │
│                            │              │                              │
│         [Usa Ferramentas]  │              │  [Injeta Gold Standards]     │
│                            ▼              ▼                              │
│      ┌──────────────────────────┐    ┌──────────────────────────┐        │
│      │   FailureAnalysisTools   │    │      DatabaseManager     │        │
│      └──────┬────────────┬──────┘    │ (few_failure_analysis.db)│        │
│             │            │           └────────────┬─────────────┘        │
│             ▼            ▼                        │                      │
│      ┌───────────┐  ┌───────────┐                 │                      │
│      │  Visão    │  │ Busca DB  │                 │                      │
│      │  Mídias   │  │ Histórica │                 │                      │
│      └─────┬─────┘  └─────┬─────┘                 │                      │
│            │              │                       │                      │
│            ▼              └───────────────┐       │                      │
│      ┌───────────┐                        ▼       ▼                      │
│      │ Gemini    │                  ┌──────────────────────────┐         │
│      │ 2.5 Flash │                  │  SQLite:                 │         │
│      └───────────┘                  │  - analyses              │         │
│                                     │  - expert_feedback       │         │
│                                     │  - historical_failures   │         │
│                                     └──────────────────────────┘         │
│                                                                          │
│  SAÍDA ESTRUTURADA:                                                      │
│  📄 Ishikawa 5M/6M  ▶  ❓ 5 Porquês  ▶  🎯 Plano de Ação  ▶  📝 Laudo .md │
└──────────────────────────────────────────────────────────────────────────┘
```

### Busca Histórica Dinâmica (Human-Like Fallback)

O sistema de busca histórica foi otimizado para evitar buscas vazias e maximizar o contexto enriquecido:
1. **Primeira Tentativa:** Busca restrita e estruturada filtrando por `Área + Equipamento + Subgrupo` exatos no banco SQLite.
2. **Segundo Nível (Fallback 1):** Se nenhum registro for encontrado, alarga a busca para listar qualquer falha no `Equipamento`.
3. **Terceiro Nível (Fallback 2):** Caso ainda esteja vazio, realiza uma pesquisa textual flexível usando termos técnicos (`description_keyword`) no campo de descrição da falha.

---

## 📂 Estrutura do Projeto

```
ANALISE-DE-FALHA/
├── 📄 app.py                    # Streamlit UI (Engine V1 / V2 comutável)
├── 📄 test_ui_preview.py        # Preview da interface sem custos de API
├── 📄 config.json               # Credenciais e API Keys (Ignorado no git)
├── 📄 styles.css                # Customização visual e design system premium
├── 📄 requirements.txt          # Dependências do projeto (incluindo agno)
│
├── 📁 core/                     # Núcleo lógico do sistema
│   ├── __init__.py
│   ├── ai_processor.py          # Processamento linear V1 (Gemini 2.5 Pro)
│   ├── config_loader.py         # Tratamento portátil e seguro de credenciais
│   ├── database.py              # Gerenciador de Banco de Dados SQLite (Repository)
│   ├── excel_reader.py          # Extrator e parser de dados da aba A3
│   ├── failure_analysis_app.py  # Orquestrador unificado das análises
│   ├── history_manager.py       # Gerenciamento de histórico V1
│   ├── image_analyzer.py        # Processamento e laudo de fotos (Gemini Flash)
│   ├── pdf_as_image_converter.py# Auxiliar para conversão de PDFs
│   ├── prompts.py               # Engenharia de prompts estruturada
│   ├── report_generator.py      # Gerador automatizado de relatórios em Markdown
│   ├── video_analyzer.py        # Processamento de vídeos industriais (Gemini Flash)
│   │
│   └── 📁 agents/               # Framework Agêntico Agno
│       ├── __init__.py
│       ├── analyst_agent.py     # Agente Líder (LeadAnalysisAgent) e Personas
│       └── tools.py             # Encapsulamento de ferramentas para o agente
│
├── 📁 data/                     # Persistência de Dados centralizada
│   ├── failure_analysis.db      # Banco de dados SQLite de Produção
│   ├── analysis_results.db      # Banco auxiliar de históricos de execuções
│   └── extracted_data.json      # Dados históricos brutos legados (para importação)
│
├── 📁 ui/                       # Módulos de Interface
│   ├── __init__.py
│   └── texts.py                 # Dicionários de internacionalização (PT/EN)
│
├── 📁 tests/                    # Suíte de Testes Automatizados
│   ├── test_imports.py          # Validação de importações e integridade de módulos
│   └── test_v2_integration.py   # Testes unitários do Database e do Agente
│
├── 📁 relatorios/               # Relatórios gerados em Markdown (.md)
├── 📁 logs/                     # Registro de eventos estruturados em arquivos .log
└── 📁 Site/                     # Landing page ou assets complementares
```

---

## 🛠️ Tecnologias e Dependências

| Categoria | Tecnologia | Versão Mínima |
|-----------|------------|---------------|
| **Linguagem** | Python | `3.9+` |
| **Framework Web** | Streamlit | `1.30.0` |
| **IA Principal** | Agno Framework / Gemini 2.5 Pro | `Latest` |
| **Visão / Mídia** | Google Gemini 2.5 Flash | `Latest` |
| **Banco de Dados** | SQLite / sqlite3 | `Nativo` |
| **Análise de Dados** | Openpyxl / Pandas | `3.1.0` / `2.0.0` |

---

## 🚀 Instalação e Execução

### 1. Clonar e Inicializar Diretório
```bash
git clone https://github.com/GuimaraesL/ANALISE-DE-FALHA.git
cd ANALISE-DE-FALHA
```

### 2. Configurar o Ambiente Virtual
```powershell
# Criação do virtualenv
python -m venv venv

# Ativação (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ativação (Linux / macOS)
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente e Arquivo de Credenciais
Crie o arquivo `config.json` na raiz do projeto (este arquivo é protegido e está listado no `.gitignore`):
```json
{
    "gemini_api_key": "SUA_CHAVE_API_GEMINI_AQUI",
    "google_credentials_path": "vertex-key.json"
}
```

### 5. Executar os Testes de Integração
Antes de rodar a UI Streamlit, valide se o ambiente e o banco de dados estão respondendo perfeitamente:
```bash
python tests/test_v2_integration.py
```

### 6. Inicializar o Streamlit
```bash
streamlit run app.py
```

---

## ⚙️ Padrões Rigorosos e Qualidade de Código

Para manter a portabilidade e a integridade em sistemas operacionais múltiplos (Windows/Linux/OneDrive), o projeto adota:
*   **Pathlib Extensivo:** Ausência total de caminhos fixados por string (`/` ou `\`). Todos os caminhos resolvem de forma absoluta a partir de `__file__`.
*   **Logging Estruturado:** Uso exclusivo da biblioteca nativa `logging`. Uso de `print()` é proibido.
*   **Fail Fast:** Exceções são validadas na inicialização do SQLite ou durante a leitura do Excel, emitindo avisos detalhados e amigáveis ao usuário antes de prosseguir.
*   **Repository Pattern:** A interface com o banco SQLite em `core/database.py` expõe apenas operações abstratas de negócios, isolando o código de persistência da UI.

---

## 🏆 Memória Evolutiva & Calibração Humana

Um grande destaque da **arquitetura V2** é a calibração contínua do comportamento da IA:
1. **Geração do RCA:** A IA cria o diagnóstico e persistência de forma autônoma na tabela `analyses`.
2. **Avaliação do Especialista:** Engenheiros de manutenção avaliam a saída no Streamlit e fornecem notas ou correções textuais.
3. **Marcação de Gold Standard:** Quando marcada como um exemplo exemplar, a análise é salva na tabela `expert_feedback` como `is_gold_standard = True`.
4. **Few-Shot Ingestion:** Nas próximas análises de problemas semelhantes, o `LeadAnalysisAgent` automaticamente recebe as notas e as resoluções anteriores do especialista no prompt, refinando as futuras gerações.

---

## 📝 Licença e Contato

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

Desenvolvido por **Leonardo Guimarães**
*Última atualização da documentação: Maio de 2026*