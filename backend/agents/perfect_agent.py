"""
Perfect Tic-Tac-Toe Agent using Minimax with Alpha-Beta Pruning.

Used by the backend for 'hard' difficulty — plays the game-theoretic optimum,
so the AI can only win or draw, never lose. Tic-tac-toe has ~5,478 reachable
states, so an alpha-beta search from any position finishes in a couple ms.

Mirrors src/agents/perfect_agent.py (PerfectMinimaxAgent) so the backend has
no dependency on the training tree.
"""

import random
from typing import Optional

from core.tictactoe import TicTacToe


class PerfectMinimaxAgent:
    """Optimal play via minimax with alpha-beta pruning. Cannot lose."""

    def __init__(self) -> None:
        self.nodes_evaluated = 0

    def choose_action(self, game: TicTacToe) -> int:
        available = game.get_available_actions()
        if not available:
            raise ValueError("No available actions")

        if len(available) == 1:
            return available[0]

        # Fast paths: immediate win, then immediate block.
        for action in available:
            test = game.copy()
            test.make_move(action)
            if test.winner == game.current_player:
                return action
        for action in available:
            test = game.copy()
            test.current_player = -game.current_player
            test.make_move(action)
            if test.winner == -game.current_player:
                return action

        # Full minimax search. Shuffle so equal-value moves rotate.
        best_action: Optional[int] = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        shuffled = list(available)
        random.shuffle(shuffled)

        for action in shuffled:
            test = game.copy()
            test.make_move(action)
            score = self._minimax(test, 1, alpha, beta, False, game.current_player)
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return best_action if best_action is not None else shuffled[0]

    def _minimax(
        self,
        game: TicTacToe,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        original_player: int,
    ) -> float:
        self.nodes_evaluated += 1

        if game.game_over:
            if game.winner == original_player:
                return 10 - depth  # prefer faster wins
            if game.winner == -original_player:
                return depth - 10  # prefer slower losses
            return 0

        available = game.get_available_actions()
        if not available:
            return 0

        is_max_turn = game.current_player == original_player

        if is_max_turn:
            value = float("-inf")
            for action in available:
                test = game.copy()
                test.make_move(action)
                value = max(value, self._minimax(test, depth + 1, alpha, beta, False, original_player))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float("inf")
            for action in available:
                test = game.copy()
                test.make_move(action)
                value = min(value, self._minimax(test, depth + 1, alpha, beta, True, original_player))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
