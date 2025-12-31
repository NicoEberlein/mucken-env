import numpy as np

class RandomAgent:

    def choose_action(self, observation, info):
        p = np.random.rand(24)
        final_p = (p * info['action_mask'])
        return np.argmax(final_p)



