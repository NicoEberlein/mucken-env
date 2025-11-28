import time

import numpy as np

class Agent:

    def choose_action(self, observation):
        p = np.random.rand(24)
        final_p = (p * observation['action_mask'])
        return np.argmax(final_p)



