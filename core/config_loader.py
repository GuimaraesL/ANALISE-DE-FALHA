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
    # Tenta primeiro na pasta config/, depois na raiz
    config_file = Path(config_path)
    if not config_file.exists():
        alt_path = Path("config") / config_path
        if alt_path.exists():
            config_file = alt_path
        else:
            raise FileNotFoundError(f"Config file '{config_path}' not found (checked root and config/ folder).")
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config
