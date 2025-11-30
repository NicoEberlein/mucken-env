import unittest

from mucken_env.cards.Card import Card
from mucken_env.cards.WenzCardStrategy import WenzCardStrategy
from mucken_env.cards.enums import Face, Color


class TestWenz(unittest.TestCase):

    def setUp(self):
        self.wenz_strategy = WenzCardStrategy()

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


if __name__ == '__main__':
    unittest.main()