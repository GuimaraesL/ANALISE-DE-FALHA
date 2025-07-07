# core/config_loader.py
import json
from pathlib import Path

def load_config(config_path: str = "config.json") -> dict:
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file '{config_path}' not found.")
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config
