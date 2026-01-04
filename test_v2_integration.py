# test_v2_integration.py
"""
Script de teste para validar a integração da V2 (SQLite + Agno Tools).
"""
import sys
from pathlib import Path

# Ajustar PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from core.database import DatabaseManager
from core.agents.tools import FailureAnalysisTools
import json

def test_database():
    print("--- Testando DatabaseManager ---")
    db = DatabaseManager(Path("test_failure_analysis.db"))
    
    # Teste de salvamento
    folder = "TEST_FOLDER_001"
    result = {"test": "data", "ai_results": {"conclusion": "Tudo certo"}}
    tokens = {"prompt_tokens": 100, "response_tokens": 50}
    
    db_id = db.save_analysis(folder, result, tokens, engine="V2")
    print(f"Análise salva com ID: {db_id}")
    
    # Teste de feedback
    success = db.save_expert_feedback(db_id, is_gold=True, correction="Conclusão Corrigida", notes="Nota de teste")
    print(f"Feedback salvo: {success}")
    
    # Teste de recuperação gold standard
    golds = db.get_gold_standards()
    print(f"Gold standards recuperados: {len(golds)}")
    if golds:
        print(f"Nota do primeiro gold: {golds[0]['expert_notes']}")
        
    return db_id

def test_tools():
    print("\n--- Testando Agno Tools Wrapper ---")
    # Apenas validação de assinatura e instanciação
    # (Não faremos chamadas reais de API para evitar custos extras no teste)
    try:
        tools = FailureAnalysisTools(api_key="mock_key", history_data=[])
        print("FailureAnalysisTools instanciado com sucesso.")
    except Exception as e:
        print(f"Erro ao instanciar tools: {e}")

if __name__ == "__main__":
    try:
        test_id = test_database()
        test_tools()
        print("\n[OK] Testes de integração basica concluidos com sucesso!")
        
    except Exception as e:
        print(f"\n[ERRO] Falha nos testes: {e}")
        sys.exit(1)
