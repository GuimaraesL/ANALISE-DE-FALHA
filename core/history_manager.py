# core/history_manager.py
"""
Módulo responsável pelo gerenciamento do histórico de falhas (RAG Estágio 1).

Este módulo implementa o primeiro estágio do sistema RAG (Retrieval-Augmented 
Generation), realizando filtragem estruturada no banco de dados de falhas 
históricas com base em Área, Equipamento e Subgrupo.

O banco de dados é armazenado em `extracted_data.json` e contém registros
de falhas passadas extraídos do sistema de análise.
"""
import json
from pathlib import Path
import logging
from typing import Any
from unidecode import unidecode


class HistoryManager:
    """
    Gerenciador de histórico de falhas para RAG Estágio 1.
    
    Esta classe é responsável por:
    1. Carregar o banco de dados de falhas históricas (JSON)
    2. Normalizar texto para comparação robusta (remove acentos, lowercase)
    3. Filtrar falhas por critérios estruturados (Área + Equipamento + Subgrupo)
    
    O objetivo é fornecer uma lista ampla de candidatos para o RAG Estágio 2,
    que fará o refinamento semântico usando IA.
    
    Attributes:
        data_path: Path para o arquivo JSON com histórico de falhas.
        history_data: Lista de dicionários carregados do arquivo JSON.
    
    Example:
        >>> manager = HistoryManager("extracted_data.json")
        >>> falhas = manager.find_related_failures({
        ...     "area": "Laminação",
        ...     "equipment": "Desbobinador",
        ...     "subgroup": "Mandril"
        ... })
        >>> print(f"Encontradas {len(falhas)} falhas relacionadas")
    """
    
    def __init__(self, data_path_or_data: Any = "extracted_data.json"):
        """
        Inicializa o gerenciador de histórico.
        
        Args:
            data_path_or_data: Caminho para o arquivo JSON (str/Path) OU lista de dados direta.
        """
        if isinstance(data_path_or_data, (str, Path)):
            self.data_path = Path(data_path_or_data)
            self.history_data = self._load_data()
        elif isinstance(data_path_or_data, list):
            self.data_path = None
            self.history_data = data_path_or_data
        else:
            self.data_path = None
            self.history_data = []
            
        logging.info(f"Gerenciador de Histórico inicializado com {len(self.history_data)} registros.")

    def get_similar_failures(self, area: str, equipment: str, subgroup: str) -> list:
        """Alias para find_related_failures com argumentos explícitos."""
        return self.find_related_failures({
            "area": area,
            "equipment": equipment,
            "subgroup": subgroup
        })

    def _load_data(self) -> list:
        if not self.data_path.exists():
            logging.warning(f"Arquivo de histórico '{self.data_path}' não encontrado.")
            return []
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erro ao carregar o arquivo de histórico: {e}")
            return []

    def _normalize_text(self, text) -> str:
        """
        Função auxiliar para normalizar o texto: remove acentos,
        converte para minúsculas e remove espaços extras.
        Agora também lida com valores que não são strings.
        """
        if not isinstance(text, str):
            # Converte para string antes de processar para evitar erros
            text = str(text)
        # Ex: "Área de Saída " -> "area de saida"
        return unidecode(text).lower().strip()

    def find_related_failures(self, current_failure_data: dict) -> list:
        """
        Encontra falhas semelhantes no histórico usando uma comparação normalizada
        e as chaves corretas do JSON.
        """
        if not self.history_data:
            return []

        # Normaliza os critérios da falha atual para uma comparação robusta
        # Os nomes das chaves aqui ('area', 'equipment') vêm do ExcelReader,
        # que já os padronizou em inglês. Isso está correto.
        area_atual = self._normalize_text(current_failure_data.get('area'))
        equip_atual = self._normalize_text(current_failure_data.get('equipment'))
        subgrupo_atual = self._normalize_text(current_failure_data.get('subgroup'))
        
        related_failures = []
        for entry in self.history_data:
            # FIX: Usando as chaves EXATAS do seu arquivo JSON.
            area_hist = self._normalize_text(entry.get('Área'))
            equip_hist = self._normalize_text(entry.get('Equipamento'))
            subgrupo_hist = self._normalize_text(entry.get('Subgrupo'))

            if (area_hist == area_atual and
                equip_hist == equip_atual and
                subgrupo_hist == subgrupo_atual):
                related_failures.append(entry)
        
        logging.info(f"Filtro amplo e normalizado encontrou {len(related_failures)} falhas relacionadas para '{area_atual}/{equip_atual}/{subgrupo_atual}'.")
        return related_failures
