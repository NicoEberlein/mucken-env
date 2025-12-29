from examples.random_agent import Agent
from mucken_env import MuckenEnv

if __name__ == '__main__':

    env = MuckenEnv(render_mode="human", render_fps=0.25)

    agents = {
        "player_0": Agent(),
        "player_1": Agent(),
        "player_2": Agent(),
        "player_3": Agent(),
    }

    rewards_collected = { agent: 0.0 for agent in agents }

    env.reset()

    for agent_id in env.agent_iter():

        env.render()

        observation, reward, termination, truncation, info = env.last()

        rewards_collected[agent_id] += reward

        action = None

        if not (termination or truncation):
            action = agents[agent_id].choose_action(observation)

        env.step(action)

    print("rewards_collected", rewards_collected)
    env.close()
