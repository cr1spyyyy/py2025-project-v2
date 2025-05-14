import os
import json
from datetime import datetime
from typing import Dict


class SessionManager:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def save_session(self, session: Dict) -> None:
        """Zapisuje stan gry i historię zakończonych rozdań do pliku."""
        game_id = session.get("game_id")
        if not game_id:
            raise ValueError("Brak game_id w danych sesji.")
        file_path = os.path.join(self.data_dir, f'session_{game_id}.json')

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Błąd zapisu sesji: {e}")

    def load_session(self, game_id: str) -> Dict:
        """Ładuje sesję gry z pliku i zwraca strukturę pozwalającą na kontynuację rozgrywki."""
        file_path = os.path.join(self.data_dir, f'session_{game_id}.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Nie znaleziono pliku sesji dla ID: {game_id}")
            return {}
        except IOError as e:
            print(f"Błąd odczytu sesji: {e}")
            return {}

    def append_hand_history(self, game_id: str, hand_data: dict) -> None:
        """Dodaje zakończone rozdanie do historii jako JSON Lines."""
        file_path = os.path.join(self.data_dir, f'session_{game_id}.jsonl')

        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                json.dump(hand_data, f)
                f.write('\n')
        except IOError as e:
            print(f"Błąd zapisu historii rozdania: {e}")
