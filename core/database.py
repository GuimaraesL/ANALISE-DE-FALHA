# core/database.py
"""
Módulo de persistência utilizando SQLite para o sistema de Análise de Falhas.

Este módulo implementa o DatabaseManager utilizando o padrão Repository para
armazenar resultados de análises e feedbacks de especialistas, permitindo
a calibração do sistema (Few-Shot Aprendizado).

Autor: Antigravity - Senior Code Quality Architect
"""
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configurar logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gerenciador de banco de dados SQLite para persistência e calibração.
    
    Responsabilidades:
    - Criação e manutenção do esquema do banco de dados.
    - Persistência de análises completas (RCA).
    - Armazenamento de feedbacks de especialistas para treinamento de agentes.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa o gerenciador e garante que as tabelas existam.
        
        Args:
            db_path: Caminho para o arquivo .db. Se None, usa 'failure_analysis.db' na raiz.
        """
        if db_path is None:
            # Caminho padrão na pasta 'data' na raiz do projeto
            root = Path(__file__).parent.parent
            data_dir = root / "data"
            data_dir.mkdir(exist_ok=True) # Garante que a pasta data existe
            self.db_path = data_dir / "failure_analysis.db"
        else:
            if not isinstance(db_path, Path):
                raise TypeError("O caminho do banco de dados deve ser um objeto pathlib.Path")
            self.db_path = db_path
            
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o SQLite com suporte a nomes de colunas via Row."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self) -> None:
        """Cria as tabelas necessárias se elas não existirem (Fail Fast)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Tabela de Análises (RCA)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        folder_name TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        result_json TEXT NOT NULL,
                        tokens_input INTEGER,
                        tokens_output INTEGER,
                        total_cost REAL,
                        engine_version TEXT DEFAULT 'V1'
                    )
                """)
                
                # Tabela de Feedback de Especialista (Calibração)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS expert_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_id INTEGER,
                        is_gold_standard BOOLEAN DEFAULT FALSE,
                        corrected_conclusion TEXT,
                        expert_notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (analysis_id) REFERENCES analyses (id)
                    )
                """)
                
                # NOVO: Tabela de Falhas Históricas (Migração do JSON/Excel)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS historical_failures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area TEXT,
                        equipment TEXT,
                        subgroup TEXT,
                        description TEXT,
                        root_cause TEXT,
                        action_plan TEXT,
                        occurrence_date TEXT,
                        metadata_json TEXT
                    )
                """)
                
                # Índices para performance de busca (RAG Estágio 1)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_search ON historical_failures (area, equipment, subgroup)")
                
                conn.commit()
                logger.info(f"Banco de dados inicializado em: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erro fatal ao inicializar banco de dados: {e}")
            raise RuntimeError(f"Não foi possível inicializar o SQLite: {e}")

    def save_analysis(self, folder_name: str, result: Dict[str, Any], token_details: Dict[str, Any], engine: str = "V1") -> int:
        """
        Persiste o resultado de uma análise rca.
        
        Args:
            folder_name: Nome da pasta analisada.
            result: Dicionário completo com o resultado do FailureAnalysisApp.
            token_details: Detalhes de consumo de tokens.
            engine: Versão do motor utilizado (V1 ou V2).
            
        Returns:
            ID do registro inserido.
        """
        try:
            # Cálculo de custo simplificado (baseado no logger atual)
            input_tokens = token_details.get("prompt_tokens", 0) + token_details.get("history_input_tokens", 0)
            output_tokens = token_details.get("response_tokens", 0) + token_details.get("history_output_tokens", 0)
            total_cost = (input_tokens + output_tokens) / 1000 * 0.0115 # Exemplo de custo Gemini
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analyses (folder_name, result_json, tokens_input, tokens_output, total_cost, engine_version)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (folder_name, json.dumps(result), input_tokens, output_tokens, total_cost, engine))
                last_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Análise salva no DB (ID: {last_id}) para pasta: {folder_name}")
                return last_id or 0
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar análise: {e}")
            return -1

    def save_expert_feedback(self, analysis_id: int, is_gold: bool, correction: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """
        Armazena feedback do especialista para futura calibração por agentes.
        
        Args:
            analysis_id: Referência à tabela analyses.
            is_gold: Se esta análise deve ser usada como "Gold Standard" (exemplo de referência).
            correction: Texto corrigido da conclusão (opcional).
            notes: Notas do especialista sobre por que esta análise é boa ou o que foi corrigido.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expert_feedback (analysis_id, is_gold_standard, corrected_conclusion, expert_notes)
                    VALUES (?, ?, ?, ?)
                """, (analysis_id, is_gold, correction, notes))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar feedback do especialista: {e}")
            return False

    def get_gold_standards(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera exemplos 'Ouro' para injeção em prompts agênticos (Few-Shot).
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Join entre feedback e analise para pegar o conteúdo real
                cursor.execute("""
                    SELECT a.folder_name, a.result_json, f.corrected_conclusion, f.expert_notes
                    FROM expert_feedback f
                    JOIN analyses a ON f.analysis_id = a.id
                    WHERE f.is_gold_standard = TRUE
                    ORDER BY f.created_at DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Erro ao recuperar Gold Standards: {e}")
            return []

    def import_historical_failures(self, failures: List[Dict[str, Any]]) -> bool:
        """Importa falhas do JSON para o banco de dados (Batch Insert)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Limpa anterior para evitar duplicatas em re-importações se desejado
                # cursor.execute("DELETE FROM historical_failures") 
                
                for f in failures:
                    # Garantir que campos que podem ser listas virem strings
                    desc = f.get('Descrição do Problema', '')
                    if isinstance(desc, list): desc = " | ".join(map(str, desc))
                    
                    cause = f.get('Causa Raiz', f.get('Causa', ''))
                    if isinstance(cause, list): cause = " | ".join(map(str, cause))
                    
                    action = f.get('Plano de Ação', '')
                    if isinstance(action, list): action = "\n- ".join([""] + [str(i) for i in action]).strip()
                    
                    cursor.execute("""
                        INSERT INTO historical_failures (area, equipment, subgroup, description, root_cause, action_plan, occurrence_date, metadata_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(f.get('Área', '')), 
                        str(f.get('Equipamento', '')), 
                        str(f.get('Subgrupo', '')),
                        desc, 
                        cause,
                        action, 
                        str(f.get('Ocorrência', '')),
                        json.dumps({k: v for k, v in f.items() if k not in ['Área', 'Equipamento', 'Subgrupo']})
                    ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Erro ao importar falhas históricas: {e}")
            return False

    def search_unified_history(self, area: str, equipment: str, subgroup: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca unificada em:
        1. Falhas Históricas (Humanas)
        2. Análises passadas da IA calibradas (Gold Standards)
        """
        results = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Busca no histórico legado
                cursor.execute("""
                    SELECT 'HUMAN' as source, area, equipment, subgroup, description, root_cause, action_plan, occurrence_date as date
                    FROM historical_failures
                    WHERE LOWER(area) LIKE LOWER(?) AND LOWER(equipment) LIKE LOWER(?) AND LOWER(subgroup) LIKE LOWER(?)
                    LIMIT ?
                """, (f"%{area}%", f"%{equipment}%", f"%{subgroup}%", limit))
                results.extend([dict(row) for row in cursor.fetchall()])
                
                # 2. Busca em análises da IA marcadas como Gold Standard (Memória Evolutiva)
                # Nota: Aqui precisamos dar parse no JSON de resultado salvo
                cursor.execute("""
                    SELECT 'AI_GOLD' as source, a.folder_name as description, f.corrected_conclusion as root_cause, a.timestamp as date
                    FROM expert_feedback f
                    JOIN analyses a ON f.analysis_id = a.id
                    WHERE f.is_gold_standard = TRUE
                    ORDER BY a.timestamp DESC
                    LIMIT 5
                """)
                results.extend([dict(row) for row in cursor.fetchall()])
                
                return results
        except sqlite3.Error as e:
            logger.error(f"Erro na busca unificada: {e}")
            return []
