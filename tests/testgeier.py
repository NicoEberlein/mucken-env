import unittest

from mucken_env.cards import GeierCardStrategy
from mucken_env.cards.Card import Card
from mucken_env.cards.enums import Face, Color


class TestGeier(unittest.TestCase):

    def setUp(self):
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


if __name__ == '__main__':
    unittest.main()