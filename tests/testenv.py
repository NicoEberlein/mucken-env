import numpy as np
from mucken_env import MuckenEnv
from pettingzoo.test import api_test

from mucken_env.cards.Card import get_unique_id, Card
from mucken_env.cards.enums import Color, Face


def test_pettingzoo_api():
    env = MuckenEnv()
    api_test(env, num_cycles=10, verbose_progress=False)

def test_seeding():
    env0 = MuckenEnv()
    env0.reset(seed=42)
    hand0 = env0.observe("player_0")['hand']

    env1 = MuckenEnv()
    env1.reset(seed=42)
    hand1 = env1.observe("player_0")['hand']

    np.testing.assert_array_equal(hand0, hand1)

def test_invalid_action():
    env = MuckenEnv()
    env.reset(seed=41)

    card_id_first = get_unique_id(Card(Color.BLATT, Face.KOENIG))
    env.step(card_id_first)

    _, _, termination, truncation, _ = env.last()
    assert not (termination or truncation)

    card_id_invalid_step = get_unique_id(Card(Color.EICHEL, Face.UNTER))
    env.step(card_id_invalid_step)

    _, _, termination, truncation, _ = env.last()
    assert termination or truncation


