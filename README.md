Com certeza\! Um bom `README.md` é a porta de entrada para qualquer projeto. Ele ajuda outros desenvolvedores (e até você mesmo no futuro) a entenderem o propósito, a estrutura e como utilizar a aplicação.

Com base em todos os arquivos e na evolução do nosso trabalho, gerei um `README.md` completo e profissional para o seu projeto.

-----

### README.md

````markdown
# Sistema Inteligente de Análise de Causa Raiz (RCA) com IA

Este projeto é um aplicativo web construído com Streamlit e Python, projetado para automatizar e aprimorar o processo de Análise de Causa Raiz (RCA) de falhas em equipamentos industriais. A aplicação utiliza o poder dos modelos de linguagem da Google (Gemini) para analisar dados multimodais e gerar relatórios técnicos estruturados.

![Interface do App](https'://i.imgur.com/your-app-screenshot.png')  ---

## ✨ Funcionalidades Principais

* **Análise Multimodal:** Processa informações de diversas fontes para criar um contexto rico:
    * **Arquivos Excel:** Extrai dados estruturados sobre a falha (área, equipamento, descrição).
    * **Imagens e Vídeos:** Utiliza IA para analisar evidências visuais e gerar laudos técnicos.
* **Inteligência Aumentada por Histórico (RAG):**
    * O "4º Pilar" do sistema. A aplicação consulta um banco de dados JSON com falhas históricas.
    * **RAG de Dois Estágios:** Primeiro, filtra um conjunto de falhas relacionadas por equipamento e, em seguida, usa um prompt de IA intermediário para selecionar os 3 casos históricos mais relevantes semanticamente.
* **Geração Automática de Relatórios:**
    * Cria um relatório completo da análise no formato Markdown.
    * Inclui ferramentas de RCA padronizadas: **Diagrama de Ishikawa** e **5 Porquês**.
    * Propõe um **Plano de Ação** e uma **Conclusão** final baseada em todas as evidências.
* **Interface Interativa:** Interface web construída com Streamlit, permitindo uma experiência de usuário amigável e intuitiva.
* **Suporte a Múltiplos Idiomas:** A interface e os relatórios podem ser gerados em Português e Inglês.

---

## ⚙️ Como Funciona: O Fluxo Inteligente

O aplicativo segue um fluxo de trabalho em múltiplos estágios para garantir uma análise precisa e contextualizada:

1.  **Coleta de Dados:** O usuário seleciona uma pasta. O sistema localiza e carrega os arquivos `.xlsx`, imagens e vídeos.
2.  **Análise de Mídias:** A IA analisa cada imagem e vídeo, gerando descrições textuais das observações.
3.  **Busca no Histórico (RAG - Estágio 1):** O `HistoryManager` filtra o banco de dados `extracted_data.json` em busca de falhas passadas que ocorreram na mesma área, equipamento e subgrupo.
4.  **Refinamento do Histórico (RAG - Estágio 2):** Um prompt de IA intermediário recebe a lista de falhas do estágio anterior e, com base no contexto da falha atual, seleciona os 3 casos históricos mais relevantes.
5.  **Análise Final:** O modelo de IA principal (Gemini 2.5 Pro) recebe um dossiê completo contendo os dados do Excel, as análises de mídias e o histórico já refinado para gerar a análise de causa raiz.
6.  **Geração do Relatório:** O `ReportGenerator` formata a saída da IA em um arquivo `.md` estruturado.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **Framework Web:** Streamlit
* **Inteligência Artificial:** Google Gemini API (modelos 1.5 Pro e 1.5 Flash)
* **Manipulação de Dados:** Pandas
* **Leitura de Excel:** Openpyxl
* **Análise de Mídia:** OpenCV, Pillow (implícitas em outras bibliotecas)
* **Normalização de Texto:** Unidecode

---

## 📂 Estrutura do Projeto

```
.
├── core/
│   ├── ai_processor.py         # Lida com as chamadas à API Gemini e o parsing da resposta.
│   ├── excel_reader.py         # Extrai dados de arquivos .xlsx.
│   ├── failure_analysis_app.py # Classe principal que orquestra todo o fluxo.
│   ├── history_manager.py      # Gerencia a busca no histórico de falhas (JSON).
│   ├── image_analyzer.py       # Analisa imagens com IA.
│   ├── prompts.py              # Centraliza toda a engenharia de prompts.
│   ├── report_generator.py     # Gera os relatórios finais em .md.
│   └── video_analyzer.py       # Analisa vídeos com IA.
├── relatorios/                   # Pasta onde os relatórios .md são salvos.
├── ui/
│   └── texts.py                # Dicionário com todos os textos para i18n (PT/EN).
├── app.py                        # Ponto de entrada da aplicação Streamlit.
├── config.json                   # Arquivo de configuração (chaves de API, etc.).
├── extracted_data.json           # Banco de dados com o histórico de falhas.
├── requirements.txt              # Dependências do projeto.
└── styles.css                    # Estilização da interface.
```

---

## 🚀 Setup e Execução

### 1. Pré-requisitos

* Python 3.9 ou superior
* Acesso à API do Google Gemini

### 2. Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuração

1.  **Chave da API do Gemini:** Abra o arquivo `config.json` e insira sua chave da API do Gemini no campo `"gemini_api_key"`.
2.  **Credenciais do Vertex AI (se necessário para vídeo):** Garanta que o seu arquivo `vertex-key.json` (ou o nome que você definiu em `config.json`) esteja na pasta raiz do projeto.

### 4. Execução

Para iniciar o aplicativo, execute o seguinte comando no seu terminal, a partir da pasta raiz do projeto:

```bash
streamlit run app.py
```

O aplicativo será aberto automaticamente no seu navegador padrão.
````