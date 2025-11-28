from dataclasses import dataclass
from itertools import product

from mucken_env.cards.enums import Color, Face

@dataclass(frozen=True, eq=True)
class Card:

    color: Color
    face: Face

    def __str__(self) -> str:
        color_symbols = {Color.EICHEL: ' Eichel', Color.BLATT: ' Blatt', Color.HERZ: ' Herz', Color.SCHELLE: ' Schelle'}
        return f"[{self.face.name.capitalize()}{color_symbols[self.color]}]"

ORDERED_COLORS = [Color.SCHELLE, Color.HERZ, Color.BLATT, Color.EICHEL]
ORDERED_FACES = [Face.NEUN, Face.UNTER, Face.OBER, Face.KOENIG, Face.ZEHN, Face.ASS]

NUM_FACES = len(Face)
ALL_CARDS = [Card(c, f) for c, f in product(ORDERED_COLORS, ORDERED_FACES)]

CARD_TO_ID = { card: i for i, card in enumerate(ALL_CARDS) }
ID_TO_CARD = { i: card for i, card in enumerate(ALL_CARDS) }

def get_unique_id(card: Card) -> int:
    return CARD_TO_ID[card]

def get_card_by_id(card_id: int) -> Card | None:
    return ID_TO_CARD.get(card_id)
