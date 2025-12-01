# MuckenEnv

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PettingZoo](https://img.shields.io/badge/PettingZoo-AEC-orange)

**MuckenEnv** is a multi-agent reinforcement learning environment for the Bavarian card game "Mucken". It is based on the [PettingZoo](https://pettingzoo.farama.org/) AEC API (Agent Environment Cycle) and is optimized for training AI agents in a game with partial information.

## About the Game (Mucken)

Mucken is a traditional Bavarian card game for 4 people, similar to Schafkopf, but with simplified rules.

* **Players:** 4 agents (`player_0` to `player_3`).
* **Teams:** Fixed partnerships "crosswise" (Player 0 & 2 vs. Player 1 & 3).
* **Cards:** 24 cards (Acorns, Leaves, Hearts, Bells; ranks A, 10, K, O, U, 9).
* **Goal:** The team must collect more points through tricks than the opposing team.
* **Trumps:** Ober, Unter, and all Heart cards.

![Mucken Gameplay Demo](demo.gif)

## Installation

Clone the repository and install it in "editable" mode (recommended for development):

```
git clone https://github.com/NicoEberlein/mucken-env.git
cd mucken-env
pip install -e .
```

Or install it directly from github:

```
pip install git+https://github.com/NicoEberlein/mucken-env.git
```

## Usage (Quickstart)

The environment uses the PettingZoo AEC API, where agents act sequentially (`agent_iter`).
See `game.py` in the examples for a working game loop with random agents.

## Environment Specifications

### Action Space

The Action Space is `Discrete(24)`. Each integer ID corresponds to a specific card.
A mapping of IDs to cards (e.g., `0` = Bells 9) is implemented in the code.

**Important:** The game requires players to **follow suit**. The environment provides an `action_mask` in the observation. Agents *must* use this mask, as playing an invalid card leads to immediate termination of the episode and a negative reward.

### Observation Space

The observation is a `Dict` space containing both raw data and **engineered features** to accelerate training.

> [!NOTE]
> **Work in Progress:** A detailed explanation of the observation space will follow

| Observation                | Shape | Value (low/high) |  |
|----------------------------|------|------------------|-|
| hand                       | (24,) | (0/1)            | |
| action_mask                | (24,) | (0/1)            | |
| current_trick_cards        | (4,) | (-1,23)          | |
| current_trick_lead_color   | (4,) | (0/1)            | |
| current_trick_players      | (4,) | (-1/3)           | |
| current_trick_teams        | (4,) | (-1/1)           | |
| trick_history              | (24,) | (-1/2)           | |
| trumps_already_played      | (1,) | (0/12)           | |
| high_trumps_already_played | (1,) | (0/8)            | |
| color_void_status          | (4,4) | (0/1)            | |
| trump_void_status          | (4,) | (0/1)            | |

<details>
<summary>Click to see detailed descriptions of all observations</summary>

#### Agent information
These are the most relevant features. They are needed for every human- and non-human agent in order to play the game.

##### hand
Binary encoding to tell the agents which card ids they currently have on their hand.

##### action_mask
Binary mask for all legal steps in the current state. Must be considered during whatever card choosing mechanism the agent uses.

##### current_trick_cards
Shows which cards were already played in the current game by other agents.
Each index can either be the `id` of the played card or `-1` if no card has been played yet.

#### Additional trick information

This information is primarily useful for non-human agents.

##### current_trick_lead_color
One-hot encoding to tell the agents what color was the first card of the current trick.
Necessary because the ruleset requires all players to follow suit if possible.
If the first card was a trump, all indices remain `0`.

##### current_trick_players
Indicates which player played which card in the current trick. `-1` if it wasn't the player's turn yet.
**Example:** `[3,0,1,-1]` means that the first card in the current trick was played by `player_3`, the second by `player_0` and the third by `player_1`.
`player_2` has not played yet.

##### current_trick_teams
Same as `current_trick_players` but instead of indicating the player of the card it indicates the team index `0` or `1` in order to clarify the teams to non-human agents.

#### Engineered features

These features add deeper insights in the game and were added to enhance the training of Reinforcement Learning models.

##### trick_history
Indicates which cards have already been played in the current and past tricks.
A card can either be played by the agent's team (`0`), by the enemies' team (`1`) or be unplayed (`-1`).

##### trumps_already_played
A scalar which represents how many trumps have already been played. All trumps are included.

##### high_trumps_already_played
A scalar which represents how many trumps have already been played. Only the high trumps `O` and `U` are included.
In game modes `Wenz` and `Geier` this is identical to `trumps_already_played` 

##### color_void_status
Is a (4,4) array which shows when players are out of a specific color. The rows represent the colors and the columns the players.
The array will be full of `0` initially. The corresponding index will change once a player doesn't add the color the first card of the trick has.

**Example**: The first card played by `player_0` is of color `EICHEL` (and not a trump). `player_1` plays a trump.
`color_void_status[3][1]` is set to `1`

##### trump_void_status
This shows which player is out of trumps and is not able to take the trick with a trump anymore. Initially it will be `[0,0,0,0]`.
As soon as a player adds a non-trump card and the first card of the trick was a trump the corresponding index will change to `1`.

</details>

### Rewards

The environment uses a **hybrid reward system** (dense + sparse) to solve the credit assignment problem:

1.  **Intermediate Rewards:** After each round, the winners of the trick receive points based on the card values (normalized). The losing team receives the negative value (zero-sum).
2.  **Final Reward:** At the end of the game (after 6 rounds), the overall victory is evaluated. The winning team receives a significant bonus (+ game score), the losing team a penalty.

## File Structure

```
mucken-env/
├── mucken_env/
│   ├── cards/           # Card logic and strategies for each game type
│   ├── envs/            # The main Environment class
│   └── ...
├── tests/               # Unit tests for rules and API compliance
├── pyproject.toml       # Dependencies and package config
└── README.md
```

## License

### Code

This project is published under the **MIT License**. See [LICENSE](LICENSE) for details.

### Game Assets (Card Images)

The playing card images used in this project are based on the **XSkat** card set (German/Bavarian pattern).

**Original author:** Gunter Gerhardt, CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0>, via Wikimedia Commons

**Modifications made:**
The original images were converted to PNG format, resized, and renamed to match the technical requirements of the MuckenEnv environment.
