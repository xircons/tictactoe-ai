"""
Ultra-Advanced Self-Play Training Loop

Creative Commons Attribution-NonCommercial 4.0 International License
Copyright (c) 2025 pppwtk

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/4.0/
"""

import time
import numpy as np
import multiprocessing as mp
from typing import Dict, List, Tuple
import json
import yaml
import random
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.tictactoe import TicTacToe
from agents.qlearning_agent import UltraAdvancedQLearningAgent


class UltraAdvancedSelfPlayTrainer:
    
    def __init__(self, 
                 episodes: int = 50000,
                 save_interval: int = 50000,
                 stats_interval: int = 10000,
                 q_table_file: str = "q_table.json",
                 use_parallel: bool = True,
                 max_workers: int = None,
                 early_stopping: bool = True,
                 convergence_threshold: float = 0.02):

        self.episodes = episodes
        self.save_interval = save_interval
        self.stats_interval = stats_interval
        self.q_table_file = q_table_file
        self.use_parallel = use_parallel
        self.max_workers = max_workers or mp.cpu_count()
        self.early_stopping = early_stopping
        self.convergence_threshold = convergence_threshold
        
        # Create ultra-advanced Q-learning agent
        self.agent = UltraAdvancedQLearningAgent(
            alpha_start=0.1,
            alpha_end=0.01,
            gamma=0.99,
            epsilon_start=1.0,
            epsilon_end=0.001,
            epsilon_decay_steps=200000,
            use_double_q=True,
            use_dyna_q=True,
            experience_replay_size=20000,
            prioritized_replay=True
        )
        
        # Training statistics
        self.win_counts = {'player_1': 0, 'player_2': 0, 'draw': 0}
        self.episode_lengths = []
        self.stats_history = []
        self.convergence_metrics = []
        
        # Performance tracking
        self.training_start_time = None
        self.episodes_per_second = 0
        self.peak_performance = 0
        
        # Logging setup
        self.setup_logging()
        
        # Performance metrics for plotting
        self.td_errors = []
        self.epsilon_history = []
        self.alpha_history = []
        self.win_rate_history = []
        self.draw_rate_history = []
        
    def train_episode_parallel(self, episode_id: int) -> Tuple[int, int, int]:
        """Train a single episode (for parallel processing)."""
        game = TicTacToe()
        winner, episode_length = self.agent.train_episode(game)
        return episode_id, winner, episode_length
    
    def train_parallel_batch(self, episode_batch: List[int]) -> List[Tuple[int, int, int]]:
        """Train a batch of episodes on the main process (Q-table must stay shared)."""
        return [self.train_episode_parallel(ep_id) for ep_id in episode_batch]
    
    def setup_logging(self):
        """Setup logging for training metrics."""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Setup logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/training_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Training started - Log file: {log_file}")
    
    def log_training_metrics(self, episode: int, stats: Dict):
        """Log training metrics."""
        self.logger.info(f"Episode {episode}: Win rates - P1: {stats['p1_win_rate']:.1f}%, "
                        f"P2: {stats['p2_win_rate']:.1f}%, Draw: {stats['draw_rate']:.1f}%")
        self.logger.info(f"Episode {episode}: Epsilon: {stats['epsilon']:.4f}, "
                        f"Alpha: {stats['alpha']:.4f}, States: {stats['total_states']}")
        
        # Store metrics for plotting
        self.epsilon_history.append(stats['epsilon'])
        self.alpha_history.append(stats['alpha'])
        self.win_rate_history.append(stats['p1_win_rate'])
        self.draw_rate_history.append(stats['draw_rate'])
    
    def generate_performance_plots(self):
        """Generate performance plots."""
        if not self.epsilon_history:
            return
        
        # Create plots directory
        os.makedirs('plots', exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Training Performance Metrics', fontsize=16)
        
        episodes = list(range(len(self.epsilon_history)))
        
        # Epsilon decay
        axes[0, 0].plot(episodes, self.epsilon_history, 'b-', linewidth=2)
        axes[0, 0].set_title('Epsilon Decay')
        axes[0, 0].set_xlabel('Episodes')
        axes[0, 0].set_ylabel('Epsilon')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Alpha decay
        axes[0, 1].plot(episodes, self.alpha_history, 'r-', linewidth=2)
        axes[0, 1].set_title('Learning Rate Decay')
        axes[0, 1].set_xlabel('Episodes')
        axes[0, 1].set_ylabel('Alpha')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Win rates
        axes[1, 0].plot(episodes, self.win_rate_history, 'g-', linewidth=2, label='Player 1')
        axes[1, 0].plot(episodes, [100 - w - d for w, d in zip(self.win_rate_history, self.draw_rate_history)], 
                       'orange', linewidth=2, label='Player 2')
        axes[1, 0].set_title('Win Rates')
        axes[1, 0].set_xlabel('Episodes')
        axes[1, 0].set_ylabel('Win Rate (%)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Draw rate
        axes[1, 1].plot(episodes, self.draw_rate_history, 'purple', linewidth=2)
        axes[1, 1].set_title('Draw Rate')
        axes[1, 1].set_xlabel('Episodes')
        axes[1, 1].set_ylabel('Draw Rate (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_file = f"plots/training_metrics_{timestamp}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Performance plots saved to {plot_file}")
        print(f"Performance plots saved to {plot_file}")
    
    def check_convergence(self) -> bool:
        """Check if training has converged based on recent performance."""
        if len(self.stats_history) < 20:
            return False
        
        # Get recent win rates
        recent_stats = self.stats_history[-20:]
        recent_p1_rates = [s['p1_win_rate'] for s in recent_stats]
        recent_draw_rates = [s['draw_rate'] for s in recent_stats]
        
        # Calculate stability metrics
        p1_std = np.std(recent_p1_rates)
        draw_std = np.std(recent_draw_rates)
        
        # Check convergence criteria
        convergence_score = (p1_std + draw_std) / 2
        
        self.convergence_metrics.append({
            'episode': self.stats_history[-1]['episode'],
            'convergence_score': convergence_score,
            'p1_std': p1_std,
            'draw_std': draw_std
        })
        
        return convergence_score < self.convergence_threshold
    
    def train(self):
        """Run the self-play training loop."""
        batch_size = min(100, self.max_workers) if self.use_parallel else 1
        print("Ultra-Advanced Q-Learning Self-Play Training - Maximum Performance")
        print("=" * 80)
        print(f"Episodes: {self.episodes:,}")
        print(
            f"Sequential training on main process (shared Q); "
            f"batch_size={batch_size} (use_parallel controls batch size only)"
        )
        print(f"Early stopping: {self.early_stopping}")
        print(f"Learning rate: {self.agent.alpha_start} → {self.agent.alpha_end}")
        print(f"Discount factor (γ): {self.agent.gamma}")
        print(f"Epsilon decay: {self.agent.epsilon_start} → {self.agent.epsilon_end}")
        print(f"Double Q-learning: {self.agent.use_double_q}")
        print(f"Dyna-Q: {self.agent.use_dyna_q}")
        print(f"Experience replay: {self.agent.experience_replay_size:,}")
        print(f"Prioritized replay: {self.agent.prioritized_replay}")
        print()
        
        self.training_start_time = time.time()
        
        print("Starting training with immediate progress updates...")
        print(f"Detailed stats every {self.stats_interval:,} completed episodes")
        print("First update should appear in ~10-30 seconds")
        print()
        
        # Training loop (batched sequential; episode advances by batch_size so use
        # (episode - 1) % N for milestones — raw `episode % N` never hits for N coprime to batch_size).
        episode = 1
        
        print(f"Debug: Starting training loop with batch_size={batch_size}")
        print(f"Debug: use_parallel={self.use_parallel}")
        print(f"Debug: max_workers={self.max_workers}")
        
        while episode <= self.episodes:
                # Create batch of episodes
                batch_end = min(episode + batch_size - 1, self.episodes)
                episode_batch = list(range(episode, batch_end + 1))
                
                print(f"Debug: About to train batch {episode}-{batch_end} ({len(episode_batch)} episodes)")
                
                batch_start_time = time.time()
                print(f"Debug: Calling train_parallel_batch...")
                results = self.train_parallel_batch(episode_batch)
                batch_time = time.time() - batch_start_time
                print(f"Debug: Batch completed in {batch_time:.2f}s, got {len(results)} results")
                
                # Process results
                for ep_id, winner, episode_length in results:
                    self.episode_lengths.append(episode_length)
                    
                    if winner == 1:
                        self.win_counts['player_1'] += 1
                    elif winner == -1:
                        self.win_counts['player_2'] += 1
                    else:
                        self.win_counts['draw'] += 1
                
                episode = batch_end + 1
                
                # Update performance metrics
                self.episodes_per_second = (
                    len(episode_batch) / batch_time if batch_time > 0 else 0.0
                )
                
                completed = episode - 1
                # Show small progress indicator every 100 completed episodes
                if completed > 0 and completed % 100 == 0:
                    print(f"Episode {completed:,} completed | Speed: {self.episodes_per_second:.1f} ep/s")
                
                # Print detailed statistics
                if completed > 0 and completed % self.stats_interval == 0:
                    self._print_ultra_advanced_statistics(completed, batch_time)
                
                # Save Q-table
                if completed > 0 and completed % self.save_interval == 0:
                    self.agent.save_q_table(self.q_table_file)
                
                # Check for early stopping
                if self.early_stopping and episode > 100000:
                    if self.check_convergence():
                        print(f"\nCONVERGENCE ACHIEVED at episode {episode - 1}!")
                        print("Training terminated early due to convergence.")
                        break
        
        # Final save and statistics
        self.agent.save_q_table(self.q_table_file)
        self._print_final_ultra_advanced_statistics()
        
    def _print_ultra_advanced_statistics(self, episode: int, batch_time: float):
        """Print training statistics."""
        elapsed_time = time.time() - self.training_start_time
        
        # Calculate recent statistics
        recent_start = max(0, episode - 10000)
        recent_lengths = self.episode_lengths[recent_start:]
        avg_length = np.mean(recent_lengths) if recent_lengths else 0
        
        # Calculate win rates
        total_games = sum(self.win_counts.values())
        p1_rate = self.win_counts['player_1'] / total_games * 100 if total_games > 0 else 0
        p2_rate = self.win_counts['player_2'] / total_games * 100 if total_games > 0 else 0
        draw_rate = self.win_counts['draw'] / total_games * 100 if total_games > 0 else 0
        
        # Store statistics
        stats = {
            'episode': episode,
            'elapsed_time': elapsed_time,
            'batch_time': batch_time,
            'episodes_per_second': self.episodes_per_second,
            'epsilon': self.agent.get_epsilon(),
            'alpha': self.agent.get_alpha(),
            'total_states': len(set(self.agent.q_table_a.keys()) | set(self.agent.q_table_b.keys())),
            'avg_episode_length': avg_length,
            'p1_win_rate': p1_rate,
            'p2_win_rate': p2_rate,
            'draw_rate': draw_rate,
            'experience_buffer_size': len(self.agent.experience_buffer)
        }
        self.stats_history.append(stats)
        
        # Log training metrics
        self.log_training_metrics(episode, stats)
        
        print(f"Episode {episode:,} | "
              f"Time: {elapsed_time:.1f}s | "
              f"Speed: {self.episodes_per_second:.1f} ep/s | "
              f"ε: {self.agent.get_epsilon():.4f} | "
              f"α: {self.agent.get_alpha():.4f}")
        print(f"States: {stats['total_states']:,} | "
              f"Avg Length: {avg_length:.1f} | "
              f"Buffer: {stats['experience_buffer_size']:,}")
        print(f"Win Rates: P1={p1_rate:.1f}% | P2={p2_rate:.1f}% | Draw={draw_rate:.1f}%")
        
        # Performance milestones
        if episode == 50000:
            print("50k episodes: Foundation learning complete")
        elif episode == 100000:
            print("100k episodes: Strategic learning phase")
        elif episode == 200000:
            print("200k episodes: Advanced optimization")
        elif episode == 300000:
            print("300k episodes: Near-perfect play")
        elif episode == 500000:
            print("500k episodes: Maximum performance achieved")
        
        # Convergence analysis
        if len(self.convergence_metrics) > 0:
            latest_convergence = self.convergence_metrics[-1]
            print(f"Convergence Score: {latest_convergence['convergence_score']:.4f}")
            
            if latest_convergence['convergence_score'] < self.convergence_threshold:
                print("Perfect convergence achieved!")
        
        print()
    
    def _print_final_ultra_advanced_statistics(self):
        """Print final training statistics."""
        total_time = time.time() - self.training_start_time
        
        print("Ultra-Advanced Training Complete!")
        print("=" * 60)
        print(f"Total episodes: {self.episodes:,}")
        print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        if total_time > 0:
            print(f"Average speed: {self.episodes/total_time:.1f} episodes/second")
        else:
            print("Average speed: n/a")
        if self.stats_history:
            peak = max(s["episodes_per_second"] for s in self.stats_history)
            print(f"Peak speed: {peak:.1f} episodes/second")
        else:
            print("Peak speed: n/a (no stats checkpoints recorded)")
        print()
        
        # Final win rates
        total_games = sum(self.win_counts.values())
        print("Final Win Rates:")
        if total_games > 0:
            print(f"  Player 1 (X): {self.win_counts['player_1']:,} ({self.win_counts['player_1']/total_games*100:.1f}%)")
            print(f"  Player 2 (O): {self.win_counts['player_2']:,} ({self.win_counts['player_2']/total_games*100:.1f}%)")
            print(f"  Draws: {self.win_counts['draw']:,} ({self.win_counts['draw']/total_games*100:.1f}%)")
        else:
            print("  No games completed.")
        print()
        
        # Q-table statistics
        all_states = set(self.agent.q_table_a.keys()) | set(self.agent.q_table_b.keys())
        print("Ultra-Advanced Q-Table Statistics:")
        print(f"  Total states: {len(all_states):,}")
        print(f"  Total steps: {self.agent.total_steps:,}")
        print(f"  Final alpha: {self.agent.get_alpha():.6f}")
        print(f"  Final epsilon: {self.agent.get_epsilon():.6f}")
        print(f"  Experience buffer: {len(self.agent.experience_buffer):,}")
        print(f"  Move patterns: {len(self.agent.move_patterns):,}")
        print()
        
        # Episode length statistics
        if self.episode_lengths:
            avg_length = float(np.mean(self.episode_lengths))
            std_length = float(np.std(self.episode_lengths))
            print(f"Episode Length: {avg_length:.1f} ± {std_length:.1f} moves")
        else:
            print("Episode Length: n/a")
        print()
        
        # Performance analysis
        if len(self.stats_history) >= 10:
            early_states = self.stats_history[0]['total_states']
            late_states = self.stats_history[-1]['total_states']
            print(f"State Space Growth: {early_states:,} → {late_states:,} states")
            
            early_epsilon = self.stats_history[0]['epsilon']
            late_epsilon = self.stats_history[-1]['epsilon']
            print(f"Exploration Decay: {early_epsilon:.4f} → {late_epsilon:.6f}")
            
            early_alpha = self.stats_history[0]['alpha']
            late_alpha = self.stats_history[-1]['alpha']
            print(f"Learning Rate Decay: {early_alpha:.4f} → {late_alpha:.6f}")
        
        # Generate final analytics
        self._generate_final_analytics()
        
        # Generate performance plots
        self.generate_performance_plots()
    
    def _generate_final_analytics(self):
        """Generate final analytics."""
        print("\nUltra-Advanced Analytics:")
        print("-" * 30)
        
        # Strategic preferences
        strategic_prefs = self.agent.analyze_strategic_preferences()
        print(f"Strategic Position Analysis: {len(strategic_prefs)} positions analyzed")
        
        # Top move patterns
        top_patterns = sorted(self.agent.move_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top Move Patterns:")
        for pattern, count in top_patterns:
            print(f"  {pattern}: {count} occurrences")
        
        # Performance metrics
        if len(self.convergence_metrics) > 0:
            final_convergence = self.convergence_metrics[-1]['convergence_score']
            print(f"Final Convergence Score: {final_convergence:.6f}")
            
            if final_convergence < self.convergence_threshold:
                print("PERFECT CONVERGENCE ACHIEVED!")
            else:
                print("Convergence in progress")
    
    def get_training_history(self) -> List[Dict]:
        """Get comprehensive training history."""
        return self.stats_history.copy()
    
    def export_analytics(self, filename: str = "training_analytics.json"):
        """Export training analytics."""
        analytics_data = {
            'training_history': self.stats_history,
            'convergence_metrics': self.convergence_metrics,
            'final_statistics': {
                'total_episodes': self.episodes,
                'total_time': time.time() - self.training_start_time,
                'win_counts': self.win_counts,
                'episode_lengths': self.episode_lengths,
                'agent_statistics': self.agent.get_statistics()
            },
            'strategic_analysis': self.agent.analyze_strategic_preferences(),
            'move_patterns': dict(self.agent.move_patterns)
        }
        
        with open(filename, 'w') as f:
            json.dump(analytics_data, f, indent=2)
        
        print(f"Analytics exported to {filename}")


def load_config(config_file: str = "config.yaml") -> dict:
    """Load configuration from YAML file.

    Searches CWD first, then the src/ directory (one level above this file).
    """
    candidates = [
        config_file,
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config_file),
    ]
    for path in candidates:
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"Loaded config from {path}")
            return config
        except FileNotFoundError:
            continue
    print(f"Config file {config_file} not found. Using default settings.")
    return {}

def set_deterministic_seed(seed: int = 42):
    """Set deterministic seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)

def main():
    """Main training function."""
    print("Ultra-Advanced Q-Learning Tic-Tac-Toe AI Training")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Set deterministic seed
    seed = config.get('reproducibility', {}).get('seed', 42)
    set_deterministic_seed(seed)
    print(f"Using seed: {seed}")
    
    # Extract parameters from config
    training_config = config.get('training', {})
    hyperparams = config.get('hyperparameters', {})
    hardware_config = config.get('hardware', {})
    
    # Create ultra-advanced trainer
    trainer = UltraAdvancedSelfPlayTrainer(
        episodes=training_config.get('episodes', 50000),
        save_interval=training_config.get('save_interval', 5000),
        stats_interval=training_config.get('stats_interval', 1000),
        q_table_file=config.get('paths', {}).get('q_table_file', 'q_table.json'),
        use_parallel=hardware_config.get('use_parallel', True),
        early_stopping=training_config.get('early_stopping', True),
        convergence_threshold=training_config.get('convergence_threshold', 0.02)
    )
    
    # Start ultra-advanced training
    trainer.train()
    
    # Export analytics
    trainer.export_analytics()


if __name__ == "__main__":
    main()