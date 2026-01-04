# Roadmap Tecnológico: Sistema de Análise de Falhas AI

## Visão Estratégica
Transformar o sistema de uma ferramenta de geração de relatórios isolados em um **Ecossistema Inteligente de Gestão de Manutenção**, capaz de aprender com especialistas humanos e correlacionar dados históricos de forma semântica.

---

## Fases de Evolução

### ✅ Fase 1: Persistência e Memória (Concluída)
**Objetivo:** Transicionar de uma arquitetura *stateless* para *stateful* para permitir continuidade e auditoria.
- [x] **Implementação de Contexto:** Adição de observações manuais por mídia.
- [x] **Arquitetura de Banco de Dados:** Criação do módulo central `core/database.py` e migração de 2.300+ registros JSON para SQLite.
- [x] **Memória de Longo Prazo:** Integração do histórico industrial diretamente no cérebro do Agente.

### ✅ Fase 2: Agentes e Calibração (Concluída)
**Objetivo:** Transicionar de scripts lineares para uma orquestração baseada em Agentes (Agno).
- [x] **Agente Líder (Orquestrador):** Implementação do `LeadAnalysisAgent` com capacidade de busca autônoma em ferramentas.
- [x] **Modo de Curadoria (Gold Standards):** Interface para marcar análises de IA como referência técnica (Treinamento Few-Shot).
- [x] **Sincronização de Seniores:** Equilíbrio técnico entre as engines V1 e V2 utilizando Gemini 2.5 Pro.

### 🚀 Fase 3: RAG Avançado e Expansão (Em Andamento)
**Objetivo:** Escalar a base de conhecimento para documentos não estruturados e insights executivos.
- [ ] **Integração de Conhecimento (Base de Manuais):** Uso do parâmetro `knowledge` do Agno para leitura de manuais PDF de equipamentos.
- [ ] **Busca Semântica por Embeddings:** Transição da busca SQL exata para busca vetorial conceitual (Vector DB).
- [ ] **Dashboard de BI e Tendências:** Página de Analytics para identificar falhas recorrentes e economia de downtime.
- [ ] **Módulo de Áudio/Voz:** Transcrição de notas de campo através de modelos Whisper ou Gemini Audio.

### 🛠️ Fase 4: Excelência Operacional (Pipeline)
- [ ] **Migração de SDK:** Atualização para o novo `google-genai` (Remover Deprecated Warnings).
- [ ] **Segurança e Multitenancy:** Isolamento de bases de dados por áreas de manutenção.

---

## Arquitetura e Padrões (Compliance)

### Pilares de DevOps
1. **Clean Structure:** Organização modular em `core/`, `ui/`, `data/` e `config/`.
2. **Agentic Workflow:** Orquestração dinâmica via Agno para tomada de decisão em tempo real.
3. **Portabilidade:** Resolução de caminhos absolutos para operação em qualquer estação de trabalho.

---
*Documentação atualizada em: 04/01/2026 por Antigravity - Senior Code Quality Architect.*
