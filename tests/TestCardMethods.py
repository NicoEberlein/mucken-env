import unittest

from mucken_env.cards.GeierCardStrategy import GeierCardStrategy
from mucken_env.cards.MuckCardStrategy import MuckCardStrategy
from mucken_env.cards.WenzCardStrategy import WenzCardStrategy
from mucken_env.cards.CardFactory import CardFactory
from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Face, Color


class TestCardMethods(unittest.TestCase):

    def setUp(self):
        self.muck_strategy = MuckCardStrategy()
        self.wenz_strategy = WenzCardStrategy()
        self.geier_strategy = GeierCardStrategy()

    def test_who_won_geier(self):

        card_stack_trump_wins = [
            Card(Color.EICHEL, Face.ZEHN),
            Card(Color.EICHEL, Face.NEUN),
            Card(Color.SCHELLE, Face.OBER),
            Card(Color.BLATT, Face.ZEHN)
        ]

        card_stack_color_wins = [
            Card(Color.SCHELLE, Face.NEUN),
            Card(Color.SCHELLE, Face.ASS),
            Card(Color.BLATT, Face.NEUN),
            Card(Color.EICHEL, Face.ASS)
        ]

        res_trump_wins = self.geier_strategy.who_won(card_stack_trump_wins)
        res_color_wins = self.geier_strategy.who_won(card_stack_color_wins)
        self.assertEqual(res_trump_wins, 2)
        self.assertEqual(res_color_wins, 1)


    def test_who_won_wenz(self):

        card_stack_trump_wins = [
            Card(Color.SCHELLE, Face.UNTER),
            Card(Color.EICHEL, Face.ASS),
            Card(Color.BLATT, Face.ZEHN),
            Card(Color.BLATT, Face.UNTER)
        ]

        card_stack_color_wins = [
            Card(Color.HERZ, Face.NEUN),
            Card(Color.HERZ, Face.OBER),
            Card(Color.HERZ, Face.ZEHN),
            Card(Color.BLATT, Face.KOENIG)
        ]

        res_trump_wins = self.wenz_strategy.who_won(card_stack_trump_wins)
        res_color_wins = self.wenz_strategy.who_won(card_stack_color_wins)
        self.assertEqual(res_trump_wins, 3)
        self.assertEqual(res_color_wins, 2)


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

        res_trump_wins = self.muck_strategy.who_won(card_stack_trump_wins)
        res_color_wins = self.muck_strategy.who_won(card_stack_color_wins)
        res_unusual_behaviour = self.muck_strategy.who_won(card_stack_unusual_behaviour)

        self.assertEqual(res_trump_wins, 3)
        self.assertEqual(res_color_wins, 0)
        self.assertEqual(res_unusual_behaviour, 3)

    def test_card_permitted_trump_first_permitted(self):

        card_stack = CardFactory.produce_card("eu,eo,hu")
        player_stack = CardFactory.produce_card("bn,hn,ho")
        card_played = CardFactory.produce_card("ho")

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_stack)

        self.assertEqual(res, True)

    def test_card_permitted_color_first_permitted(self):

        card_stack = CardFactory.produce_card("sa,sz,hz")
        player_stack = CardFactory.produce_card("hu,ho,su,bz")
        card_played = CardFactory.produce_card("bz")

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_stack)

        self.assertEqual(res, True)

    def test_card_permitted_trump_first_forbidden(self):

        card_stack = CardFactory.produce_card("so,hz")
        player_stack = CardFactory.produce_card("hu,ho,sz,bz")
        card_played = CardFactory.produce_card("bz")

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_stack)

        self.assertEqual(res, False)

    def test_card_permitted_color_first_forbidden(self):

        card_stack = CardFactory.produce_card("sa,hz")
        player_stack = CardFactory.produce_card("hu,ho,sz,bz")
        card_played = CardFactory.produce_card("hu")

        res = self.muck_strategy.card_permitted(card_stack[0], card_played, player_stack)

        self.assertEqual(res, False)


    def test_compare_muck_trumps(self):
        card0 = Card(Color.HERZ, Face.OBER)
        card1 = Card(Color.HERZ, Face.ZEHN)

        self.assertEqual(self.muck_strategy._compare_muck_trumps(card0, card1)>0, True)

if __name__ == '__main__':
    unittest.main()