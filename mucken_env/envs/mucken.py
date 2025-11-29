import os
import time
import uuid
from typing import Dict

import numpy as np
from gymnasium import spaces
from gymnasium.utils import seeding
from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector

from mucken_env.cards.Card import ALL_CARDS, get_card_by_id, get_unique_id
from mucken_env.cards.MuckCardStrategy import MuckCardStrategy


class MuckenEnv(AECEnv):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "mucken-v0.1",
        "is_parallelizable": False,
        "render_fps": 2,
    }

    def __init__(self, render_mode=None):

        self.render_mode = render_mode
        self.possible_agents = ["player_0", "player_1", "player_2", "player_3"]

        super().__init__()

        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )

        self.action_spaces = {
            agent: spaces.Discrete(24) for agent in self.possible_agents
        }

        self.observation_spaces = {
            agent: spaces.Dict({
                "hand": spaces.Box(low=0, high=1, shape=(24,), dtype=np.int8),
                "current_trick_cards": spaces.Box(low=-1, high=23, shape=(4,), dtype=np.int8),
                "current_trick_lead_color": spaces.Box(low=0, high=1, shape=(4,), dtype=np.int8),
                "current_trick_players": spaces.Box(low=-1, high=3, shape=(4,), dtype=np.int8),
                "current_trick_teams": spaces.Box(low=-1, high=1, shape=(4,), dtype=np.int8),
                "trick_history": spaces.Box(low=-1, high=2, shape=(24,), dtype=np.int8),
                "trumps_already_played": spaces.Box(low=0, high=12, shape=(1,), dtype=np.int8),
                "high_trumps_already_played": spaces.Box(low=0, high=8, shape=(1,), dtype=np.int8),
                "color_void_status": spaces.Box(low=0, high=1, shape=(4,4), dtype=np.int8),
                "trump_void_status": spaces.Box(low=0, high=1, shape=(4,), dtype=np.int8),
                "action_mask": spaces.Box(low=0, high=1, shape=(24,), dtype=np.int8),
            }) for agent in self.possible_agents
        }

        self.strategy = None
        self.agents = []
        self._agent_selector = None
        self.agent_selection = None
        self.rewards = {}
        self._cumulative_rewards = {}
        self.terminations = {}
        self.truncations = {}
        self.infos = {}

        self.game_state = {}

        partner_indices = {0: 2, 1: 3, 2: 0, 3: 1}

        self.partner_map = {
            self.possible_agents[i]: self.possible_agents[partner_i]
            for i, partner_i in partner_indices.items()
        }

    def reset(self, seed=None, options=None):

        if seed is not None:
            self.np_random, self.np_random_seed = seeding.np_random(seed)

        self.strategy = MuckCardStrategy()
        self.agents = self.possible_agents[:]
        self.rewards = { agent: 0 for agent in self.agents }
        self._cumulative_rewards = { agent: 0 for agent in self.agents }
        self.terminations = { agent: False for agent in self.agents }
        self.truncations = { agent: False for agent in self.agents }

        self.infos = {agent: {
            "round_index": 0,
        } for agent in self.agents}

        self.game_state = self._initialize_game_state(seed=seed)

        for agent in self.agents:
            hand_score = 0
            for card in self.game_state["hands"][agent]:
                hand_score += self.strategy.get_hand_score(card)
            self.infos[agent]["hand_score"] = hand_score/self.strategy.get_max_score()

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

        observation = self.observe(self.agent_selection)
        info = self.infos[self.agent_selection]

        return observation, info


    def step(self, action):

        self._clear_rewards()
        self._cumulative_rewards[self.agent_selection] = 0

        agent_id = self.agent_selection

        if self.terminations[agent_id] or self.truncations[agent_id]:
            self._was_dead_step(action)
            return

        if self.game_state['trick_index'] == 0 and self.game_state['trick_card_history']:
            self.game_state['round_index'] += 1
            for agent in self.agents:
                self.infos[agent]['round_index'] = self.game_state['round_index']

        played_card = get_card_by_id(action)
        first_card = None if len(self.game_state['current_trick']) == 0 else self.game_state['current_trick'][0][1]

        card_permitted = self.strategy.card_permitted(first_card, played_card, self.game_state['hands'][agent_id])
        if card_permitted:

            self._update_void_status(agent_id, played_card, first_card)
            self._apply_action(agent_id, played_card)
            self.agent_selection = self._agent_selector.next()

            if self.game_state['trick_index'] == 4:
                # Round is over
                winner = self._get_winner_of_trick()
                winner_index = self.agent_name_mapping[winner]
                score = self._sum_card_stack()
                self.game_state['player_scores'][winner] += score
                self.game_state['player_scores'][self._get_team_mate(winner)] += score

                if winner == "player_0" or winner == "player_2":
                    self._give_rewards(score/120, (-score)/120)
                else:
                    self._give_rewards((-score) / 120, score / 120)

                self._reset_after_round()

                reordered_agents = self.agents[winner_index:] + self.agents[:winner_index]

                self._agent_selector.reinit(reordered_agents)
                self.agent_selection = self._agent_selector.next()

                #Game is over
                if self.game_state['round_index'] == 5:
                    # Game is over
                    self._calc_final_reward()
                    for agent in self.agents:
                        self.terminations[agent] = True

        else:

            self._agent_invalid_action(agent_id)

    def observe(self, agent):

        # build trick history
        trick_history = np.full((24,), -1, dtype=np.int8)

        for trick in self.game_state['trick_card_history']:
            for played_card in trick:
                # played_card = ("player_0", Card(...))
                agent_index = self.agent_name_mapping[agent]
                played_card_agent_index = self.agent_name_mapping[played_card[0]]
                if agent_index == played_card_agent_index or (agent_index+2)%4 == played_card_agent_index:
                    trick_history[get_unique_id(played_card[1])] = 0
                else:
                    trick_history[get_unique_id(played_card[1])] = 1

        # build action mask
        action_mask = np.full((24,), 0, dtype=np.int8)
        player_hand = self.game_state['hands'][agent]

        # permit all cards that belong to agent's hands
        for card in player_hand:
            card_id = get_unique_id(card)
            action_mask[card_id] = 1

        # forbid all cards that can't be played because of game rules
        for card_id in np.nonzero(action_mask)[0]:
            first_card = None if len(self.game_state['current_trick']) == 0 else self.game_state['current_trick'][0][1]
            player_hand = self.game_state['hands'][agent]
            currently_observed_card = get_card_by_id(card_id)
            action_mask[card_id] = self.strategy.card_permitted(first_card, currently_observed_card, player_hand)

        # forbid all cards that were already played by agent
        condition = (trick_history != -1)
        for card_id in np.where(condition)[0]:
            action_mask[card_id] = 0

        # build hand
        hand = np.full((24,), 0, dtype=np.int8)
        for card in self.game_state['hands'][agent]:
            hand[get_unique_id(card)] = 1

        # build current trick cards
        current_trick_cards = np.full((4,), -1, dtype=np.int8)
        for i, trick_card in enumerate(self.game_state['current_trick']):
            current_trick_cards[i] = get_unique_id(trick_card[1])

        # build current trick players
        current_trick_players = np.full((4,), -1, dtype=np.int8)
        for i, trick_card in enumerate(self.game_state['current_trick']):
            player_index = self.agent_name_mapping[trick_card[0]]
            current_trick_players[i] = player_index

        # build current trick teams
        current_trick_teams = np.full((4,), -1, dtype=np.int8)
        for i, trick_card in enumerate(self.game_state['current_trick']):
            card_player_index = self.agent_name_mapping[trick_card[0]]
            if card_player_index == self.agent_name_mapping[agent] or card_player_index == (self.agent_name_mapping[agent]+2)%4 :
                current_trick_teams[i] = 0
            else:
                current_trick_teams[i] = 1

        # build color of first card of current trick
        current_trick_lead_color = np.full((4,), 0, dtype=np.int8)
        if len(self.game_state['current_trick']) > 0:
            lead_color = self.game_state['current_trick'][0][1].color
            current_trick_lead_color[lead_color.value] = 1


        return {
            'hand': hand,
            'current_trick_cards': current_trick_cards,
            'current_trick_lead_color': current_trick_lead_color,
            'current_trick_players': current_trick_players,
            'current_trick_teams': current_trick_teams,
            'trick_history': trick_history,
            'trumps_already_played': np.array([self.game_state['trumps_already_played']], dtype=np.int8),
            'high_trumps_already_played': np.array([self.game_state['high_trumps_already_played']], dtype=np.int8),
            'color_void_status': self.game_state['color_void_status'],
            'trump_void_status': self.game_state['trump_void_status'],
            'action_mask': action_mask,
        }

    def render(self):
        if self.render_mode != "human":
            return

        if len(self.game_state['current_trick']) == 0 and len(self.game_state['last_completed_trick']) == 0:
            return

        os.system('cls' if os.name == 'nt' else 'clear')

        trick_tuples_to_render = self.game_state.get('last_completed_trick', [])

        if not trick_tuples_to_render:
            trick_tuples_to_render = self.game_state.get('current_trick', [])

        cards_on_table: Dict[str, str] = {
            player_id: str(card) for player_id, card in trick_tuples_to_render
        }

        p0_card = cards_on_table.get('player_0', '(wartet...)').center(18)
        p1_card = cards_on_table.get('player_1', '(wartet...)').center(18)
        p2_card = cards_on_table.get('player_2', '(wartet...)').center(18)
        p3_card = cards_on_table.get('player_3', '(wartet...)').center(18)
        header = f"--- Runde: {self.game_state.get('trick_index', 0) + 1} / 4 ---"

        table_view = f"""
        {header.center(50)}
        +--------------------------------------------------+
        |                                                  |
        |                Spieler 2 (Partner)               |
        |              {p2_card}              |
        |                                                  |
        | Spieler 1 (Gegner)        Spieler 3 (Gegner)     |
        | {p1_card}      {p3_card} |
        |                                                  |
        |                   Spieler 0 (Sie)                  |
        |              {p0_card}              |
        |                                                  |
        +--------------------------------------------------+
        """

        active_player_info = f"--> {self.agent_selection} ist am Zug."

        current_hand_list = self.game_state.get('hands', {}).get(self.agent_selection, [])
        hand_info = "Hand: " + " ".join(str(card) for card in current_hand_list)

        print(table_view)
        print(active_player_info)
        print(hand_info)

        self.game_state['last_completed_trick'] = []

        time.sleep(1)

    def close(self):
        pass

    def _initialize_game_state(self, seed):

        cards = ALL_CARDS[:]
        np.random.seed(seed)
        np.random.shuffle(cards)

        hands = { agent: [] for agent in self.agents }

        for i, card in enumerate(cards):

            player_index = i % 4
            player_id = self.possible_agents[player_index]

            hands[player_id].append(card)

        new_state = {
            "id": str(uuid.uuid4()),
            "round_index": 0,
            "trick_index": 0,
            "hands": hands,
            "player_scores": { agent: 0 for agent in self.possible_agents },
            # trick_card_history: [[("player_0", Card(...))],[],[],[],[],[]]
            "trick_card_history": [],
            # current_trick: [("player_0",Card(...)),...]
            "current_trick": [],
            "last_completed_trick": [],
            "high_trumps_already_played": 0,
            "trumps_already_played": 0,
            "color_void_status": np.full((4,4), 0, dtype=np.int8),
            "trump_void_status": np.full((4,), 0, dtype=np.int8),
            "has_played_mask": { agent: 0 for agent in self.possible_agents },
        }

        return new_state

    def _apply_action(self, agent, action):
        self.game_state['current_trick'].append((agent, action))
        self.game_state['hands'][agent].remove(action)
        self.game_state['trick_index'] += 1
        self.game_state['high_trumps_already_played'] += 1 if self.strategy.is_trump(action, must_be_high=True) else 0
        self.game_state['trumps_already_played'] += 1 if self.strategy.is_trump(action) else 0

    def _reset_after_round(self):

        self.game_state['last_completed_trick'] = self.game_state['current_trick']
        self.game_state['trick_index'] = 0
        self.game_state['trick_card_history'].append(self.game_state['current_trick'])
        self.game_state['current_trick'] = []

    def _agent_invalid_action(self, agent):
        agent_index = self.agent_name_mapping[agent]

        if agent_index % 1 == 0:
            self._give_rewards(1, -1)
        else:
            self._give_rewards(-1, 1)

        self.terminations = { agent: True for agent in self.agents }

    def _calc_final_reward(self):
        first_team_score = self.game_state['player_scores'][self.agents[0]]
        second_team_score = self.game_state['player_scores'][self.agents[1]]

        reward = (first_team_score - second_team_score) / 60

        self._give_rewards(reward, -reward)

    def _give_rewards(self, reward_0, reward_1):

        self.rewards[self.agents[0]] += reward_0
        self.rewards[self.agents[1]] += reward_1
        self.rewards[self.agents[2]] += reward_0
        self.rewards[self.agents[3]] += reward_1

    def _get_winner_of_trick(self):
        current_card_stack = []
        for trick_card in self.game_state['current_trick']:
            current_card_stack.append(trick_card[1])
        highest_card_index = self.strategy.who_won(current_card_stack)
        highest_trick_card = self.game_state['current_trick'][highest_card_index]
        return highest_trick_card[0]

    def _sum_card_stack(self):
        sum_cards = 0
        for trick_card in self.game_state['current_trick']:
            sum_cards += trick_card[1].face.value
        return sum_cards

    def _get_team_mate(self, player_id: str) -> str:
        return self.partner_map[player_id]

    def _update_void_status(self, agent, played_card, first_card):
        if first_card is None:
            return

        if self.strategy.is_trump(first_card) and not self.strategy.is_trump(played_card):
            self.game_state['trump_void_status'][self.agent_name_mapping[agent]] = 1
            return

        if played_card.color != first_card.color:
            # agent doesn't have color if first card on hand
            color_index = first_card.color.value
            self.game_state['color_void_status'][color_index][self.agent_name_mapping[agent]] = 1
            return

