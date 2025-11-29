import numpy as np
import pytest
from mucken_env import MuckenEnv
from pettingzoo.test import api_test

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

