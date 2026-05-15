import numpy as np
import json
import random
import math
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, deque
import time
import gzip
import pickle
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.tictactoe import TicTacToe


class UltraAdvancedQLearningAgent:
    """Ultra-advanced Q-Learning agent."""
    
    def __init__(self, 
                 alpha_start: float = 0.1,
                 alpha_end: float = 0.01,
                 gamma: float = 0.99,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.001,
                 epsilon_decay_steps: int = 200000,
                 use_double_q: bool = True,
                 use_dyna_q: bool = True,
                 experience_replay_size: int = 10000,
                 prioritized_replay: bool = True):
        """
        Initialize ultra-advanced Q-learning agent.
        """
        self.alpha_start = alpha_start
        self.alpha_end = alpha_end
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_steps = epsilon_decay_steps
        self.use_double_q = use_double_q
        self.use_dyna_q = use_dyna_q
        self.experience_replay_size = experience_replay_size
        self.prioritized_replay = prioritized_replay
        
        # Double Q-tables for stability
        self.q_table_a: Dict[str, np.ndarray] = {}
        self.q_table_b: Dict[str, np.ndarray] = {}
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=experience_replay_size)
        self.experience_priorities = deque(maxlen=experience_replay_size)
        
        # Training statistics
        self.total_steps = 0
        self.episodes_trained = 0
        self.convergence_history = deque(maxlen=1000)
        
        # Analytics
        self.move_patterns = defaultdict(int)
        self.q_value_heatmaps = {}
        self.strategic_preferences = defaultdict(float)
        
    def get_alpha(self) -> float:
        """Calculate current learning rate with exponential decay."""
        if self.total_steps >= self.epsilon_decay_steps:
            return self.alpha_end
        
        decay_factor = self.total_steps / self.epsilon_decay_steps
        return self.alpha_start * (self.alpha_end / self.alpha_start) ** decay_factor
    
    def get_epsilon(self) -> float:
        """Calculate current epsilon with exponential decay."""
        if self.total_steps >= self.epsilon_decay_steps:
            return self.epsilon_end
        
        decay_factor = self.total_steps / self.epsilon_decay_steps
        return self.epsilon_start * (self.epsilon_end / self.epsilon_start) ** decay_factor
    
    def get_q_values(self, state_key: str) -> Tuple[np.ndarray, np.ndarray]:
        """Get Q-values for a state from both tables."""
        if state_key not in self.q_table_a:
            self.q_table_a[state_key] = np.zeros(9, dtype=np.float32)
        if state_key not in self.q_table_b:
            self.q_table_b[state_key] = np.zeros(9, dtype=np.float32)
        return self.q_table_a[state_key], self.q_table_b[state_key]
    
    def get_combined_q_values(self, state_key: str) -> np.ndarray:
        """Get combined Q-values from both tables."""
        q_a, q_b = self.get_q_values(state_key)
        return (q_a + q_b) / 2
    
    def check_immediate_win_or_block(self, game: TicTacToe) -> Optional[int]:
        """Check for immediate win or block opportunities."""
        available_actions = game.get_available_actions()
        
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
        
        return None
    
    def evaluate_ultra_advanced_patterns(self, board: List[int], player: int, move_count: int) -> float:
        """
        Ultra-advanced reward shaping with efficiency penalties and stylistic preferences.
        """
        shaping_reward = 0.0
        
        # Define all possible lines
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        
        # Tactical pattern rewards (enhanced)
        for line in lines:
            values = [board[i] for i in line]
            
            if values.count(player) == 3:
                shaping_reward += 10.0
            elif values.count(player) == 2 and values.count(0) == 1:
                shaping_reward += 2.0
            elif values.count(-player) == 2 and values.count(0) == 1:
                shaping_reward += 1.5
            elif values.count(player) == 1 and values.count(0) == 2:
                shaping_reward += 0.3
        
        # Enhanced position bonuses with stylistic preferences
        if board[4] == player:  # Center control (highest priority)
            shaping_reward += 0.8
        
        # Corner preference (strategic)
        corners = [0, 2, 6, 8]
        corner_count = sum(1 for i in corners if board[i] == player)
        shaping_reward += corner_count * 0.4
        
        # Edge preference (defensive)
        edges = [1, 3, 5, 7]
        edge_count = sum(1 for i in edges if board[i] == player)
        shaping_reward += edge_count * 0.2
        
        # Efficiency penalty (encourage shorter winning sequences)
        if move_count > 5:
            shaping_reward -= 0.1 * (move_count - 5)
        
        # Fork creation bonus (multiple threats)
        fork_count = self._count_forks(board, player)
        shaping_reward += fork_count * 1.0
        
        return shaping_reward
    
    def _count_forks(self, board: List[int], player: int) -> int:
        """Count fork opportunities (multiple winning threats)."""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        
        threats = 0
        for line in lines:
            values = [board[i] for i in line]
            if values.count(player) == 2 and values.count(0) == 1:
                threats += 1
        
        return max(0, threats - 1)  # Fork = 2+ threats
    
    def choose_action_with_mcts_evaluation(self, game: TicTacToe) -> int:
        """
        Choose action using tactical intelligence + ε-greedy + MCTS evaluation.
        """
        available_actions = game.get_available_actions()
        
        if not available_actions:
            raise ValueError("No available actions!")
        
        # Always check for immediate wins/blocks first
        tactical_action = self.check_immediate_win_or_block(game)
        if tactical_action is not None:
            return tactical_action
        
        # MCTS-style evaluation for complex positions
        if len(available_actions) <= 3:  # Late game positions
            return self._mcts_evaluate_action(game, available_actions)
        
        # Standard ε-greedy for early/mid game
        state_key = game.get_state_key()
        epsilon = self.get_epsilon()
        
        if random.random() < epsilon:
            return random.choice(available_actions)
        else:
            q_values = self.get_combined_q_values(state_key)
            available_q_values = {action: q_values[action] for action in available_actions}
            best_action = max(available_q_values, key=available_q_values.get)
            return best_action
    
    def _mcts_evaluate_action(self, game: TicTacToe, available_actions: List[int]) -> int:
        """MCTS-style evaluation for late game positions."""
        action_scores = {}
        
        for action in available_actions:
            score = 0
            # Simulate multiple random games from this position
            for _ in range(10):
                test_game = game.copy()
                test_game.make_move(action)
                
                # Play random game to completion
                while not test_game.game_over and test_game.get_available_actions():
                    random_action = random.choice(test_game.get_available_actions())
                    test_game.make_move(random_action)
                
                # Score based on outcome
                if test_game.winner == game.current_player:
                    score += 1
                elif test_game.winner == 0:
                    score += 0.5
                # Loss gets 0 points
            
            action_scores[action] = score
        
        return max(action_scores, key=action_scores.get)
    
    def choose_action(self, game: TicTacToe) -> int:
        """Main action selection method."""
        return self.choose_action_with_mcts_evaluation(game)
    
    def add_experience(self, state: str, action: int, reward: float, next_state: str, done: bool):
        """Add experience to replay buffer."""
        experience = (state, action, reward, next_state, done)
        self.experience_buffer.append(experience)
        
        # Calculate priority based on TD error
        if self.prioritized_replay:
            q_a, q_b = self.get_q_values(state)
            current_q = (q_a[action] + q_b[action]) / 2
            
            if next_state in self.q_table_a:
                next_q_a = self.q_table_a[next_state]
                next_q_b = self.q_table_b[next_state]
                max_next_q = max(np.max(next_q_a), np.max(next_q_b))
            else:
                max_next_q = 0
            
            td_error = abs(reward + self.gamma * max_next_q - current_q)
            priority = td_error + 1e-6  # Small epsilon to avoid zero priority
            self.experience_priorities.append(priority)
    
    def sample_experience(self, batch_size: int = 32) -> List[Tuple]:
        """Sample experiences from replay buffer."""
        if len(self.experience_buffer) < batch_size:
            return list(self.experience_buffer)
        
        if self.prioritized_replay and len(self.experience_priorities) > 0:
            # Prioritized sampling
            priorities = np.array(self.experience_priorities)
            probabilities = priorities / np.sum(priorities)
            indices = np.random.choice(len(self.experience_buffer), batch_size, p=probabilities)
            return [self.experience_buffer[i] for i in indices]
        else:
            # Random sampling
            return random.sample(list(self.experience_buffer), batch_size)
    
    def update_q_value_with_replay(self, state_key: str, action: int, reward: float, next_state_key: str):
        """Update Q-value using experience replay."""
        alpha = self.get_alpha()
        
        # Randomly choose which table to update
        if random.random() < 0.5:
            q_table_update = self.q_table_a
            q_table_target = self.q_table_b
        else:
            q_table_update = self.q_table_b
            q_table_target = self.q_table_a
        
        # Ensure state exists
        if state_key not in q_table_update:
            q_table_update[state_key] = np.zeros(9, dtype=np.float32)
        q_values = q_table_update[state_key]
        
        # Calculate target Q-value
        if next_state_key in q_table_target:
            next_q_values = q_table_target[next_state_key]
            max_next_q = np.max(next_q_values)
        else:
            max_next_q = 0.0
        
        target = reward + self.gamma * max_next_q
        
        # Q-learning update
        q_values[action] += alpha * (target - q_values[action])
        
        self.total_steps += 1
    
    def update_q_value(self, state_key: str, action: int, reward: float, next_state_key: str):
        """Main Q-value update method."""
        self.update_q_value_with_replay(state_key, action, reward, next_state_key)
        
        # Add to experience buffer
        self.add_experience(state_key, action, reward, next_state_key, False)
        
        # Dyna-Q: Learn from simulated experiences
        if self.use_dyna_q and len(self.experience_buffer) > 100:
            self._dyna_q_update()
    
    def _dyna_q_update(self):
        """Dyna-Q: Learn from simulated experiences."""
        if len(self.experience_buffer) < 10:
            return
        
        # Sample random experiences and replay them
        experiences = self.sample_experience(batch_size=min(10, len(self.experience_buffer)))
        
        for state, action, reward, next_state, done in experiences:
            if not done:
                self.update_q_value_with_replay(state, action, reward, next_state)
    
    def train_episode_with_prioritized_start(self, game: TicTacToe) -> Tuple[int, int]:
        """
        Train agent with prioritized starting positions for faster learning.
        """
        # 30% chance to start from partially filled board
        use_prioritized = (
            random.random() < 0.3 and self.episodes_trained > 1000
        )
        if use_prioritized:
            game = self._create_prioritized_start_position()
        else:
            game.reset()
        self.episodes_trained += 1
        
        moves_made = []
        move_count = 0
        
        while not game.game_over:
            current_state = game.get_state_key()
            current_player = game.current_player
            
            action = self.choose_action(game)
            game.make_move(action)
            move_count += 1
            
            # Enhanced tactical reward with efficiency penalties
            tactical_reward = self.evaluate_ultra_advanced_patterns(game.board, current_player, move_count)
            
            moves_made.append({
                'state': current_state,
                'action': action,
                'player': current_player,
                'next_state': game.get_state_key(),
                'tactical_reward': tactical_reward,
                'move_count': move_count
            })
            
            # Track move patterns for analytics
            self.move_patterns[f"{current_state}_{action}"] += 1
            
            if not game.game_over:
                reward = tactical_reward
                self.update_q_value(current_state, action, reward, game.get_state_key())
        
        # Terminal rewards
        winner = game.winner
        if winner != 0:
            winner_moves = [move for move in moves_made if move['player'] == winner]
            if winner_moves:
                last_winner_move = winner_moves[-1]
                self.update_q_value(
                    last_winner_move['state'],
                    last_winner_move['action'],
                    10.0,
                    last_winner_move['next_state']
                )
            
            loser = -winner
            loser_moves = [move for move in moves_made if move['player'] == loser]
            if loser_moves:
                last_loser_move = loser_moves[-1]
                self.update_q_value(
                    last_loser_move['state'],
                    last_loser_move['action'],
                    -10.0,
                    last_loser_move['next_state']
                )
        else:
            if moves_made:
                last_move = moves_made[-1]
                self.update_q_value(
                    last_move['state'],
                    last_move['action'],
                    1.0,
                    last_move['next_state']
                )
        
        return winner, len(moves_made)
    
    def _create_prioritized_start_position(self) -> TicTacToe:
        """Create partially filled board for faster mid-game learning."""
        game = TicTacToe()
        
        # Randomly place 2-4 pieces
        num_pieces = random.randint(2, 4)
        positions = random.sample(range(9), num_pieces)
        
        for i, pos in enumerate(positions):
            player = 1 if i % 2 == 0 else -1
            game.board[pos] = player
        
        # Ensure valid game state
        if game.check_winner():
            return TicTacToe()  # Return empty board if already won
        
        return game
    
    def train_episode(self, game: TicTacToe) -> Tuple[int, int]:
        """Main training episode method."""
        return self.train_episode_with_prioritized_start(game)
    
    def compress_q_table(self):
        """Compress Q-table by removing duplicate Q-values."""
        compressed_states = {}
        seen_q_values = {}
        
        all_states = set(self.q_table_a.keys()) | set(self.q_table_b.keys())
        
        for state_key in all_states:
            q_a = self.q_table_a.get(state_key, np.zeros(9, dtype=np.float32))
            q_b = self.q_table_b.get(state_key, np.zeros(9, dtype=np.float32))
            combined_q = (q_a + q_b) / 2
            
            # Create hash of Q-values
            q_hash = hash(tuple(combined_q.round(6)))
            
            if q_hash not in seen_q_values:
                seen_q_values[q_hash] = state_key
                compressed_states[state_key] = combined_q.tolist()
        
        print(f"Q-table compression: {len(all_states)} → {len(compressed_states)} states")
        return compressed_states
    
    def generate_q_value_heatmap(self, state_key: str) -> Dict:
        """Generate Q-value heatmap for a state."""
        q_values = self.get_combined_q_values(state_key)
        
        heatmap = {
            'state': state_key,
            'q_values': q_values.tolist(),
            'max_q': float(np.max(q_values)),
            'min_q': float(np.min(q_values)),
            'preferred_actions': [int(i) for i in np.argsort(q_values)[-3:][::-1]]
        }
        
        self.q_value_heatmaps[state_key] = heatmap
        return heatmap
    
    def analyze_strategic_preferences(self) -> Dict:
        """Analyze strategic preferences from Q-values."""
        all_states = set(self.q_table_a.keys()) | set(self.q_table_b.keys())
        
        position_preferences = defaultdict(list)
        
        for state_key in all_states:
            q_values = self.get_combined_q_values(state_key)
            
            # Analyze position preferences
            for pos in range(9):
                if q_values[pos] > 0:
                    position_preferences[pos].append(q_values[pos])
        
        # Calculate average preferences
        strategic_analysis = {}
        for pos, values in position_preferences.items():
            strategic_analysis[f'position_{pos}'] = {
                'average_q': float(np.mean(values)),
                'frequency': len(values),
                'max_q': float(np.max(values))
            }
        
        return strategic_analysis
    
    def save_q_table(self, filename: str, format: str = "auto"):
        """Save Q-tables with compression and analytics."""
        # Determine format based on filename extension or format parameter
        if format == "auto":
            if filename.endswith('.gz'):
                format = "gzip"
            elif filename.endswith('.pkl'):
                format = "pickle"
            else:
                format = "json"
        
        # Compress Q-table
        compressed_q_table = self.compress_q_table()
        
        # Generate analytics
        strategic_preferences = self.analyze_strategic_preferences()
        
        # Create comprehensive save data
        save_data = {
            'q_table': compressed_q_table,
            'analytics': {
                'strategic_preferences': strategic_preferences,
                'move_patterns': dict(self.move_patterns),
                'training_stats': {
                    'episodes_trained': self.episodes_trained,
                    'total_steps': self.total_steps,
                    'final_alpha': float(self.get_alpha()),
                    'final_epsilon': float(self.get_epsilon()),
                    'experience_buffer_size': len(self.experience_buffer)
                }
            }
        }
        
        # Save based on format
        if format == "gzip":
            with gzip.open(filename, 'wt', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
        elif format == "pickle":
            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)
        else:  # json
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
        
        print(f"Ultra-Advanced Q-table saved to {filename} ({format} format)")
        print(f"Compressed states: {len(compressed_q_table):,}")
        print(f"Episodes trained: {self.episodes_trained:,}")
        print(f"Total steps: {self.total_steps:,}")
        print(f"Experience buffer: {len(self.experience_buffer):,}")
        print(f"Final alpha: {self.get_alpha():.6f}")
        print(f"Final epsilon: {self.get_epsilon():.6f}")
    
    def load_q_table(self, filename: str):
        """Load Q-table with analytics from multiple formats."""
        try:
            # Determine format based on filename extension
            if filename.endswith('.gz'):
                with gzip.open(filename, 'rt', encoding='utf-8') as f:
                    save_data = json.load(f)
            elif filename.endswith('.pkl'):
                with open(filename, 'rb') as f:
                    save_data = pickle.load(f)
            else:
                with open(filename, 'r') as f:
                    save_data = json.load(f)
            
            # Load Q-table
            q_table_data = save_data.get('q_table', save_data)  # Backward compatibility
            
            for state_key, q_values in q_table_data.items():
                q_array = np.array(q_values, dtype=np.float32)
                self.q_table_a[state_key] = q_array.copy()
                self.q_table_b[state_key] = q_array.copy()
            
            # Load analytics if available
            if 'analytics' in save_data:
                analytics = save_data['analytics']
                self.move_patterns = defaultdict(int, analytics.get('move_patterns', {}))
                
                training_stats = analytics.get('training_stats', {})
                self.episodes_trained = training_stats.get('episodes_trained', 0)
                self.total_steps = training_stats.get('total_steps', 0)
            
            print(f"Ultra-Advanced Q-table loaded from {filename}")
            print(f"Total states: {len(self.q_table_a):,}")
            
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty Q-table.")
        except Exception as e:
            print(f"Error loading Q-table: {e}")
    
    def get_statistics(self) -> Dict:
        """Get training statistics."""
        all_states = set(self.q_table_a.keys()) | set(self.q_table_b.keys())
        return {
            'total_states': len(all_states),
            'episodes_trained': self.episodes_trained,
            'total_steps': self.total_steps,
            'current_alpha': self.get_alpha(),
            'current_epsilon': self.get_epsilon(),
            'gamma': self.gamma,
            'use_double_q': self.use_double_q,
            'use_dyna_q': self.use_dyna_q,
            'experience_buffer_size': len(self.experience_buffer),
            'move_patterns_count': len(self.move_patterns)
        }


class RandomAgent:
    """Random agent for comparison testing."""
    
    def choose_action(self, game: TicTacToe) -> int:
        """Choose a random available action."""
        available_actions = game.get_available_actions()
        if not available_actions:
            raise ValueError("No available actions!")
        return random.choice(available_actions)


if __name__ == "__main__":
    # Test the ultra-advanced agent
    print("Testing Ultra-Advanced Q-Learning Agent")
    print("=" * 50)
    
    agent = UltraAdvancedQLearningAgent()
    game = TicTacToe()
    
    # Test tactical intelligence
    print("Testing ultra-advanced tactical intelligence:")
    game.reset()
    game.make_move(0)  # X
    game.make_move(3)  # O
    game.make_move(1)  # X
    
    print("Board state:")
    game.display_board()
    
    # Should detect win opportunity
    action = agent.choose_action(game)
    print(f"Chosen action: {action}")
    
    # Test analytics
    print(f"\nAgent statistics: {agent.get_statistics()}")
    
    # Test strategic analysis
    strategic_prefs = agent.analyze_strategic_preferences()
    print(f"Strategic preferences: {len(strategic_prefs)} position analyses")