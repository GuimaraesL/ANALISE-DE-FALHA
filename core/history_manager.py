# core/history_manager.py
import json
from pathlib import Path
import logging
from unidecode import unidecode # Importa a biblioteca para normalização

class HistoryManager:
    def __init__(self, data_path: str = "extracted_data.json"):
        self.data_path = Path(data_path)
        self.history_data = self._load_data()
        logging.info(f"Gerenciador de Histórico inicializado com {len(self.history_data)} registros.")

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
