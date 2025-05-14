import random
import datetime
from typing import List
class Card:
    # słownik symboli unicode
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}

    def __init__(self, rank, suit):
        # TODO: definicja konstruktora, ma ustawiać pola rangi i koloru.
        self.rank = rank
        self.suit = suit

    def get_value(self):
        # TODO: definicja metody (ma zwracać kartę w takiej reprezentacji, jak dotychczas, tzn. krotka)
        return(self.rank, self.suit)

    def __str__(self):
        # TODO: definicja metody, przydatne do wypisywania karty
        return f"{self.rank}{Card.unicode_dict[self.suit]}"


class Deck():

    def __init__(self, *args):
        # TODO: definicja metody, ma tworzyć niepotasowaną talię (jak na poprzednich lab)
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['s', 'h', 'd', 'c']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]

    def __str__(self):
        # TODO: definicja metody, przydatne do wypisywania karty
        return ', '.join(str(card) for card in self.cards)
    def shuffle(self):
        # TODO: definicja metody, tasowanie
        random.shuffle(self.cards)

    def deal(self, players):
        # TODO: definicja metody, otrzymuje listę graczy i rozdaje im karty wywołując na nich metodę take_card z Player
        while self.cards:
            for player in players:
                if self.cards:
                    player.take_card(self.cards.pop())


class Player():

    def __init__(self, money, name=""):
        self.__stack_ = money
        self.__name_ = name
        self.__hand_ = []

    def take_card(self, card):
        self.__hand_.append(card)

    def get_stack_amount(self):
        return self.__stack_

    def change_card(self, card, idx):
        # TODO: przyjmuje nową kartę, wstawia ją za kartę o indeksie idx, zwraca kartę wymienioną
        old_card = self.__hand_[idx]
        self.__hand_[idx] = card
        return old_card
    def get_player_hand(self):
        return tuple(self.__hand_)

    def cards_to_str(self):
        # TODO: definicja metody, zwraca stringa z kartami gracza
        return ', '.join(str(card) for card in self.__hand_)

    def hand_rank(self):
        # TODO: definicja metody, zwraca to co mamy na rece, mozliwe kombinacje np. dwie pary
        ranks = [card.rank for card in self.__hand_]
        suits = [card.suit for card in self.__hand_]

        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5,
                       '6': 6, '7': 7, '8': 8, '9': 9,
                       '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

        values = sorted([rank_values[rank] for rank in ranks])
        is_flush = len(set(suits)) == 1

        # Sprawdzenie strita
        is_straight = (
            all(values[i] == values[i - 1] + 1 for i in range(1, 5)) or
            values == [2, 3, 4, 5, 14]
        )

        rank_count = {rank: ranks.count(rank) for rank in ranks}
        sorted_counts = sorted(rank_count.values(), reverse=True)

        # Układy
        if is_flush and sorted(values) == [10, 11, 12, 13, 14]:
            return "Poker królewski"
        if is_flush and is_straight:
            return "Poker"
        if sorted_counts == [4, 1]:
            return "Kareta"
        if sorted_counts == [3, 2]:
            return "Full"
        if is_flush:
            return "Kolor"
        if is_straight:
            return "Strit"
        if sorted_counts == [3, 1, 1]:
            return "Trójka"
        if sorted_counts == [2, 2, 1]:
            return "Dwie pary"
        if sorted_counts == [2, 1, 1, 1]:
            return "Para"

        return "Wysoka karta"

    def __str__(self):
        return f"{self.__name_}: {self.cards_to_str()}"




class GameEngine:
    def __init__(self, players: List[Player], deck: Deck,
                 small_blind: int = 25, big_blind: int = 50):
        """Inicjalizuje graczy, talię, blindy i pulę."""

    def play_round(self) -> None:
        """Przeprowadza jedną rundę:
           1. Pobiera blindy
           2. Rozdaje karty
           3. Rundę zakładów
           4. Wymianę kart
           5. Showdown i przyznanie puli
        """

    def prompt_bet(self, player: Player, current_bet: int) -> str:
        """Pobiera akcję od gracza (human lub bot) — check/call/raise/fold."""

    def exchange_cards(self, hand: List[Card], indices: List[int]) -> List[Card]:
        """Wymienia wskazane karty z ręki gracza, wkłada stare na spód talii."""

    def showdown(self) -> Player:
        """Porównuje układy pozostałych graczy i zwraca zwycięzcę."""

    def exchange_cards(self,
                       hand: List[Card],
                       indices: List[int]
                       ) -> List[Card]:
        """
        hand     – 5 kart gracza
        indices  – lista indeksów (0–4) do wymiany
        Zwraca: nową listę 5 kart.
        Stare karty odkłada na spód talii.
        """

    def end_round_and_save(self, game_id: str, session_manager: SessionManager):
        hand_data = {
            "game_id": game_id,
            "timestamp": datetime.now().isoformat(),
            "stage": "showdown",
            "players": [
                {"id": i + 1, "name": p._Player__name_, "stack": p.get_stack_amount()}
                for i, p in enumerate(self.players)
            ],
            "deck": [str(card) for card in self.deck.cards],
            "hands": {
                str(i + 1): [str(c) for c in p.get_player_hand()]
                for i, p in enumerate(self.players)
            },
            "bets": self.bets,
            "current_player": self.current_player_id,
            "pot": self.pot,
            "hand_ranks": {
                str(i + 1): p.hand_rank() for i, p in enumerate(self.players)
            },
            "winner_id": self.winner_id
        }

        session_manager.append_hand_history(game_id, hand_data)
