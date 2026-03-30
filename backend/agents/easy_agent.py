"""
Easy AI Agent - Random moves
Simple agent for beginners
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.tictactoe import TicTacToe
import random


class EasyAgent:
    """Easy AI that makes random moves."""
    
    def __init__(self):
        self.name = "Easy Random AI"
    
    def choose_action(self, game: TicTacToe) -> int:
        """Choose a random available action."""
        available_actions = game.get_available_actions()
        if not available_actions:
            raise ValueError("No available actions!")
        return random.choice(available_actions)

