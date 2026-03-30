"""
Medium AI Agent - Heuristic strategy
Agent with basic tic-tac-toe strategy
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.tictactoe import TicTacToe
import random


class MediumAgent:
    """Medium AI that uses advanced heuristic strategy."""
    
    def __init__(self):
        self.name = "Medium Heuristic AI"
    
    def choose_action(self, game: TicTacToe) -> int:
        """Choose action using advanced heuristic strategy."""
        available_actions = game.get_available_actions()
        if not available_actions:
            raise ValueError("No available actions!")
        
        # 1. Check for immediate win
        for action in available_actions:
            test_game = game.copy()
            test_game.make_move(action)
            if test_game.winner == game.current_player:
                return action
        
        # 2. Check for immediate block (opponent's winning move)
        for action in available_actions:
            test_game = game.copy()
            test_game.current_player = -game.current_player
            test_game.make_move(action)
            if test_game.winner == -game.current_player:
                return action
        
        # 3. Look ahead - check if we can create a fork (two winning paths)
        fork_moves = self._find_fork_opportunities(game, game.current_player)
        if fork_moves:
            return random.choice(fork_moves)
        
        # 4. Block opponent's fork opportunities
        opponent_forks = self._find_fork_opportunities(game, -game.current_player)
        if opponent_forks:
            # If opponent has multiple fork opportunities, take center or create two-in-a-row
            if len(opponent_forks) > 1:
                if 4 in available_actions:
                    return 4
            return random.choice(opponent_forks)
        
        # 5. Take center if available (strategic position)
        if 4 in available_actions:
            return 4
        
        # 6. Counter opponent's corner strategy
        # If opponent is in opposite corner, take a side to prevent fork
        board = game.board
        if board[0] == -game.current_player and board[8] == 0 and 8 in available_actions:
            sides = [1, 3, 5, 7]
            available_sides = [s for s in sides if s in available_actions]
            if available_sides:
                return random.choice(available_sides)
        if board[2] == -game.current_player and board[6] == 0 and 6 in available_actions:
            sides = [1, 3, 5, 7]
            available_sides = [s for s in sides if s in available_actions]
            if available_sides:
                return random.choice(available_sides)
        
        # 7. Prefer corners (strategic positions for winning)
        corners = [0, 2, 6, 8]
        available_corners = [c for c in corners if c in available_actions]
        if available_corners:
            # Prefer corners that align with our existing pieces
            best_corner = self._get_best_corner(game, available_corners)
            if best_corner is not None:
                return best_corner
            return random.choice(available_corners)
        
        # 8. Take sides (less strategic but still valid)
        sides = [1, 3, 5, 7]
        available_sides = [s for s in sides if s in available_actions]
        if available_sides:
            return random.choice(available_sides)
        
        # Fallback to random
        return random.choice(available_actions)
    
    def _find_fork_opportunities(self, game: TicTacToe, player: int) -> list:
        """Find moves that create fork opportunities (two ways to win)."""
        fork_moves = []
        available_actions = game.get_available_actions()
        
        for action in available_actions:
            test_game = game.copy()
            test_game.current_player = player
            test_game.make_move(action)
            
            # Count how many winning moves this creates
            winning_moves = 0
            for next_action in test_game.get_available_actions():
                test_game2 = test_game.copy()
                test_game2.current_player = player
                test_game2.make_move(next_action)
                if test_game2.winner == player:
                    winning_moves += 1
            
            # A fork has at least 2 winning opportunities
            if winning_moves >= 2:
                fork_moves.append(action)
        
        return fork_moves
    
    def _get_best_corner(self, game: TicTacToe, corners: list) -> int:
        """Get the best corner that aligns with existing pieces."""
        board = game.board
        player = game.current_player
        
        # Prioritize corners that form a line with our existing pieces
        for corner in corners:
            # Check if this corner completes a diagonal or row/col with our piece
            if corner == 0:
                if board[1] == player or board[3] == player or board[4] == player:
                    return corner
            elif corner == 2:
                if board[1] == player or board[5] == player or board[4] == player:
                    return corner
            elif corner == 6:
                if board[3] == player or board[7] == player or board[4] == player:
                    return corner
            elif corner == 8:
                if board[5] == player or board[7] == player or board[4] == player:
                    return corner
        
        return None

