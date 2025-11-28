from mucken_env.cards.AbstractCardStrategy import AbstractCardStrategy
from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Face, Color

class MuckCardStrategy(AbstractCardStrategy):

    def _contains_trump(self, cards: list[Card]):
        has_trump = False
        for card in cards:
            if self.is_trump(card):
                has_trump = True
        return has_trump

    def _get_mucken_face_value(self, face:Face):
        if face == Face.OBER:
            return 13
        if face == Face.UNTER:
            return 12
        return face.value

    def _compare_muck_trumps(self, card0, card1):
        if card0.face != card1.face:
            return self._get_mucken_face_value(card0.face) - self._get_mucken_face_value(card1.face)
        else:
            return card0.color.value - card1.color.value

    def is_trump(self, card:Card, must_be_high=False) -> bool:

        if card.face == Face.OBER or card.face == Face.UNTER:
            return True
        if card.color == Color.HERZ and not must_be_high:
            return True
        return False

    def who_won(self, cards:list[Card]) -> int:
        highest_card = 0
        if not self._contains_trump(cards):
            for i, card in enumerate(cards):
                if card.color == cards[0].color:
                    if self._compare_faces(cards[highest_card].face, card.face) < 0:
                        highest_card = i
        else:
            highest_card = -1
            for i, card in enumerate(cards):
                if self.is_trump(card):
                    if highest_card == -1:
                        highest_card = i
                    else:
                        comp = self._compare_muck_trumps(cards[highest_card], card)
                        if comp < 0:
                            highest_card = i
        return highest_card

    def get_hand_score(self, card: Card) -> int:
        if card.face == Face.OBER:
            return 10
        elif card.face == Face.UNTER:
            return 8
        elif card.color == Color.HERZ:
            if card.face == Face.ASS:
                return 6
            elif card.face == Face.ZEHN:
                return 5
            else:
                return 3
        else:
            if card.face == Face.ASS:
                return 2
            elif card.face == Face.ZEHN:
                return 1
            else:
                return 0

    def get_max_score(self) -> int:
        return 4*10+2*8
            

