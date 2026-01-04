# scripts/migrate_json_to_db.py
import json
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path para importar core
sys.path.append(str(Path(__file__).parent.parent))

from core.database import DatabaseManager

def migrate():
    json_path = Path("extracted_data.json")
    if not json_path.exists():
        print(f"Erro: Arquivo {json_path} não encontrado.")
        return

    print(f"Lendo dados de {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total de registros encontrados: {len(data)}")
    
    db = DatabaseManager()
    
    # Criamos um backup simples da tabela caso já exista algo
    # db.import_historical_failures agora faz o insert
    
    success = db.import_historical_failures(data)
    
    if success:
        print("Migração concluída com sucesso! Todos os registros estão no SQLite.")
    else:
        print("Erro durante a migração. Verifique os logs.")

if __name__ == "__main__":
    migrate()
