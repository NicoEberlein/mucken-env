import numpy as np
from gymnasium import spaces
from pettingzoo.utils import BaseWrapper


class MuckenRLWrapper(BaseWrapper):


    def __init__(self, env):
        super().__init__(env)
        self.observation_spaces = {}

        for agent, space in env.observation_spaces.items():

            flat_dim = 0

            for key, subspace in space.items():
                if key == "action_mask":
                    continue
                flat_dim += np.prod(subspace.shape)

            self.observation_spaces[agent] = spaces.Box(-np.inf, np.inf, shape=(int(flat_dim),), dtype=np.float32)

    def last(self, observe=True):

        obs_dict, reward, termination, truncation, info = self.env.last(observe=observe)

        if observe and obs_dict is not None:
            if "action_mask" in obs_dict:
                info["action_mask"] = obs_dict["action_mask"]

            flat_obs = []
            for key in sorted(obs_dict.keys()):
                if key == "action_mask":
                    continue
                flat_obs.append(obs_dict[key].flatten())

            return np.concatenate(flat_obs).astype(np.float32), reward, termination, truncation, info

        return obs_dict, reward, termination, truncation, info

    def observe(self, agent):

        obs_dict = self.env.observe(agent)
        if obs_dict is None: return None

        flat_list = []
        for key in sorted(obs_dict.keys()):
            if key == "action_mask": continue
            flat_list.append(obs_dict[key].flatten())
        return np.concatenate(flat_list).astype(np.float32)