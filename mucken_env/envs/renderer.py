import os
import time
from pathlib import Path
from typing import Dict

import numpy as np

from mucken_env.cards.Card import CARD_TO_ID


class MuckenRenderer:

    def __init__(self, render_mode, render_fps):
        self.render_mode = render_mode
        self.render_fps = render_fps
        self.screen = None
        self.clock = None
        self.window_size = (1000,800)
        self.assets = {}

        self.card_width = 150
        self.card_height = 220

        if self.render_mode == "human":
            import pygame

    def render(self, game_state, agent_selection):

        if self.render_mode == "text":
            self._render_text(game_state, agent_selection)
        elif self.render_mode == "human" or self.render_mode == "rgb_array":
            return self._render_human(game_state, agent_selection)

        return None

    def _render_human(self, game_state, agent_selection):

        import pygame

        if self.screen is None:
            pygame.init()
            if self.render_mode == "human":
                self.screen = pygame.display.set_mode(self.window_size)
                pygame.display.set_caption("MuckenEnv")
            elif self.render_mode == "rgb_array":
                self.screen = pygame.Surface(self.window_size)

            self.clock = pygame.time.Clock()

        pygame.event.pump()

        if len(self.assets) == 0:
            self._load_assets()

        self.screen.fill((34, 139, 34))

        self._draw_table(game_state)
        self._draw_hands(game_state)
        self._draw_info(game_state, agent_selection)

        if self.render_mode == "human":
            pygame.display.flip()
        elif self.render_mode == "rgb_array":
            return np.transpose(np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2))

        self.clock.tick(self.render_fps)

    def _render_text(self, game_state, agent_selection):

        trick_tuples_to_render = game_state.get('last_completed_trick', [])

        if not trick_tuples_to_render:
            trick_tuples_to_render = game_state.get('current_trick', [])

        cards_on_table: Dict[str, str] = {
            player_id: str(card) for player_id, card in trick_tuples_to_render
        }

        p0_card = cards_on_table.get('player_0', '(wartet...)').center(18)
        p1_card = cards_on_table.get('player_1', '(wartet...)').center(18)
        p2_card = cards_on_table.get('player_2', '(wartet...)').center(18)
        p3_card = cards_on_table.get('player_3', '(wartet...)').center(18)
        header = f"--- Runde: {game_state.get('trick_index', 0) + 1} / 4 ---"

        table_view = f"""
        {header.center(50)}
        +--------------------------------------------------+
        |                                                  |
        |                Spieler 2                         |
        |              {p2_card}                           |
        |                                                  |
        | Spieler 1                         Spieler 3      |
        | {p1_card}                         {p3_card}      |
        |                                                  |
        |                   Spieler 0                      |
        |              {p0_card}                           |
        |                                                  |
        +--------------------------------------------------+
        """

        active_player_info = f"--> {agent_selection} ist am Zug."

        current_hand_list = game_state.get('hands', {}).get(agent_selection, [])
        hand_info = "Hand: " + " ".join(str(card) for card in current_hand_list)

        print(table_view)
        print(active_player_info)
        print(hand_info)

        game_state['last_completed_trick'] = []

        if self.render_fps > 0:
            time.sleep(1.0 / self.render_fps)

    def close(self):
        if self.screen is not None:
            import pygame
            pygame.display.quit()
            pygame.quit()
            self.screen = None

    def _draw_info(self, game_state, agent_selection):
        import pygame
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(f"Turn: {agent_selection}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        if game_state['winner_last_round'] is not None:
            text_winner = font.render(f"Winner last round: {game_state['winner_last_round']}", True, (255, 255, 255))
            self.screen.blit(text_winner, (10, 40))

    def _draw_table(self, game_state):

        center_x, center_y = 500, 400
        offset = 60

        pos_map = {
            "player_0": (center_x, center_y + offset),
            "player_1": (center_x - offset, center_y),
            "player_2": (center_x, center_y - offset),
            "player_3": (center_x + offset, center_y),
        }

        trick_to_render = game_state['last_completed_trick'] if game_state['trick_index'] == 0 else game_state['current_trick']

        for player_id, card in trick_to_render:
            card_id = CARD_TO_ID[card]
            img = self.assets.get(card_id)

            if img:

                x, y = pos_map[player_id]
                rect = img.get_rect(center=(x, y))
                self.screen.blit(img, rect)

    def _draw_hands(self, game_state):

        import pygame

        positions = {
            "player_0": {"pos": (500, 720), "angle": 0, "offset": (40, 0)},
            "player_1": {"pos": (80, 400), "angle": -90, "offset": (0, 40)},
            "player_2": {"pos": (500, 80), "angle": 180, "offset": (-40, 0)},
            "player_3": {"pos": (920, 400), "angle": 90, "offset": (0, -40)},
        }

        for agent_id, hand_cards in game_state['hands'].items():
            config = positions.get(agent_id)
            if not config: continue

            num_cards = len(hand_cards)
            center_x, center_y = config["pos"]
            dx, dy = config["offset"]

            start_x = center_x - (dx * (num_cards - 1) / 2)
            start_y = center_y - (dy * (num_cards - 1) / 2)

            for i, card in enumerate(hand_cards):
                card_id = CARD_TO_ID[card]

                img = self.assets.get(card_id)

                if config["angle"] != 0:
                    img = pygame.transform.rotate(img, config["angle"])

                x = start_x + (i * dx) - (img.get_width() // 2)
                y = start_y + (i * dy) - (img.get_width() // 2)

                self.screen.blit(img, (x, y))

    def _load_assets(self):
        import pygame

        assets_dir = _get_assets_path()

        for card_id in range(24):
            filepath = os.path.join(assets_dir, f"{card_id}.png")

            try:
                image = pygame.image.load(filepath)
                image = pygame.transform.smoothscale(image, (self.card_width, self.card_height))
                self.assets[card_id] = image
            except FileNotFoundError:
                fallback = pygame.Surface((self.card_width, self.card_height))
                fallback.fill((255, 0, 0))
                self.assets[card_id] = fallback

def _get_assets_path():
    current_file_path = Path(__file__).resolve()
    package_root = current_file_path.parent.parent
    assets_path = os.path.join(package_root, "assets")
    return assets_path