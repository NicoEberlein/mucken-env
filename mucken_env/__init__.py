from gymnasium.envs.registration import register
from mucken_env.envs.mucken import MuckenEnv

register(
    id="mucken_env/Mucken-v0",
    entry_point="mucken_env.envs:MuckenEnv"
)