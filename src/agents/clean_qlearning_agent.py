"""
Clean tabular Q-learning agent for tic-tac-toe (Sutton & Barto style).

The minimal correct setup, in contrast to UltraAdvancedQLearningAgent:
  * State = raw board tuple from the current player's perspective.
    No symmetry reduction (it would require remapping action indices,
    which the existing implementation forgets to do).
  * Reward = terminal only — +1 win, -1 loss, 0 draw. No shaping.
  * No tactical win/block guard during training. The agent must learn
    "blocking matters" from being punished when it fails to block.
  * No Dyna-Q, no double-Q, no MCTS, no prioritized replay, no experience
    replay. Plain tabular Q-learning with ε-greedy exploration.

Tic-tac-toe has ~5,478 reachable states. With this setup, Q(s,a) provably
converges to Q*(s,a), and the greedy policy plays game-theoretic optimum —
i.e., draws every game against a perfect minimax opponent and never loses
to a random one.

Self-play: a single Q-table is used for both sides. Because the state key
flips the board to the current player's perspective, "X to move" and the
mirror "O to move" map to the same key — sample-efficient and consistent.

Public API matches what an inference layer needs: choose_action(game),
train_episode(game), save(path), load(path), state_count().
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.tictactoe import TicTacToe


StateKey = Tuple[int, ...]


class CleanQLearningAgent:
    """Tabular Q-learning with ε-greedy exploration and terminal-only rewards."""

    def __init__(
        self,
        alpha: float = 0.3,
        alpha_end: float = 0.05,
        gamma: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.02,
        decay_episodes: int = 80_000,
    ) -> None:
        # Hyperparameters
        self.alpha_start = alpha
        self.alpha_end = alpha_end
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.decay_episodes = decay_episodes

        # Tabular Q: state_key (tuple of 9 ints in {-1,0,1}) → 9-vector of Q-values
        self.Q: Dict[StateKey, np.ndarray] = {}

        # Diagnostics
        self.episodes_trained = 0

    # ---------- schedules ----------

    def _progress(self) -> float:
        return min(self.episodes_trained / self.decay_episodes, 1.0)

    def get_epsilon(self) -> float:
        p = self._progress()
        return (1.0 - p) * self.epsilon_start + p * self.epsilon_end

    def get_alpha(self) -> float:
        p = self._progress()
        return (1.0 - p) * self.alpha_start + p * self.alpha_end

    # ---------- state ----------

    @staticmethod
    def state_key(board: List[int], current_player: int) -> StateKey:
        """Board tuple flipped to current player's perspective.

        The current player is always +1 in the key, so X-to-move and
        the mirror O-to-move share the same entry — single Q-table,
        consistent updates from both sides of self-play.
        """
        return tuple(c * current_player for c in board)

    def q_values(self, key: StateKey) -> np.ndarray:
        row = self.Q.get(key)
        if row is None:
            row = np.zeros(9, dtype=np.float32)
            self.Q[key] = row
        return row

    def state_count(self) -> int:
        return len(self.Q)

    # ---------- action selection ----------

    def choose_action(self, game: TicTacToe, greedy: bool = False) -> int:
        """ε-greedy. With greedy=True, ε=0 (used at inference)."""
        actions = game.get_available_actions()
        if not actions:
            raise ValueError("No legal actions")

        epsilon = 0.0 if greedy else self.get_epsilon()
        if random.random() < epsilon:
            return random.choice(actions)

        key = self.state_key(game.board, game.current_player)
        q = self.q_values(key)
        best_v = max(float(q[a]) for a in actions)
        bests = [a for a in actions if float(q[a]) == best_v]
        return random.choice(bests)

    # ---------- training ----------

    def train_episode(self, game: TicTacToe) -> int:
        """One self-play episode. Returns the winner (1, -1, or 0)."""
        game.reset()
        alpha = self.get_alpha()

        # Track each player's last decision: (state_key, action)
        last_state: Dict[int, Optional[StateKey]] = {1: None, -1: None}
        last_action: Dict[int, Optional[int]] = {1: None, -1: None}

        while not game.game_over:
            p = game.current_player
            s = self.state_key(game.board, p)
            a = self.choose_action(game, greedy=False)

            # Mid-game update for player p's previous transition:
            #   target = γ · max_{a'} Q(s, a')   (no immediate reward)
            # Q(s_prev, a_prev) ← Q + α (target - Q)
            if last_state[p] is not None:
                prev_q = self.q_values(last_state[p])
                cur_q = self.q_values(s)
                valid_next = game.get_available_actions()
                max_next = max(float(cur_q[ai]) for ai in valid_next) if valid_next else 0.0
                target = self.gamma * max_next
                prev_q[last_action[p]] += alpha * (target - prev_q[last_action[p]])

            last_state[p] = s
            last_action[p] = a
            game.make_move(a)

        # Terminal: each player's final transition gets the actual outcome.
        winner = game.winner
        for p in (1, -1):
            if last_state[p] is None:
                continue
            if winner == p:
                r = 1.0
            elif winner == -p:
                r = -1.0
            else:
                r = 0.0
            prev_q = self.q_values(last_state[p])
            prev_q[last_action[p]] += alpha * (r - prev_q[last_action[p]])

        self.episodes_trained += 1
        return winner

    # ---------- persistence ----------

    def save(self, path: str) -> None:
        data = {
            "q_table": {
                # Keep keys human-readable: "[1, 0, -1, ...]"
                str(list(k)): v.tolist()
                for k, v in self.Q.items()
            },
            "meta": {
                "episodes_trained": self.episodes_trained,
                "alpha_start": self.alpha_start,
                "alpha_end": self.alpha_end,
                "gamma": self.gamma,
                "epsilon_start": self.epsilon_start,
                "epsilon_end": self.epsilon_end,
                "decay_episodes": self.decay_episodes,
                "agent": "CleanQLearningAgent",
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw = data.get("q_table", data)
        self.Q.clear()
        for k, v in raw.items():
            # "[1, 0, -1, ...]" → tuple
            tup = tuple(int(x) for x in k.strip("[]").split(","))
            self.Q[tup] = np.asarray(v, dtype=np.float32)
        meta = data.get("meta", {})
        self.episodes_trained = int(meta.get("episodes_trained", 0))


if __name__ == "__main__":
    # Tiny smoke test: train a few episodes and ensure choose_action works.
    a = CleanQLearningAgent(decay_episodes=200)
    for _ in range(200):
        a.train_episode(TicTacToe())
    g = TicTacToe()
    print("trained episodes:", a.episodes_trained, "states:", a.state_count())
    print("first move on empty board:", a.choose_action(g, greedy=True))
