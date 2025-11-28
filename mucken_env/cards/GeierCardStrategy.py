from mucken_env.cards.AbstractCardStrategy import AbstractCardStrategy
from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Face


class GeierCardStrategy(AbstractCardStrategy):

    def who_won(self, cards: list[Card]) -> int:
        highest_card = 0

        for i in range(1, len(cards)):
            if self.is_trump(cards[highest_card]):
                # First card is trump
                if self.is_trump(cards[i]) and self._compare_colors(cards[highest_card].color, cards[i].color) < 0:
                    highest_card = i
            else:
                # First card isn't trump
                if self.is_trump(cards[i]):
                    highest_card = i
                    continue
                else:
                    if cards[i].color == cards[highest_card].color and self._compare_faces(cards[highest_card].face, cards[i].face) < 0:
                        highest_card = i

        return highest_card

    def is_trump(self, card: Card, must_be_high=False) -> bool:
        if card.face == Face.OBER:
            return True
        return False

    def get_hand_score(self, card: Card) -> int:
        if card.face == Face.OBER:
            return 10
        elif card.face == Face.ASS:
            return 5
        elif card.face == Face.ZEHN:
            return 3
        else:
            return 0

    def get_max_score(self) -> int:
        return 4*10+2*5

