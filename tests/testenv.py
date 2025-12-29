import numpy as np
from mucken_env import MuckenEnv
from pettingzoo.test import api_test

from mucken_env.cards.Card import get_unique_id, Card
from mucken_env.cards.enums import Color, Face


def test_pettingzoo_api():
    env = MuckenEnv()
    api_test(env, num_cycles=1000, verbose_progress=False)

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

def test_missing_card_player_0():
    env = MuckenEnv()
    env.reset(seed=41)

    env.step(get_unique_id(Card(Color.BLATT, Face.ZEHN)))

    assert env.rewards['player_0'] == -1

    _, _, termination, truncation, _ = env.last()

    assert termination
    
def test_missing_card_player_1():
    env = MuckenEnv()
    env.reset(seed=41)

    env.step(get_unique_id(Card(Color.BLATT, Face.KOENIG)))

    _, _, termination, truncation, _ = env.last()

    assert not (truncation or termination)

    # invalid action
    env.step(get_unique_id(Card(Color.SCHELLE, Face.NEUN)))
    assert env.rewards['player_1'] == -1

    _, _, termination, truncation, _ = env.last()
    assert termination


