import random


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

        is_straight = False
        sorted_ranks = sorted(ranks, key=lambda x: ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'].index(x))
        if sorted_ranks == ['2', '3', '4', '5', '6'] or sorted_ranks == ['3', '4', '5', '6', '7']:
            is_straight = True

        rank_count = {rank: ranks.count(rank) for rank in ranks}
        sorted_counts = sorted(rank_count.values(), reverse=True)

        if sorted_counts == [4, 1]:  # Kareta
            return 8
        elif sorted_counts == [3, 2]:  # Full
            return 7
        elif sorted_counts == [3, 1, 1]:  # Trójka
            return 4
        elif sorted_counts == [2, 2, 1]:  # Dwie pary
            return 3
        elif sorted_counts == [2, 1, 1, 1]:  # Para
            return 2
        elif is_straight:  # Strit
            return 5
        else:
            return 0  # Brak układu
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