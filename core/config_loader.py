# core/config_loader.py
"""
Módulo responsável pelo carregamento de configurações da aplicação.

Este módulo fornece uma função utilitária para carregar configurações
de um arquivo JSON, seguindo o princípio de Fail Fast caso o arquivo
não seja encontrado.
"""
import json
from pathlib import Path


def load_config(config_path: str = "config.json") -> dict:
    """
    Carrega as configurações da aplicação a partir de um arquivo JSON.
    
    Esta função busca o arquivo de configuração no caminho especificado
    e retorna seu conteúdo como um dicionário Python. Segue o princípio
    de Fail Fast, lançando exceção imediatamente se o arquivo não existir.
    
    Args:
        config_path: Caminho para o arquivo de configuração JSON.
            Por padrão, busca 'config.json' na raiz do projeto.
    
    Returns:
        Dicionário contendo as configurações carregadas do arquivo.
        Espera-se que contenha as chaves:
        - gemini_api_key: Chave da API do Google Gemini
        - google_credentials_path: Caminho para credenciais do Vertex AI
    
    Raises:
        FileNotFoundError: Se o arquivo de configuração não for encontrado.
        json.JSONDecodeError: Se o arquivo não for um JSON válido.
    
    Example:
        >>> config = load_config()
        >>> api_key = config.get("gemini_api_key")
    """
    # Define a raiz do projeto relativa a este arquivo (core/config_loader.py -> raiz)
    root_path = Path(__file__).parent.parent
    
    # Ordem de busca: 
    # 1. Pasta config/ (Nova estrutura)
    # 2. Raiz do projeto (Estrutura antiga/fallback)
    # 3. Caminho literal (Caso o usuário passe um path absoluto)
    
    config_file_in_config = root_path / "config" / config_path
    config_file_in_root = root_path / config_path
    config_file_literal = Path(config_path)

    if config_file_in_config.exists():
        config_file = config_file_in_config
    elif config_file_in_root.exists():
        config_file = config_file_in_root
    elif config_file_literal.exists():
        config_file = config_file_literal
    else:
        raise FileNotFoundError(
            f"Arquivo de configuração '{config_path}' não encontrado.\n"
            f"Locais verificados:\n"
            f"- {config_file_in_config}\n"
            f"- {config_file_in_root}\n"
            "Verifique se o arquivo existe e se você está no diretório correto do projeto."
        )
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config
