"""Inference agent backed by the clean tabular Q-learner.

All three difficulties draw from a single trained Q-table (q_table_clean.json).
The greedy policy of a converged clean Q-learner plays the game-theoretic
optimum — same strength as minimax, but O(1) table lookup instead of search.

Difficulty just controls how often we explore (random) vs exploit (optimal):
  * easy   — heavy random, occasional optimal moves
  * medium — mostly optimal, sometimes random (tough but beatable)
  * hard   — always optimal (cannot lose, only draw or win)
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Optional

from agents.clean_qlearning_agent import CleanQLearningAgent
from core.tictactoe import TicTacToe


# How often each level picks a random legal move instead of the optimal one.
EPSILON_BY_DIFFICULTY = {
    "easy": 0.7,    # 70% random, 30% optimal → loses often, very beginner-friendly
    "medium": 0.2,  # 20% random, 80% optimal → tough but human can find wins
    "hard": 0.0,    # always optimal → unbeatable (draws are still possible)
}


class QLearningInferenceAgent:
    """API-friendly wrapper around CleanQLearningAgent for the Flask backend."""

    DEFAULT_TABLE_NAME = "q_table_clean.json"
    LEGACY_TABLE_NAME = "q_table.json"  # accepted as fallback if clean missing

    def __init__(self, q_table_path: Optional[str] = None) -> None:
        self.agent = CleanQLearningAgent()
        self._load_error: Optional[str] = None
        self._path_loaded: Optional[Path] = None

        path = self._resolve_path(q_table_path)
        try:
            self.agent.load(str(path))
            self._path_loaded = path
        except FileNotFoundError:
            self._load_error = f"Q-table not found at {path}"
        except Exception as exc:  # malformed JSON, etc.
            self._load_error = f"Failed to load Q-table at {path}: {exc}"

    # ---------- path resolution ----------

    def _resolve_path(self, explicit: Optional[str]) -> Path:
        """Search order: explicit arg → env var → backend/ → repo root.
        Prefers q_table_clean.json over the legacy q_table.json."""
        if explicit:
            return Path(explicit)

        env_path = os.environ.get("Q_TABLE_PATH")
        if env_path:
            return Path(env_path)

        backend_dir = Path(__file__).resolve().parent.parent  # backend/agents → backend
        repo_root = backend_dir.parent
        search_dirs = [backend_dir, repo_root]
        for name in (self.DEFAULT_TABLE_NAME, self.LEGACY_TABLE_NAME):
            for d in search_dirs:
                p = d / name
                if p.is_file():
                    return p
        # Final fallback (likely doesn't exist — surfaced as load_error)
        return repo_root / self.DEFAULT_TABLE_NAME

    # ---------- diagnostics (used by /api/health) ----------

    @property
    def load_error(self) -> Optional[str]:
        return self._load_error

    def is_ready(self) -> bool:
        return self.agent.state_count() > 0

    def state_count(self) -> int:
        return self.agent.state_count()

    @property
    def loaded_path(self) -> Optional[str]:
        return str(self._path_loaded) if self._path_loaded else None

    # ---------- move selection ----------

    def choose_move(self, game: TicTacToe, difficulty: str) -> int:
        difficulty = (difficulty or "hard").lower()
        actions = game.get_available_actions()
        if not actions:
            raise ValueError("No legal moves")

        epsilon = EPSILON_BY_DIFFICULTY.get(difficulty, 0.0)

        # Explore with probability ε — random legal move, no Q-table lookup.
        if epsilon and random.random() < epsilon:
            return random.choice(actions)

        # Exploit: greedy from the trained clean Q-table. If the table didn't
        # load, fall back to a random legal move so the API still responds.
        if self.agent.state_count() == 0:
            return random.choice(actions)
        return self.agent.choose_action(game, greedy=True)
