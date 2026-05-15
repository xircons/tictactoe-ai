"""
Long-form training run (~1 hour on a typical laptop).

Compared to the default train.py:
  - More episodes (500k by default — adjust EPISODES below)
  - epsilon_decay_steps stretched so exploration lasts most of the run,
    not just the first ~2,500 episodes
  - Bigger experience replay buffer
  - Lower alpha_end for finer-grained late-stage updates
  - early_stopping disabled so it actually runs the full duration

Usage:
    python3 src/training/train_long.py

Output (overwrites previous):
    q_table.json
    training_analytics.json
    logs/training_<ts>.log
    plots/training_metrics_<ts>.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from training.train import UltraAdvancedSelfPlayTrainer, set_deterministic_seed
from agents.qlearning_agent import UltraAdvancedQLearningAgent


# Tune these if you want a longer/shorter run.
EPISODES = 500_000          # ~500k ≈ 40–60 min on a modern laptop
SAVE_INTERVAL = 50_000      # save q_table.json every Nth episode (resume-safe)
STATS_INTERVAL = 10_000     # print + log detailed stats every Nth episode


def main() -> None:
    set_deterministic_seed(42)

    trainer = UltraAdvancedSelfPlayTrainer(
        episodes=EPISODES,
        save_interval=SAVE_INTERVAL,
        stats_interval=STATS_INTERVAL,
        q_table_file="q_table.json",
        use_parallel=True,
        early_stopping=False,        # let it run the full duration
        convergence_threshold=0.02,
    )

    # Override the default agent with one tuned for a long run.
    # Key change: epsilon_decay_steps was 200k (decayed to floor in
    # ~2,500 episodes) — bump it to 30M steps so the agent keeps exploring
    # through most of the training instead of locking in early.
    trainer.agent = UltraAdvancedQLearningAgent(
        alpha_start=0.1,
        alpha_end=0.005,             # slightly lower than default 0.01
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.001,
        epsilon_decay_steps=30_000_000,
        use_double_q=True,
        use_dyna_q=True,
        experience_replay_size=50_000,
        prioritized_replay=True,
    )

    trainer.train()
    trainer.export_analytics()


if __name__ == "__main__":
    main()
