import unittest

from mucken_env.cards.MuckCardStrategy import MuckCardStrategy
from mucken_env.cards.CardFactory import CardFactory
from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Face, Color


class TestMuck(unittest.TestCase):

    def setUp(self):
        self.muck_strategy = MuckCardStrategy()


    def test_who_won_muck(self):

        card_stack_trump_wins = [
            Card(Color.HERZ, Face.NEUN),
            Card(Color.HERZ, Face.OBER),
            Card(Color.BLATT, Face.UNTER),
            Card(Color.EICHEL, Face.OBER)
        ]

        card_stack_color_wins = [
            Card(Color.HERZ, Face.ASS),
            Card(Color.HERZ, Face.ZEHN),
            Card(Color.EICHEL, Face.ASS),
            Card(Color.EICHEL, Face.NEUN)
        ]

        card_stack_unusual_behaviour = [
            Card(Color.HERZ, Face.ASS),
            Card(Color.HERZ, Face.UNTER),
            Card(Color.BLATT, Face.UNTER),
            Card(Color.BLATT, Face.OBER)
        ]

        card_stack_3_cards = [
            Card(Color.SCHELLE, Face.UNTER),
            Card(Color.HERZ, Face.OBER),
            Card(Color.SCHELLE, Face.NEUN)
        ]

        res_trump_wins = self.muck_strategy.who_won(card_stack_trump_wins)
        res_color_wins = self.muck_strategy.who_won(card_stack_color_wins)
        res_unusual_behaviour = self.muck_strategy.who_won(card_stack_unusual_behaviour)
        res_3_cards = self.muck_strategy.who_won(card_stack_3_cards)

        self.assertEqual(res_trump_wins, 3)
        self.assertEqual(res_color_wins, 0)
        self.assertEqual(res_unusual_behaviour, 3)
        self.assertEqual(res_3_cards, 1)

    def test_card_permitted_trump_first_permitted(self):

        card_stack = [
            Card(Color.EICHEL, Face.UNTER),
            Card(Color.EICHEL, Face.OBER),
            Card(Color.HERZ, Face.UNTER)
        ]

        player_stack = [
            Card(Color.BLATT, Face.NEUN),
            Card(Color.HERZ, Face.NEUN),
            Color.HERZ, Face.OBER
        ]

        card_played = Card(Color.HERZ, Face.OBER)

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_stack)

        self.assertEqual(res, True)

    def test_card_permitted_color_first_permitted(self):

        card_stack = CardFactory.produce_card("sa,sz,hz")
        player_stack = CardFactory.produce_card("hu,ho,su,bz")
        card_played = CardFactory.produce_card("bz")

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_stack)

        self.assertEqual(res, True)

    def test_card_permitted_trump_first_forbidden(self):

        card_stack = [
            Card(Color.SCHELLE, Face.OBER),
        ]

        player_hands = [
            Card(Color.BLATT, Face.NEUN),
            Card(Color.HERZ, Face.ZEHN),
            Card(Color.HERZ, Face.OBER),
            Card(Color.SCHELLE, Face.NEUN),
        ]

        card_played = Card(Color.SCHELLE, Face.NEUN)

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_hands)

        self.assertEqual(res, False)

    def test_card_permitted_color_first_forbidden(self):

        card_stack = [
            Card(Color.SCHELLE, Face.KOENIG),
        ]

        player_hands = [
            Card(Color.BLATT, Face.UNTER),
            Card(Color.EICHEL, Face.KOENIG),
            Card(Color.SCHELLE, Face.ZEHN),
            Card(Color.SCHELLE, Face.OBER),
            Card(Color.EICHEL, Face.UNTER),
            Card(Color.HERZ, Face.KOENIG)
        ]

        card_played = Card(Color.SCHELLE, Face.OBER)

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_hands)

        self.assertEqual(res, False)


    def test_compare_muck_trumps(self):
        card0 = Card(Color.HERZ, Face.OBER)
        card1 = Card(Color.HERZ, Face.ZEHN)

        card2 = Card(Color.EICHEL, Face.UNTER)
        card3 = Card(Color.EICHEL, Face.OBER)

        card4 = Card(Color.HERZ, Face.OBER)
        card5 = Card(Color.BLATT, Face.OBER)

        self.assertEqual(self.muck_strategy._compare_muck_trumps(card0, card1) > 0, True)
        self.assertEqual(self.muck_strategy._compare_muck_trumps(card2, card3) > 0, False)
        self.assertEqual(self.muck_strategy._compare_muck_trumps(card4, card5) > 0, False)

if __name__ == '__main__':
    unittest.main()