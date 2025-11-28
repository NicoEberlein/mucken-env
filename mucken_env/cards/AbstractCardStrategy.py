from abc import ABC, abstractmethod

from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Color, Face


class AbstractCardStrategy(ABC):

    def _compare_faces(self, face_0: Face, face_1: Face):
        return face_0.value - face_1.value

    def _compare_colors(self, color_0: Color, color_1: Color):
        return color_0.value - color_1.value

    @abstractmethod
    def get_hand_score(self, card: Card) -> int:
        pass

    @abstractmethod
    def get_max_score(self) -> int:
        pass

    @abstractmethod
    def is_trump(self, card: Card, must_be_high=False) -> bool:
        pass

    @abstractmethod
    def who_won(self, cards: list[Card]) -> int:
        pass

    def card_permitted(self, first_card: Card, card_played: Card, player_cards: list[Card]) -> bool:
        if first_card is None:
            return True
        if self.is_trump(first_card) and self.is_trump(card_played):
            return True
        if not self.is_trump(first_card) and self._compare_colors(first_card.color, card_played.color) == 0:
            return True

        permitted = True
        for card in player_cards:
            if self.is_trump(first_card) and self.is_trump(card):
                permitted = False
                break
            if not self.is_trump(first_card) and self._compare_colors(first_card.color, card.color) == 0 and not self.is_trump(card):
                permitted = False
                break
        return permitted

