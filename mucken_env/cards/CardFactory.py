from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Color, Face


class CardFactory:

    @staticmethod
    def produce_card(card_type):
        card_type = card_type.lower()
        arr = card_type.split(',')

        card_list = []

        for c in arr:
            color_obj = face_obj = None

            color = c[0]
            face = c[1]

            match color:
                case "e":
                    color_obj = Color.EICHEL
                case "b":
                    color_obj = Color.BLATT
                case "h":
                    color_obj = Color.HERZ
                case "s":
                    color_obj = Color.SCHELLE

            match face:
                case "a":
                    face_obj = Face.ASS
                case "z":
                    face_obj = Face.ZEHN
                case "k":
                    face_obj = Face.KOENIG
                case "o":
                    face_obj = Face.OBER
                case "u":
                    face_obj = Face.UNTER
                case "n":
                    face_obj = Face.NEUN

            card_list.append(Card(color_obj, face_obj))

        return card_list[0] if len(card_list) == 1 else card_list