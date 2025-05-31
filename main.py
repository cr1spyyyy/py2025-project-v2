import random
import json
import datetime
from typing import List, Tuple, Dict, Optional, Callable


# --- Klasa GameLogger ---
class GameLogger:
    def __init__(self, log_file_path="poker_log.txt"):
        self.log_file_path = log_file_path
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Sesja gry rozpoczęta: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        except IOError:
            print(f"Nie można otworzyć pliku logu: {self.log_file_path}")

    def log(self, message: str):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except IOError:
            print(f"Błąd zapisu logu: {log_entry.strip()}")

    def close_session(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] === Sesja gry zakończona ===\n"
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except IOError:
            print(f"Błąd zapisu logu zamknięcia sesji: {log_entry.strip()}")


# --- Klasa Card ---
class Card:
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}
    RANK_ORDER = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13,
                  'A': 14}
    VALUE_TO_RANK_STR = {v: k for k, v in RANK_ORDER.items()}
    def __init__(self, rank: str, suit: str):
        if rank not in Card.RANK_ORDER:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in Card.unicode_dict:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank
        self.suit = suit

    def get_value(self) -> Tuple[str, str]:
        return (self.rank, self.suit)

    def get_rank_value(self) -> int:
        return Card.RANK_ORDER[self.rank]

    def __str__(self) -> str:
        return f"{self.rank}{Card.unicode_dict[self.suit]}"

    def __repr__(self) -> str:
        return self.__str__()

    def __lt__(self, other: 'Card') -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.get_rank_value() < other.get_rank_value()


# --- Klasa Deck ---
class Deck():
    def __init__(self):
        ranks = list(Card.RANK_ORDER.keys())
        suits = list(Card.unicode_dict.keys())
        self.cards: List[Card] = [Card(rank, suit) for suit in suits for rank in ranks]

    def __str__(self) -> str:
        return f"Talia ({len(self.cards)} kart)"

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal_one(self) -> Optional[Card]:
        if self.cards:
            return self.cards.pop(0)
        return None

    def deal(self, players: List['Player'], num_cards: int = 5, logger: Optional[GameLogger] = None):
        if logger: logger.log("Rozpoczęcie rozdawania kart.")
        for _ in range(num_cards):
            for player in players:
                if not player.is_folded and len(player._Player__hand_) < 5:
                    card = self.deal_one()
                    if card:
                        log_msg_card = str(card) if player.is_bot else "kartę"
                        if logger: logger.log(f"Gracz {player.name} otrzymuje {log_msg_card}.")
                        player.take_card(card)
                    else:
                        if logger: logger.log("Talia jest pusta podczas rozdawania.")
                        print("Talia jest pusta!")
                        return
        if logger: logger.log("Zakończono rozdawanie kart.")

    def add_cards_to_bottom(self, discarded_cards: List[Card]):
        self.cards.extend(discarded_cards)


# --- Klasa Player ---
class Player():
    HAND_HIERARCHY = {
        "Wysoka karta": 0, "Para": 1, "Dwie pary": 2, "Trójka": 3,
        "Strit": 4, "Kolor": 5, "Full": 6, "Kareta": 7,
        "Poker": 8, "Poker królewski": 9
    }

    def __init__(self, money: int, name: str = "", is_bot: bool = False):
        self.__stack_ = money
        self.__name_ = name if name else f"Gracz_{random.randint(100, 999)}"
        self.__hand_: List[Card] = []
        self.is_folded: bool = False
        self.current_bet_in_round: int = 0
        self.is_bot: bool = is_bot

    @property
    def name(self) -> str:
        return self.__name_

    @property
    def stack(self) -> int:
        return self.__stack_

    @classmethod
    def create_players(cls, num_players: int, initial_stack: int, human_player_name: str = "Gracz") -> List['Player']:
        player_list: List[Player] = []
        # Pierwszy gracz to człowiek
        player_list.append(cls(money=initial_stack, name=human_player_name, is_bot=False))
        # Pozostali to boty
        for i in range(1, num_players):
            player_list.append(cls(money=initial_stack, name=f"Bot_{i}", is_bot=True))
        return player_list

    def take_card(self, card: Card):
        if len(self.__hand_) < 5:
            self.__hand_.append(card)

    def get_stack_amount(self) -> int:
        return self.__stack_

    def pay_money(self, amount: int) -> int:
        to_pay = min(self.__stack_, amount)
        self.__stack_ -= to_pay
        return to_pay

    def receive_money(self, amount: int):
        self.__stack_ += amount

    def change_card(self, new_card: Card, idx: int) -> Card:
        if 0 <= idx < len(self.__hand_):
            old_card = self.__hand_[idx]
            self.__hand_[idx] = new_card
            return old_card
        raise IndexError(f"Niepoprawny indeks {idx} dla ręki o rozmiarze {len(self.__hand_)}")

    def get_player_hand(self) -> Tuple[Card, ...]:
        return tuple(sorted(self.__hand_, reverse=True))

    def cards_to_str(self, reveal_for_human: bool = False) -> str:
        if not self.__hand_: return "Brak kart"
        if self.is_bot and not reveal_for_human:
            return "?? " * len(self.__hand_)
        return ', '.join(str(card) for card in sorted(self.__hand_, reverse=True))

    def clear_hand(self) -> List[Card]:
        discarded = self.__hand_
        self.__hand_ = []
        self.is_folded = False
        self.current_bet_in_round = 0
        return discarded

    def hand_rank(self) -> Tuple[str, int, List[int]]:
        if len(self.__hand_) != 5:
            return "Niepełna ręka", -1, []

        hand_sorted = sorted(self.__hand_, key=lambda c: c.get_rank_value(), reverse=True)
        values = [card.get_rank_value() for card in hand_sorted]
        suits = [card.suit for card in hand_sorted]

        is_flush = len(set(suits)) == 1
        is_straight = False
        tie_breaker_values_straight = values
        if all(values[i] == values[i + 1] + 1 for i in range(len(values) - 1)):
            is_straight = True
        elif values == [14, 5, 4, 3, 2]:
            is_straight = True
            tie_breaker_values_straight = [5, 4, 3, 2, 1]

        rank_counts: Dict[int, int] = {}
        for r_val in values:
            rank_counts[r_val] = rank_counts.get(r_val, 0) + 1
        sorted_rank_groups = sorted(rank_counts.items(), key=lambda item: (item[1], item[0]), reverse=True)

        final_tie_breakers = values

        if is_flush and is_straight:
            final_tie_breakers = tie_breaker_values_straight
            if values == [14, 13, 12, 11, 10]:
                return "Poker królewski", Player.HAND_HIERARCHY["Poker królewski"], final_tie_breakers
            return "Poker", Player.HAND_HIERARCHY["Poker"], final_tie_breakers
        if sorted_rank_groups[0][1] == 4:
            final_tie_breakers = [g[0] for g in sorted_rank_groups]
            return "Kareta", Player.HAND_HIERARCHY["Kareta"], final_tie_breakers
        if sorted_rank_groups[0][1] == 3 and sorted_rank_groups[1][1] == 2:
            final_tie_breakers = [g[0] for g in sorted_rank_groups]
            return "Full", Player.HAND_HIERARCHY["Full"], final_tie_breakers
        if is_flush:
            return "Kolor", Player.HAND_HIERARCHY["Kolor"], final_tie_breakers
        if is_straight:
            final_tie_breakers = tie_breaker_values_straight
            return "Strit", Player.HAND_HIERARCHY["Strit"], final_tie_breakers
        if sorted_rank_groups[0][1] == 3:
            final_tie_breakers = [g[0] for g in sorted_rank_groups]
            return "Trójka", Player.HAND_HIERARCHY["Trójka"], final_tie_breakers
        if sorted_rank_groups[0][1] == 2 and sorted_rank_groups[1][1] == 2:
            final_tie_breakers = [g[0] for g in sorted_rank_groups]
            return "Dwie pary", Player.HAND_HIERARCHY["Dwie pary"], final_tie_breakers
        if sorted_rank_groups[0][1] == 2:
            final_tie_breakers = [g[0] for g in sorted_rank_groups]
            return "Para", Player.HAND_HIERARCHY["Para"], final_tie_breakers
        return "Wysoka karta", Player.HAND_HIERARCHY["Wysoka karta"], final_tie_breakers

    def __str__(self) -> str:
        return f"{self.name} (Stack: {self.stack}): {self.cards_to_str()}"


# --- Klasa GameEngine ---
class GameEngine:
    def __init__(self, players: List[Player], deck: Deck, small_blind: int, big_blind: int, logger: GameLogger):
        self.players = players
        self.deck = deck
        self.small_blind_amount = small_blind
        self.big_blind_amount = big_blind
        self.pot = 0
        self.dealer_button_idx = -1
        self.current_bet_to_match_in_round = 0
        self.logger = logger

    def _get_active_players_in_game(self) -> List[Player]:
        return [p for p in self.players if p.stack > 0]

    def _get_active_players_in_hand(self) -> List[Player]:
        return [p for p in self.players if not p.is_folded and p.stack >= 0]

    def _find_next_player_idx_with_condition(self, start_idx: int, condition_func: Callable[[Player], bool]) -> int:
        current_idx = start_idx
        for _ in range(len(self.players)):
            if condition_func(self.players[current_idx]):
                return current_idx
            current_idx = (current_idx + 1) % len(self.players)
        return -1

    def _post_blinds(self) -> int:
        self.logger.log("--- Rozpoczęcie stawiania blindów ---")
        print("\n--- Blindy ---")
        num_players_with_stack = len(self._get_active_players_in_game())
        if num_players_with_stack < 2:
            self.logger.log("Za mało graczy do postawienia blindów.")
            print("Za mało graczy do postawienia blindów.")
            return (self.dealer_button_idx + 1) % len(self.players)

        sb_idx = self._find_next_player_idx_with_condition(
            (self.dealer_button_idx + 1) % len(self.players),
            lambda p: p.stack > 0
        )
        if sb_idx == -1:
            self.logger.log("Nie znaleziono gracza do Small Blind.")
            return (self.dealer_button_idx + 1) % len(self.players)

        sb_player = self.players[sb_idx]
        sb_paid = sb_player.pay_money(self.small_blind_amount)
        sb_player.current_bet_in_round += sb_paid
        self.pot += sb_paid
        self.logger.log(f"Gracz {sb_player.name} stawia małą w ciemno: {sb_paid}. Stack: {sb_player.stack}")
        print(f"{sb_player.name} stawia małą w ciemno: {sb_paid}")

        bb_idx = self._find_next_player_idx_with_condition(
            (sb_idx + 1) % len(self.players),
            lambda p: p.stack > 0 and p != sb_player
        )
        if num_players_with_stack == 2:
            bb_idx = self._find_next_player_idx_with_condition(
                (sb_idx + 1) % len(self.players), lambda p: p.stack > 0
            )

        if bb_idx == -1 or bb_idx == sb_idx:
            self.logger.log(
                f"Nie znaleziono gracza do Big Blind lub tylko SB może postawić. Aktualny zakład do wyrównania: {sb_paid}")
            self.current_bet_to_match_in_round = sb_paid
            first_to_act_idx = self._find_next_player_idx_with_condition(
                (sb_idx + 1) % len(self.players), lambda p: not p.is_folded and p.stack > 0
            )
            return first_to_act_idx if first_to_act_idx != -1 else sb_idx

        bb_player = self.players[bb_idx]
        bb_paid = bb_player.pay_money(self.big_blind_amount)
        bb_player.current_bet_in_round += bb_paid
        self.pot += bb_paid
        self.logger.log(f"Gracz {bb_player.name} stawia dużą w ciemno: {bb_paid}. Stack: {bb_player.stack}")
        print(f"{bb_player.name} stawia dużą w ciemno: {bb_paid}")

        self.current_bet_to_match_in_round = max(bb_paid, sb_paid)
        self.logger.log(
            f"Aktualny zakład do wyrównania po blindach: {self.current_bet_to_match_in_round}. Pula: {self.pot}")

        first_to_act_idx = self._find_next_player_idx_with_condition(
            (bb_idx + 1) % len(self.players), lambda p: not p.is_folded and p.stack > 0
        )
        if first_to_act_idx != -1:
            self.logger.log(f"Pierwszy do akcji: {self.players[first_to_act_idx].name}")
        else:
            self.logger.log(f"Brak gracza do pierwszej akcji, prawdopodobnie BB: {self.players[bb_idx].name}")
            first_to_act_idx = bb_idx

        return first_to_act_idx if first_to_act_idx != -1 else bb_idx

    def _get_bot_action(self, bot: Player) -> Tuple[str, int]:
        self.logger.log(
            f"Tura bota: {bot.name}. Stack: {bot.stack}, Karty: {bot.cards_to_str(True)}")
        amount_to_call = self.current_bet_to_match_in_round - bot.current_bet_in_round
        hand_name, hand_value, _ = bot.hand_rank()

        if amount_to_call <= 0:  # Może check/bet
            if hand_value >= Player.HAND_HIERARCHY["Para"]:
                bet_amount = min(self.big_blind_amount * 2, bot.stack)
                if bet_amount > 0:
                    self.logger.log(f"Bot {bot.name} ma {hand_name} i decyduje się postawić {bet_amount}.")
                    return ("bet", bet_amount)
            self.logger.log(f"Bot {bot.name} ma {hand_name} i decyduje się czekać.")
            return ("check", 0)
        else:
            if hand_value >= Player.HAND_HIERARCHY["Dwie pary"] and bot.stack > amount_to_call + self.big_blind_amount:
                raise_total_amount = self.current_bet_to_match_in_round + self.big_blind_amount
                self.logger.log(f"Bot {bot.name} ma {hand_name} i decyduje się przebić do {raise_total_amount}.")
                return ("raise", raise_total_amount)
            elif hand_value >= Player.HAND_HIERARCHY[
                "Para"] and amount_to_call <= bot.stack / 4:
                if amount_to_call <= bot.stack:
                    self.logger.log(f"Bot {bot.name} ma {hand_name} i decyduje się sprawdzić {amount_to_call}.")
                    return ("call", 0)

            if amount_to_call > 0 and (hand_value < Player.HAND_HIERARCHY["Para"] or amount_to_call > bot.stack / 3):
                self.logger.log(
                    f"Bot {bot.name} ma {hand_name} i decyduje się spasować wobec zakładu {amount_to_call}.")
                return ("fold", 0)

            if amount_to_call <= bot.stack:
                self.logger.log(
                    f"Bot {bot.name} (ostateczność) ma {hand_name} i decyduje się sprawdzić {amount_to_call}.")
                return ("call", 0)
            else:
                self.logger.log(f"Bot {bot.name} (ostateczność, brak stacka) ma {hand_name} i decyduje się spasować.")
                return ("fold", 0)

    def prompt_human_action(self, player: Player) -> Tuple[str, int]:
        amount_to_call = self.current_bet_to_match_in_round - player.current_bet_in_round
        self.logger.log(
            f"Tura gracza: {player.name}. Stack: {player.stack}, Do wyrównania: {max(0, amount_to_call)}, Karty: {player.cards_to_str(True)}")  # Gracz widzi swoje karty
        print(f"\n{player.name}, twoja kolej (Stack: {player.stack}, Pula: {self.pot})")
        print(
            f"Do tej pory postawiłeś: {player.current_bet_in_round}. Do wyrównania: {self.current_bet_to_match_in_round}.")
        print(f"Twoje karty: {player.cards_to_str(True)}")

        available_actions = ["fold"]
        if amount_to_call <= 0:
            available_actions.append("check")
        else:
            can_call_amount = min(amount_to_call, player.stack)
            available_actions.append(f"call ({can_call_amount})")

        if player.stack > 0:
            if amount_to_call <= 0:
                available_actions.append("bet")
            elif player.stack > amount_to_call:
                available_actions.append("raise")

        while True:
            action_str = input(f"Akcja ({'/'.join(available_actions)}): ").lower().strip()
            self.logger.log(f"Gracz {player.name} próbuje wykonać akcję: {action_str}")

            if action_str == "fold": return ("fold", 0)
            if action_str == "check" and "check" in available_actions: return ("check", 0)
            if action_str.startswith("call") and any(a.startswith("call") for a in available_actions): return (
            "call", 0)

            if action_str == "bet" and "bet" in available_actions:
                try:
                    bet_amount_str = input(f"Podaj kwotę zakładu (min {self.big_blind_amount}): ")
                    self.logger.log(f"Gracz {player.name} podaje kwotę zakładu: {bet_amount_str}")
                    bet_amount = int(bet_amount_str)
                    if bet_amount < self.big_blind_amount and player.stack > bet_amount:
                        self.logger.log(f"Kwota zakładu {bet_amount} mniejsza niż minimum {self.big_blind_amount}.")
                        print(f"Minimalny zakład to {self.big_blind_amount}.")
                        continue
                    if bet_amount > player.stack:
                        self.logger.log(
                            f"Gracz {player.name} próbuje postawić {bet_amount}, ale ma tylko {player.stack}. Stawia all-in.")
                        print(f"Nie masz tyle żetonów. Stawiasz wszystko: {player.stack}")
                        bet_amount = player.stack
                    return ("bet", bet_amount)
                except ValueError:
                    self.logger.log(f"Gracz {player.name} podał nieprawidłową kwotę zakładu.")
                    print("Nieprawidłowa kwota.")

            if action_str == "raise" and "raise" in available_actions:
                try:
                    raise_by_amount_str = input(f"O ile chcesz podbić (min {self.big_blind_amount})? ")
                    self.logger.log(f"Gracz {player.name} podaje kwotę podbicia o: {raise_by_amount_str}")
                    raise_by_amount = int(raise_by_amount_str)
                    if raise_by_amount < self.big_blind_amount and player.stack > (amount_to_call + raise_by_amount):
                        self.logger.log(
                            f"Kwota podbicia {raise_by_amount} mniejsza niż minimum {self.big_blind_amount}.")
                        print(f"Minimalne podbicie to o {self.big_blind_amount}.")
                        continue

                    total_bet_for_player = self.current_bet_to_match_in_round + raise_by_amount
                    if total_bet_for_player - player.current_bet_in_round > player.stack:
                        self.logger.log(
                            f"Gracz {player.name} próbuje przebić do {total_bet_for_player}, ale ma za mało. Stawia all-in.")
                        print(f"Nie masz tyle żetonów. Przebijasz o wszystko co masz po wyrównaniu.")
                        return ("raise", player.current_bet_in_round + player.stack)

                    return ("raise", total_bet_for_player)
                except ValueError:
                    self.logger.log(f"Gracz {player.name} podał nieprawidłową kwotę podbicia.")
                    print("Nieprawidłowa kwota.")

            self.logger.log(f"Gracz {player.name} wybrał nieprawidłową akcję: {action_str}")
            print("Nieprawidłowa akcja.")

    def _betting_round(self, start_player_idx: int):
        self.logger.log(
            f"--- Rozpoczęcie rundy licytacji. Pula: {self.pot}, Do wyrównania: {self.current_bet_to_match_in_round} ---")
        print(f"\n--- Runda Licytacji ---")

        acting_players_indices = []
        idx = start_player_idx
        for _ in range(len(self.players)):
            player = self.players[idx]
            if not player.is_folded and player.stack >= 0:
                acting_players_indices.append(idx)
            idx = (idx + 1) % len(self.players)

        if not acting_players_indices:
            self.logger.log("Brak graczy do licytacji.")
            print("Brak graczy do licytacji.")
            return

        current_actor_queue_idx = 0

        betting_continues = True
        while betting_continues:
            active_in_hand = self._get_active_players_in_hand()
            if len(active_in_hand) <= 1:
                self.logger.log("Licytacja zakończona - pozostał jeden lub mniej graczy.")
                betting_continues = False
                break

            all_matched_or_folded_or_all_in = True
            player_to_act_this_loop = False

            for p_idx_check in acting_players_indices:
                p_check = self.players[p_idx_check]
                if not p_check.is_folded:
                    if p_check.stack > 0 and p_check.current_bet_in_round < self.current_bet_to_match_in_round:
                        all_matched_or_folded_or_all_in = False
                    if p_check.stack > 0:
                        player_to_act_this_loop = True

            if all_matched_or_folded_or_all_in and not player_to_act_this_loop:
                self.logger.log("Licytacja zakończona - wszyscy wyrównali lub są all-in/spasowani.")
                betting_continues = False
                break

            if current_actor_queue_idx >= len(acting_players_indices):
                all_bets_equal_final_check = True
                for p_final_check in self._get_active_players_in_hand():
                    if p_final_check.stack > 0 and p_final_check.current_bet_in_round < self.current_bet_to_match_in_round:
                        all_bets_equal_final_check = False
                        break

                if all_bets_equal_final_check:
                    self.logger.log("Licytacja zakończona - wszyscy wyrównali po pełnej kolejce.")
                    betting_continues = False
                    break
                else:
                    current_actor_queue_idx = 0
                    new_acting_indices = []
                    first_player_after_last_raiser_or_starter = acting_players_indices[0]

                    idx_rebuild = first_player_after_last_raiser_or_starter
                    for _ in range(len(self.players)):
                        player_rebuild = self.players[idx_rebuild]
                        if not player_rebuild.is_folded and player_rebuild.stack >= 0:
                            new_acting_indices.append(idx_rebuild)
                        idx_rebuild = (idx_rebuild + 1) % len(self.players)

                    acting_players_indices = new_acting_indices
                    if not acting_players_indices:
                        self.logger.log("Brak aktywnych graczy po resecie kolejki licytacji.")
                        betting_continues = False;
                        break

            player_idx = acting_players_indices[current_actor_queue_idx]
            player = self.players[player_idx]

            if player.is_folded or (
                    player.stack == 0 and player.current_bet_in_round >= self.current_bet_to_match_in_round):
                current_actor_queue_idx += 1
                continue
            if player.stack == 0 and player.current_bet_in_round < self.current_bet_to_match_in_round:  # All-in za mniej
                current_actor_queue_idx += 1
                continue

            action, amount = ("", 0)
            if player.is_bot:
                action, amount = self._get_bot_action(player)
            else:
                action, amount = self.prompt_human_action(player)

            # Logika obsługi akcji (taka sama jak poprzednio)
            if action == "fold":
                player.is_folded = True
                self.logger.log(f"Gracz {player.name} spasował. Stack: {player.stack}")
                print(f"{player.name} pasuje.")
            elif action == "check":
                self.logger.log(f"Gracz {player.name} czeka. Stack: {player.stack}")
                print(f"{player.name} czeka.")
            elif action == "call":
                amount_needed_to_call = self.current_bet_to_match_in_round - player.current_bet_in_round
                to_pay = min(amount_needed_to_call, player.stack)
                paid = player.pay_money(to_pay)
                player.current_bet_in_round += paid
                self.pot += paid
                self.logger.log(
                    f"Gracz {player.name} sprawdza, dokładając {paid}. Całkowity zakład w rundzie: {player.current_bet_in_round}. Pula: {self.pot}. Stack: {player.stack}")
                print(f"{player.name} sprawdza, dokładając {paid}.")
            elif action == "bet":
                money_to_add_to_pot = amount - player.current_bet_in_round
                paid = player.pay_money(min(money_to_add_to_pot, player.stack))
                player.current_bet_in_round += paid

                self.pot += paid
                self.current_bet_to_match_in_round = player.current_bet_in_round
                self.logger.log(
                    f"Gracz {player.name} stawia {player.current_bet_in_round} (dokładając {paid}). Pula: {self.pot}. Stack: {player.stack}")
                print(f"{player.name} stawia {player.current_bet_in_round} (dokładając {paid}).")
                # Reset kolejki, bo była agresja
                current_actor_queue_idx = 0
                new_acting_indices = []
                start_check_idx = (player_idx + 1) % len(self.players)
                for i in range(len(self.players)):
                    p_temp_idx = (start_check_idx + i) % len(self.players)
                    if p_temp_idx == player_idx: break
                    p_temp = self.players[p_temp_idx]
                    if not p_temp.is_folded and p_temp.stack >= 0:
                        new_acting_indices.append(p_temp_idx)
                acting_players_indices = new_acting_indices
                if not acting_players_indices: betting_continues = False; continue
            elif action == "raise":
                money_to_add_to_pot = amount - player.current_bet_in_round
                paid = player.pay_money(min(money_to_add_to_pot, player.stack))
                player.current_bet_in_round += paid

                self.pot += paid
                self.current_bet_to_match_in_round = player.current_bet_in_round
                self.logger.log(
                    f"Gracz {player.name} przebija do {player.current_bet_in_round} (dokładając {paid}). Pula: {self.pot}. Stack: {player.stack}")
                print(f"{player.name} przebija do {player.current_bet_in_round} (dokładając {paid}).")
                # Reset kolejki
                current_actor_queue_idx = 0
                new_acting_indices = []
                start_check_idx = (player_idx + 1) % len(self.players)
                for i in range(len(self.players)):
                    p_temp_idx = (start_check_idx + i) % len(self.players)
                    if p_temp_idx == player_idx: break
                    p_temp = self.players[p_temp_idx]
                    if not p_temp.is_folded and p_temp.stack >= 0:
                        new_acting_indices.append(p_temp_idx)
                acting_players_indices = new_acting_indices
                if not acting_players_indices: betting_continues = False; continue

            if betting_continues and action not in ["bet", "raise"]:
                current_actor_queue_idx += 1

        self.logger.log(f"--- Zakończenie rundy licytacji. Pula: {self.pot} ---")

    def _get_bot_exchange_decision(self, bot: Player) -> List[int]:
        """Prosta logika wymiany kart dla bota."""
        self.logger.log(f"Bot {bot.name} decyduje o wymianie. Ręka: {bot.cards_to_str(True)}")
        hand_cards = bot._Player__hand_[:]
        hand_name, hand_value, tie_breakers = bot.hand_rank()

        indices_to_discard = []

        if hand_value >= Player.HAND_HIERARCHY["Trójka"]:
            self.logger.log(f"Bot {bot.name} ma {hand_name}, nie wymienia kart.")
            return []

        if hand_value == Player.HAND_HIERARCHY["Dwie pary"]:
            ranks = [card.get_rank_value() for card in hand_cards]
            rank_counts = {r: ranks.count(r) for r in set(ranks)}
            kicker_rank_val = -1
            for r_val, count in rank_counts.items():
                if count == 1:
                    kicker_rank_val = r_val
                    break
            if kicker_rank_val != -1:
                for i, card in enumerate(hand_cards):
                    if card.get_rank_value() == kicker_rank_val:
                        indices_to_discard.append(i)
                        self.logger.log(f"Bot {bot.name} ma dwie pary, wymienia kickera: {card}")
                        break
            return indices_to_discard

        if hand_value == Player.HAND_HIERARCHY["Para"]:
            pair_rank_val = -1
            ranks = [card.get_rank_value() for card in hand_cards]
            rank_counts = {r: ranks.count(r) for r in set(ranks)}
            for r_val, count in rank_counts.items():
                if count == 2:
                    pair_rank_val = r_val
                    break

            for i, card in enumerate(hand_cards):
                if card.get_rank_value() != pair_rank_val:
                    indices_to_discard.append(i)
            pair_rank_display_str = Card.VALUE_TO_RANK_STR.get(pair_rank_val, 'NIEZNANA') if pair_rank_val != -1 else ''
            self.logger.log(
                f"Bot {bot.name} ma parę {pair_rank_display_str}, wymienia {len(indices_to_discard)} karty.")
            return indices_to_discard

        if len(hand_cards) == 5:
            indexed_hand = list(enumerate(bot._Player__hand_))
            indexed_hand.sort(key=lambda item: item[1].get_rank_value())

            num_to_discard_high_card = min(3, len(indexed_hand))
            for i in range(num_to_discard_high_card):
                original_index = indexed_hand[i][0]
                if original_index not in indices_to_discard:
                    indices_to_discard.append(original_index)

            if indices_to_discard:  # Tylko jeśli faktycznie coś jest do wyrzucenia
                self.logger.log(f"Bot {bot.name} ma wysoką kartę, wymienia {len(indices_to_discard)} karty.")
            return indices_to_discard

        return []

    def _perform_card_exchange_for_player(self, player: Player):
        if player.is_folded: return

        indices_to_replace: List[int] = []
        num_to_exchange = 0

        if player.is_bot:
            indices_to_replace = self._get_bot_exchange_decision(player)
            num_to_exchange = len(indices_to_replace)
            if num_to_exchange > 0:
                print(f"{player.name} wymienia {num_to_exchange} kart.")
            else:
                print(f"{player.name} nie wymienia kart.")
        else:  # Gracz ludzki
            self.logger.log(f"Tura wymiany kart dla gracza {player.name}. Ręka: {player.cards_to_str(True)}")
            print(f"\n{player.name}, twoja ręka: {player.cards_to_str(True)}")
            current_hand_list = player._Player__hand_

            num_exchange_str = input(f"Ile kart chcesz wymienić (0-{len(current_hand_list)}, Enter = 0)? ")
            try:
                num_to_exchange = int(num_exchange_str) if num_exchange_str else 0
                if not 0 <= num_to_exchange <= len(current_hand_list):
                    num_to_exchange = 0
            except ValueError:
                num_to_exchange = 0

            self.logger.log(f"Gracz {player.name} decyduje się wymienić {num_to_exchange} kart.")

            if num_to_exchange == 0:
                print(f"{player.name} nie wymienia kart.")
                return

            print("Twoja obecna ręka (indeksy 0-4):")
            for i, card_obj in enumerate(current_hand_list):
                print(f"  {i}: {card_obj}")

            for i in range(num_to_exchange):
                while True:
                    try:
                        idx_str = input(f"Podaj indeks karty #{i + 1} do wymiany (0-{len(current_hand_list) - 1}): ")
                        idx = int(idx_str)
                        if not 0 <= idx < len(current_hand_list) or idx in indices_to_replace:
                            print("Nieprawidłowy lub powtórzony indeks.")
                            continue
                        indices_to_replace.append(idx)
                        break
                    except ValueError:
                        print("Nieprawidłowy indeks.")
            self.logger.log(f"Gracz {player.name} wymienia karty o indeksach: {indices_to_replace}")

        if num_to_exchange > 0:
            indices_to_replace.sort(reverse=True)
            discarded_cards: List[Card] = []
            for idx_in_hand in indices_to_replace:
                new_card = self.deck.deal_one()
                if new_card:
                    old_card = player.change_card(new_card, idx_in_hand)
                    discarded_cards.append(old_card)
                    self.logger.log(f"Gracz {player.name} wymienił {old_card} na {new_card}.")
                else:
                    self.logger.log(f"Talia pusta podczas wymiany dla gracza {player.name}.")
                    print("Talia jest pusta, nie można dobrać nowych kart.")
                    break
            if discarded_cards: self.deck.add_cards_to_bottom(discarded_cards)

        if not player.is_bot or num_to_exchange > 0:  # Pokaż nową rękę graczowi lub jeśli bot coś wymienił
            self.logger.log(
                f"Gracz {player.name} - nowa ręka: {player.cards_to_str(True if not player.is_bot else False)}")
            print(f"{player.name}, nowa ręka: {player.cards_to_str(True if not player.is_bot else False)}")

    def showdown(self) -> None:
        self.logger.log(f"--- Rozpoczęcie Showdown. Pula: {self.pot} ---")
        print("\n--- Showdown ---")
        active_players = self._get_active_players_in_hand()

        if not active_players:
            self.logger.log("Brak graczy do showdownu (wszyscy spasowali).")
            print("Brak graczy do showdownu (wszyscy spasowali).")
            return

        if len(active_players) == 1:
            winner = active_players[0]
            self.logger.log(
                f"Gracz {winner.name} wygrywa {self.pot} jako jedyny pozostały. Stack: {winner.stack + self.pot}")
            print(f"{winner.name} wygrywa {self.pot} jako jedyny pozostały gracz.")
            winner.receive_money(self.pot)
            self.pot = 0
            return

        print("Odkrywanie kart:")
        player_evals: List[Tuple[Player, Tuple[str, int, List[int]]]] = []
        for player in active_players:
            eval_result = player.hand_rank()
            player_evals.append((player, eval_result))
            self.logger.log(
                f"Showdown: {player.name} ma {eval_result[0]} ({player.cards_to_str(True)}), Tie-breakers: {eval_result[2]}")
            print(f"{player.name}: {player.cards_to_str(True)} -> {eval_result[0]} (Tie: {eval_result[2]})")

        player_evals.sort(key=lambda x: (x[1][1], x[1][2]), reverse=True)

        best_eval = player_evals[0][1]
        winners_data = [pe for pe in player_evals if (pe[1][1], pe[1][2]) == (best_eval[1], best_eval[2])]

        num_winners = len(winners_data)
        if num_winners > 0:
            win_amount_base = self.pot // num_winners
            remainder = self.pot % num_winners
            self.logger.log(f"Zwycięzcy (liczba: {num_winners}):")
            print(f"\nZwycięzca/y puli ({self.pot}):")
            for i, (player_obj, eval_data) in enumerate(winners_data):
                final_win_amount = win_amount_base + (1 if i < remainder else 0)
                player_obj.receive_money(final_win_amount)
                self.logger.log(
                    f"  - {player_obj.name} z {eval_data[0]}, wygrywa {final_win_amount}. Nowy stack: {player_obj.stack}")
                print(f"  - {player_obj.name} z {eval_data[0]}, wygrywa {final_win_amount}")
            self.pot = 0
        else:
            self.logger.log("Błąd: Brak zwycięzcy w showdownie.")
            print("Błąd: Brak zwycięzcy.")
        self.logger.log("--- Zakończenie Showdown ---")

    def play_round(self, round_number: int) -> None:
        self.logger.log(f"====== NOWA RUNDA #{round_number} ======")
        print("\n" + "=" * 10 + f" NOWA RUNDA #{round_number} " + "=" * 10)
        self.pot = 0
        self.current_bet_to_match_in_round = 0
        self.deck = Deck()
        self.logger.log(f"Stworzono nową talię ({len(self.deck.cards)} kart).")
        self.deck.shuffle()
        self.logger.log("Talia została potasowana.")

        for p in self.players:
            discarded = p.clear_hand()
            if discarded: self.logger.log(f"Gracz {p.name} zrzucił karty: {', '.join(map(str, discarded))}")
        self.logger.log("Wyczyszczono ręce graczy.")

        self.dealer_button_idx = (self.dealer_button_idx + 1) % len(self.players)
        actual_dealer_idx_candidate = self.dealer_button_idx
        self.dealer_button_idx = self._find_next_player_idx_with_condition(
            actual_dealer_idx_candidate, lambda p: p.stack > 0
        )
        if self.dealer_button_idx == -1:
            self.dealer_button_idx = actual_dealer_idx_candidate  # Wróć do kandydata

        self.logger.log(f"Dealerem jest: {self.players[self.dealer_button_idx].name}")
        print(f"Dealerem jest: {self.players[self.dealer_button_idx].name}")

        first_to_act_idx = self._post_blinds()

        active_for_blinds = self._get_active_players_in_hand()
        if len(active_for_blinds) < 1:
            self.logger.log("Gra kończy się po blindach, za mało aktywnych graczy lub wszyscy all-in.")
            print("Gra kończy się po blindach (np. wszyscy all-in).")
            self.showdown()
            return
        if len(active_for_blinds) == 1 and self.pot > 0:  # Jeśli został tylko 1 gracz, zgarnia pulę
            self.logger.log(f"Gra kończy się po blindach, {active_for_blinds[0].name} wygrywa pulę {self.pot}.")
            print(f"{active_for_blinds[0].name} wygrywa pulę {self.pot} po blindach.")
            active_for_blinds[0].receive_money(self.pot)
            self.pot = 0
            return

        self.logger.log("--- Rozdawanie kart ---")
        print("\n--- Rozdawanie kart ---")
        self.deck.deal(self.players, 5, self.logger)
        for p in self.players:
            if not p.is_folded:
                # Pokaż karty tylko graczowi ludzkiemu
                if not p.is_bot:
                    print(p)

        if len(self._get_active_players_in_hand()) > 1:
            self._betting_round(start_player_idx=first_to_act_idx)

        active_after_betting = self._get_active_players_in_hand()
        if len(active_after_betting) <= 1:
            self.logger.log("Gra kończy się po licytacji, jeden lub mniej graczy.")
            self.showdown()
            return

        self.logger.log("--- Wymiana Kart ---")
        print("\n--- Wymiana Kart ---")
        exchange_start_idx = self._find_next_player_idx_with_condition(
            (self.dealer_button_idx + 1) % len(self.players),
            lambda p: not p.is_folded and p.stack >= 0
        )
        if exchange_start_idx != -1:
            for i in range(len(self.players)):
                player_to_exchange_idx = (exchange_start_idx + i) % len(self.players)
                player = self.players[player_to_exchange_idx]
                if not player.is_folded and player.stack >= 0:
                    self._perform_card_exchange_for_player(player)

        self.showdown()
        self.logger.log(f"====== KONIEC RUNDY #{round_number} ======")


if __name__ == "__main__":
    game_logger = GameLogger("poker_game_history.txt")
    game_logger.log("Aplikacja Pokera uruchomiona.")

    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        game_logger.log(f"Wczytano konfigurację z config.json: {config}")
    except FileNotFoundError:
        game_logger.log("Nie znaleziono pliku config.json. Używam wartości domyślnych.")
        print("Nie znaleziono pliku config.json. Używam wartości domyślnych.")
        config = {"initial_stack": 1000, "small_blind": 25, "big_blind": 50, "num_players": 2}
    except json.JSONDecodeError:
        game_logger.log("Błąd dekodowania config.json. Używam wartości domyślnych.")
        print("Błąd w pliku config.json. Używam wartości domyślnych.")
        config = {"initial_stack": 1000, "small_blind": 25, "big_blind": 50, "num_players": 2}

    human_name = input("Podaj swoje imię: ") or "Gracz"
    player_list = Player.create_players(
        num_players=config.get("num_players", 2),
        initial_stack=config["initial_stack"],
        human_player_name=human_name
    )
    if config.get("num_players", 2) < 2:
        player_list = Player.create_players(2, config["initial_stack"], human_name)
        game_logger.log(f"Liczba graczy w configu mniejsza niż 2, ustawiono na 2.")

    game_logger.log(
        f"Utworzono {len(player_list)} graczy z początkowym stackiem {config['initial_stack']}. Gracz ludzki: {human_name}")

    game_deck = Deck()

    engine = GameEngine(
        players=player_list,
        deck=game_deck,
        small_blind=config["small_blind"],
        big_blind=config["big_blind"],
        logger=game_logger
    )

    round_num = 0
    while True:
        round_num += 1

        active_for_game = [p for p in engine.players if p.stack > 0]
        if len(active_for_game) < 2:
            game_logger.log("Za mało graczy z żetonami, aby kontynuować grę.")
            print("\nZa mało graczy z żetonami, aby kontynuować grę.")
            if active_for_game:
                game_logger.log(f"Ostateczny zwycięzca: {active_for_game[0].name} ze stosem {active_for_game[0].stack}")
                print(f"Ostateczny zwycięzca: {active_for_game[0].name} ze stosem {active_for_game[0].stack}")
            else:
                game_logger.log("Brak graczy z żetonami na koniec gry.")
                print("Brak graczy z żetonami.")
            break

        engine.play_round(round_num)

        game_logger.log("--- Podsumowanie Stacków po rundzie ---")
        print("\n--- Podsumowanie Stacków ---")
        for p in engine.players:
            game_logger.log(f"Gracz {p.name}: {p.stack}")
            print(f"{p.name}: {p.stack}")

        # Sprawdź, czy gracz ludzki ma jeszcze stack
        human_player_obj = next((p for p in engine.players if not p.is_bot), None)
        if human_player_obj and human_player_obj.stack <= 0:
            print(f"\n{human_player_obj.name}, nie masz już żetonów. Koniec gry dla Ciebie.")
            game_logger.log(f"Gracz ludzki {human_player_obj.name} stracił wszystkie żetony.")
            break

        if input("\nZagrać kolejną rundę? (t/n): ").lower() != 't':
            game_logger.log("Gracz zdecydował się zakończyć grę.")
            break

    game_logger.close_session()
    print("\nKoniec gry!")