import random


class Card:
    # słownik symboli unicode
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}

    def __init__(self, rank, suit):
        # TODO: definicja konstruktora, ma ustawiać pola rangi i koloru.

        pass

    def get_value(self):
        # TODO: definicja metody (ma zwracać kartę w takiej reprezentacji, jak dotychczas, tzn. krotka)
        pass

    def __str__(self):
        # TODO: definicja metody, przydatne do wypisywania karty
        pass


class Deck():

    def __init__(self, *args):
        # TODO: definicja metody, ma tworzyć niepotasowaną talię (jak na poprzednich lab)
        pass

    def __str__(self):
        # TODO: definicja metody, przydatne do wypisywania karty
        pass

    def shuffle(self):
        # TODO: definicja metody, tasowanie
        pass

    def deal(self, players):
        # TODO: definicja metody, otrzymuje listę graczy i rozdaje im karty wywołując na nich metodę take_card z Player
        pass


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

    def get_player_hand(self):
        return tuple(self.__hand_)

    def cards_to_str(self):
        # TODO: definicja metody, zwraca stringa z kartami gracza
        pass

    def hand_rank(self):
        # TODO: definicja metody, zwraca to co mamy na rece, mozliwe kombinacje np. dwie pary
        hands = [[('10', 'h'), ('J', 'h'), ('D', 'h'), ('K', 'h'), ('A', 'h')],  # Przykład: poker królewski        : 10
                 [('A', 'c'), ('A', 's'), ('A', 'h'), ('A', 'd'), ('8', 's')],  # Przykład: kareta                 : 8
                 [('5', 'c'), ('6', 'd'), ('7', 'h'), ('8', 's'), ('9', 'd')],  # Przykład: strit                  : 5
                 [('A', 's'), ('2', 'h'), ('3', 'd'), ('4', 'c'), ('5', 's')],  # Przykład: też strit, (As jako 1) : 5
                 [('2', 'c'), ('2', 'd'), ('5', 'h'), ('9', 's'), ('K', 'd')]  # Przykład: jedna para             : 2
                 ]
        pass
