"""
Baseline Agents for Q-Learning Tic-Tac-Toe AI Comparison

Includes simple agents for regression testing and performance comparison.
"""

import random
import numpy as np
from typing import List, Tuple, Dict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.tictactoe import TicTacToe


class RandomAgent:
    """Random agent for baseline comparison."""
    
    def __init__(self):
        self.name = "Random"
    
    def choose_action(self, game: TicTacToe) -> int:
        """Choose a random available action."""
        available_actions = game.get_available_actions()
        if not available_actions:
            raise ValueError("No available actions!")
        return random.choice(available_actions)


class HeuristicAgent:
    """Heuristic agent using basic tic-tac-toe strategy."""
    
    def __init__(self):
        self.name = "Heuristic"
    
    def choose_action(self, game: TicTacToe) -> int:
        """Choose action using heuristic strategy."""
        available_actions = game.get_available_actions()
        if not available_actions:
            raise ValueError("No available actions!")
        
        # Check for immediate win
        for action in available_actions:
            test_game = game.copy()
            test_game.make_move(action)
            if test_game.winner == game.current_player:
                return action
        
        # Check for immediate block
        for action in available_actions:
            test_game = game.copy()
            test_game.current_player = -game.current_player
            test_game.make_move(action)
            if test_game.winner == -game.current_player:
                return action
        
        # Prefer center
        if 4 in available_actions:
            return 4
        
        # Prefer corners
        corners = [0, 2, 6, 8]
        for corner in corners:
            if corner in available_actions:
                return corner
        
        # Random from remaining
        return random.choice(available_actions)


class MinimaxAgent:
    """Perfect minimax agent for comparison."""
    
    def __init__(self):
        self.name = "Minimax"
    
    def evaluate_position(self, game: TicTacToe) -> int:
        """Evaluate current position using minimax."""
        if game.game_over:
            if game.winner == 1:
                return 1
            elif game.winner == -1:
                return -1
            else:
                return 0
        
        available_actions = game.get_available_actions()
        if not available_actions:
            return 0
        
        # Try each possible move
        scores = []
        for action in available_actions:
            test_game = game.copy()
            test_game.make_move(action)
            score = self.evaluate_position(test_game)
            scores.append(score)
        
        # Return best score for current player
        if game.current_player == 1:
            return max(scores)
        else:
            return min(scores)
    
    def choose_action(self, game: TicTacToe) -> int:
        """Choose best action using minimax."""
        available_actions = game.get_available_actions()
        if not available_actions:
            raise ValueError("No available actions!")
        
        best_action = None
        best_score = float('-inf') if game.current_player == 1 else float('inf')
        
        for action in available_actions:
            test_game = game.copy()
            test_game.make_move(action)
            score = self.evaluate_position(test_game)
            
            if game.current_player == 1:  # Maximizing player
                if score > best_score:
                    best_score = score
                    best_action = action
            else:  # Minimizing player
                if score < best_score:
                    best_score = score
                    best_action = action
        
        return best_action


class TournamentHarness:
    """Tournament system for comparing different agents."""
    
    def __init__(self):
        self.results = {}
    
    def play_game(self, agent1, agent2, verbose: bool = False) -> Tuple[int, int]:
        """Play a game between two agents."""
        game = TicTacToe()
        moves = 0
        
        while not game.game_over and moves < 9:
            if game.current_player == 1:
                action = agent1.choose_action(game)
            else:
                action = agent2.choose_action(game)
            
            game.make_move(action)
            moves += 1
            
            if verbose:
                print(f"Move {moves}: Player {game.current_player} plays at {action}")
                game.display_board()
                print()
        
        winner = game.winner
        return winner, moves
    
    def run_tournament(self, agents: List, games_per_match: int = 100) -> Dict:
        """Run a tournament between all agents."""
        print(f"Running tournament with {len(agents)} agents")
        print(f"Games per match: {games_per_match}")
        print("=" * 50)
        
        results = {}
        
        # Initialize results
        for agent in agents:
            results[agent.name] = {
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'total_games': 0
            }
        
        # Play all pairs
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i >= j:  # Avoid duplicate matches
                    continue
                
                print(f"\n{agent1.name} vs {agent2.name}")
                
                agent1_wins = 0
                agent2_wins = 0
                draws = 0
                
                for game_num in range(games_per_match):
                    # Agent1 plays as X (player 1)
                    winner, _ = self.play_game(agent1, agent2)
                    
                    if winner == 1:
                        agent1_wins += 1
                    elif winner == -1:
                        agent2_wins += 1
                    else:
                        draws += 1
                    
                    # Agent2 plays as X (player 1) - swap roles
                    winner, _ = self.play_game(agent2, agent1)
                    
                    if winner == 1:
                        agent2_wins += 1
                    elif winner == -1:
                        agent1_wins += 1
                    else:
                        draws += 1
                
                # Update results
                total_games = games_per_match * 2
                results[agent1.name]['wins'] += agent1_wins
                results[agent1.name]['losses'] += agent2_wins
                results[agent1.name]['draws'] += draws
                results[agent1.name]['total_games'] += total_games
                
                results[agent2.name]['wins'] += agent2_wins
                results[agent2.name]['losses'] += agent1_wins
                results[agent2.name]['draws'] += draws
                results[agent2.name]['total_games'] += total_games
                
                print(f"  {agent1.name}: {agent1_wins} wins, {agent2_wins} losses, {draws} draws")
                print(f"  {agent2.name}: {agent2_wins} wins, {agent1_wins} losses, {draws} draws")
        
        return results
    
    def print_tournament_results(self, results: Dict):
        """Print tournament results in a nice format."""
        print("\nTournament Results:")
        print("=" * 60)
        
        # Sort by win rate
        sorted_agents = sorted(results.items(), 
                             key=lambda x: x[1]['wins'] / max(1, x[1]['total_games']), 
                             reverse=True)
        
        print(f"{'Agent':<15} {'Wins':<8} {'Losses':<8} {'Draws':<8} {'Win Rate':<10}")
        print("-" * 60)
        
        for agent_name, stats in sorted_agents:
            win_rate = stats['wins'] / max(1, stats['total_games']) * 100
            print(f"{agent_name:<15} {stats['wins']:<8} {stats['losses']:<8} "
                  f"{stats['draws']:<8} {win_rate:<10.1f}%")


def main():
    """Test baseline agents."""
    print("Baseline Agents Test")
    print("=" * 30)
    
    # Create agents
    random_agent = RandomAgent()
    heuristic_agent = HeuristicAgent()
    minimax_agent = MinimaxAgent()
    
    agents = [random_agent, heuristic_agent, minimax_agent]
    
    # Run tournament
    tournament = TournamentHarness()
    results = tournament.run_tournament(agents, games_per_match=50)
    tournament.print_tournament_results(results)


if __name__ == "__main__":
    main()
