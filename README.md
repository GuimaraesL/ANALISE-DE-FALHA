# 🔍 Sistema Inteligente de Análise de Causa Raiz (RCA) com IA

![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5-purple.svg)

> **Automatiza a análise de causa raiz de falhas industriais usando IA multimodal com RAG de 2 estágios para correlação histórica.**

---

## 📖 Sobre o Projeto

Este projeto é uma aplicação web construída com **Streamlit** e **Python** que automatiza o processo de **Análise de Causa Raiz (RCA)** de falhas em equipamentos industriais. A aplicação utiliza os modelos de linguagem da **Google (Gemini 2.5)** para analisar dados multimodais (Excel, imagens, vídeos) e gerar relatórios técnicos estruturados seguindo metodologias consagradas como **Diagrama de Ishikawa** e **5 Porquês**.

---

## ✨ Funcionalidades Principais

| Funcionalidade | Descrição |
|----------------|-----------|
| 📊 **Análise Multimodal** | Processa arquivos Excel, imagens e vídeos simultaneamente |
| 🔍 **RAG de 2 Estágios** | Busca e refina histórico de falhas para contexto enriquecido |
| 🐟 **Diagrama de Ishikawa** | Geração automática de diagrama de causa e efeito |
| ❓ **5 Porquês** | Análise estruturada com cards interativos |
| 🎯 **Plano de Ação** | Recomendações práticas baseadas na análise |
| 🖼️ **Contexto de Mídias** | Permite guiar a IA com observações por foto/vídeo |
| 🌐 **Bilíngue** | Suporte completo a Português e Inglês |
| 📥 **Export Markdown** | Download de relatórios no formato .md |

---

## 🏗️ Arquitetura do Sistema

### Fluxo de Dados

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE DE ANÁLISE                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  📁 ENTRADA              🔧 PROCESSAMENTO              📤 SAÍDA         │
│  ════════                ═══════════════               ═══════          │
│                                                                          │
│  ┌─────────┐            ┌─────────────────┐                             │
│  │ Pasta   │───────────▶│ ExcelReader     │──▶ Dados estruturados       │
│  │ Excel   │            └─────────────────┘                             │
│  │ Imagens │            ┌─────────────────┐                             │
│  │ Vídeos  │───────────▶│ ImageAnalyzer   │──▶ Laudo técnico visual     │
│  └─────────┘            │ (Gemini Flash)  │                             │
│       │                 └─────────────────┘                             │
│       │                 ┌─────────────────┐                             │
│       └────────────────▶│ VideoAnalyzer   │──▶ Análise de movimento     │
│                         │ (Gemini Flash)  │                             │
│                         └─────────────────┘                             │
│                                  │                                       │
│  ┌─────────────┐                 ▼                                       │
│  │ extracted_  │         ┌─────────────────┐                            │
│  │ data.json   │────────▶│ HistoryManager  │                            │
│  │ (Histórico) │         │ RAG Estágio 1   │                            │
│  └─────────────┘         │ (Filtro)        │                            │
│                          └────────┬────────┘                            │
│                                   ▼                                      │
│                          ┌─────────────────┐                            │
│                          │ AIProcessor     │                            │
│                          │ RAG Estágio 2   │──▶ Refinamento semântico   │
│                          │ (Gemini Pro)    │                            │
│                          └────────┬────────┘                            │
│                                   ▼                                      │
│                          ┌─────────────────┐      ┌──────────────┐      │
│                          │ Análise Final   │─────▶│ Ishikawa     │      │
│                          │ (Gemini 2.5 Pro)│      │ 5 Porquês    │      │
│                          └─────────────────┘      │ Plano Ação   │      │
│                                   │               │ Conclusão    │      │
│                                   ▼               └──────────────┘      │
│                          ┌─────────────────┐                            │
│                          │ ReportGenerator │──▶ 📄 Relatório .md        │
│                          └─────────────────┘                            │
└──────────────────────────────────────────────────────────────────────────┘
```

### Sistema RAG de 2 Estágios

O diferencial deste sistema é o **RAG (Retrieval-Augmented Generation) de 2 estágios**:

1. **Estágio 1 - Filtro Estruturado** (`HistoryManager`)
   - Busca no banco `extracted_data.json` por falhas com mesma Área + Equipamento + Subgrupo
   - Normalização de texto (remove acentos, lowercase)
   - Retorna lista ampla de candidatos

2. **Estágio 2 - Refinamento Semântico** (`AIProcessor.refine_history_with_ai`)
   - IA analisa contexto da falha atual vs candidatos
   - Seleciona os 3 casos mais relevantes semanticamente
   - Gera resumo contextualizado para o prompt final

---

## 📂 Estrutura do Projeto

```
ANALISE-DE-FALHA/
├── 📄 app.py                    # Ponto de entrada Streamlit (UI principal)
├── 📄 test_ui_preview.py        # Preview de componentes UI sem gastar créditos
├── 📄 config.json               # Configurações (API keys) - NÃO versionar!
├── 📄 extracted_data.json       # Banco de dados histórico (~12MB)
├── 📄 styles.css                # Estilos CSS premium para UI
├── 📄 requirements.txt          # Dependências Python
│
├── 📁 core/                     # Lógica de negócio
│   ├── __init__.py
│   ├── ai_processor.py          # Montagem de prompt + Gemini 2.5 Pro
│   ├── config_loader.py         # Carregador de config.json
│   ├── excel_reader.py          # Extração de dados Excel (aba A3)
│   ├── failure_analysis_app.py  # Orquestrador principal do pipeline
│   ├── history_manager.py       # RAG Estágio 1 (filtro por área/equip)
│   ├── image_analyzer.py        # Análise de imagens (Gemini Flash)
│   ├── pdf_as_image_converter.py# Conversão PDF → Imagem
│   ├── prompts.py               # Engenharia de prompts (18KB)
│   ├── report_generator.py      # Gerador de relatórios .md
│   └── video_analyzer.py        # Análise de vídeos (Gemini Flash)
│
├── 📁 ui/                       # Interface do usuário
│   ├── __init__.py
│   └── texts.py                 # Internacionalização (PT/EN)
│
├── 📁 relatorios/               # Relatórios gerados (saída)
├── 📁 logs/                     # Logs de execução
└── 📁 Site/                     # Assets para página web (opcional)
```

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Versão |
|-----------|------------|--------|
| **Linguagem** | Python | 3.9+ |
| **Framework Web** | Streamlit | 1.x |
| **IA Principal** | Google Gemini 2.5 Pro | Latest |
| **IA Auxiliar** | Google Gemini 2.5 Flash | Latest |
| **Leitura Excel** | Openpyxl | 3.x |
| **Normalização** | Unidecode | 1.x |
| **Gráficos** | Matplotlib | 3.x |

---

---

## ⚙️ Restrições Técnicas e Padrões

Este projeto segue padrões rigorosos de qualidade de código:

| Padrão | Regra | Motivo |
|--------|-------|--------|
| 🛤️ **Pathlib** | `from pathlib import Path` obrigatório | Compatibilidade Windows/Linux |
| 🚫 **print()** | Proibido, usar `logging` | Rastreabilidade e níveis de log |
| ⚡ **Fail Fast** | Exceções específicas no core | Identificação rápida de erros |
| 📦 **Stateless** | Classes sem estado desnecessário | Facilita testes e manutenção |
| 🔒 **Config Seguro** | `config.json` no `.gitignore` | Proteção de API keys |

---

## 🚀 Setup e Execução

### 1. Pré-requisitos

- Python 3.9 ou superior
- Chave da API do Google Gemini
- (Opcional) Credenciais do Vertex AI para análise de vídeo

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/ANALISE-DE-FALHA.git
cd ANALISE-DE-FALHA

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
.\venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração

Crie um arquivo `config.json` na raiz do projeto:

```json
{
    "gemini_api_key": "SUA_CHAVE_API_AQUI",
    "google_credentials_path": "vertex-key.json"
}
```

### 4. Execução

```bash
# Iniciar aplicação principal
streamlit run app.py

# Ou para testar UI sem gastar créditos
streamlit run test_ui_preview.py
```

---

## 🔧 Troubleshooting

### Problema: "API key not found"

**Causa:** Arquivo `config.json` não encontrado ou mal formatado.

**Solução:**
```bash
# Verifique se o arquivo existe
ls config.json

# Verifique o conteúdo (JSON válido)
cat config.json | python -m json.tool
```

### Problema: "Arquivo de histórico não encontrado"

**Causa:** O arquivo `extracted_data.json` não está presente.

**Solução:** Este arquivo contém o histórico de falhas para o RAG. Você precisa obtê-lo do sistema de extração ou criar um arquivo vazio:
```json
[]
```

### Problema: "Port 8501 already in use"

**Causa:** Outra instância do Streamlit está rodando.

**Solução:**
```bash
# Use outra porta
streamlit run app.py --server.port 8502
```

### Problema: "ModuleNotFoundError: No module named 'core'"

**Causa:** Você não está na pasta raiz do projeto.

**Solução:**
```bash
cd C:\caminho\para\ANALISE-DE-FALHA
streamlit run app.py
```

### Problema: Análise de vídeo falhando

**Causa:** Credenciais do Vertex AI não configuradas.

**Solução:**
1. Coloque o arquivo `vertex-key.json` na raiz do projeto
2. Configure o caminho no `config.json`:
   ```json
   "google_credentials_path": "vertex-key.json"
   ```

---

## 📊 Métricas de Tokens

O sistema exibe o consumo de tokens de cada análise:

| Métrica | Descrição |
|---------|-----------|
| **Tokens de Entrada** | Prompt + histórico + análises de mídia |
| **Tokens de Saída** | Resposta da IA (Ishikawa, 5 Porquês, etc) |
| **Custo Estimado** | Baseado na tabela de preços do Gemini |

⚠️ **Limite Recomendado:** Manter prompt final abaixo de 30.000 tokens para otimização de custo.

---

## 🗺️ Roadmap e Evolução

O projeto possui um plano de evolução estruturado para transicionar de uma ferramenta de análise para um **Sistema Especialista de Manutenção**.

**Destaques do [ROADMAP.md](ROADMAP.md):**
- **Persistência SQLite:** Memória de longo prazo para análises.
- **Calibração de Especialista:** Aprendizado através de feedback humano (Dynamic Few-Shot).
- **Busca Semântica (RAG):** Migração para banco de vetores para correlação avançada.

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido por **Leonardo Guimarães**

---

*Última atualização: Janeiro 2026*