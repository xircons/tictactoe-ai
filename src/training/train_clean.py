"""
Training driver for CleanQLearningAgent.

Pure tabular Q-learning with terminal-only rewards. Goal: prove that with
the right setup, Q-learning on tic-tac-toe converges to optimal play —
drawing every game against minimax, never losing to random.

Usage:
    python3 src/training/train_clean.py                 # default 500k episodes
    python3 src/training/train_clean.py 100000          # override episode count
    python3 src/training/train_clean.py --fresh         # ignore existing checkpoint
Re-running resumes from q_table_clean.json automatically. Pass --fresh to wipe.

Outputs (saved at repo root, separate from the legacy q_table.json):
    q_table_clean.json
"""

from __future__ import annotations

import os
import random
import sys
import time
from typing import Tuple

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.clean_qlearning_agent import CleanQLearningAgent
from agents.perfect_agent import PerfectMinimaxAgent
from core.tictactoe import TicTacToe


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)


# ---------- evaluation helpers ----------


def play_one(agent: CleanQLearningAgent, opponent_fn, agent_plays_x: bool) -> int:
    """Play one game. Returns winner (1, -1, 0)."""
    g = TicTacToe()
    g.reset()
    while not g.game_over:
        if (g.current_player == 1) == agent_plays_x:
            move = agent.choose_action(g, greedy=True)
        else:
            move = opponent_fn(g)
        g.make_move(move)
    return g.winner


def benchmark(agent: CleanQLearningAgent, n_per_side: int = 100) -> dict:
    """Play n_per_side games as X and as O against random + against minimax."""
    rng = random.Random(123)
    minimax = PerfectMinimaxAgent()

    def random_move(g: TicTacToe) -> int:
        return rng.choice(g.get_available_actions())

    def minimax_move(g: TicTacToe) -> int:
        return minimax.choose_action(g)

    results = {}
    for opp_name, opp_fn in [("random", random_move), ("minimax", minimax_move)]:
        wins = losses = draws = 0
        for plays_x in (True, False):
            for _ in range(n_per_side):
                winner = play_one(agent, opp_fn, plays_x)
                me = 1 if plays_x else -1
                if winner == me:
                    wins += 1
                elif winner == -me:
                    losses += 1
                else:
                    draws += 1
        total = 2 * n_per_side
        results[opp_name] = {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "total": total,
        }
    return results


def print_benchmark(label: str, results: dict) -> None:
    print(f"\n{label}")
    print(f"  {'opponent':10s} {'wins':>5s} {'losses':>6s} {'draws':>5s}  (out of {results['random']['total']})")
    for opp in ("random", "minimax"):
        r = results[opp]
        marker = "  ← never lose" if (opp == "minimax" and r["losses"] == 0) else ""
        print(f"  {opp:10s} {r['wins']:5d} {r['losses']:6d} {r['draws']:5d}{marker}")


# ---------- training ----------


def train(
    episodes: int = 500_000,
    save_path: str = "q_table_clean.json",
    checkpoint_every: int = 50_000,
    resume: bool = True,
) -> CleanQLearningAgent:
    set_seed(42)

    agent = CleanQLearningAgent(
        alpha=0.3,
        alpha_end=0.05,
        gamma=0.95,
        epsilon_start=1.0,
        epsilon_end=0.02,
        decay_episodes=int(episodes * 0.8),  # explore for first 80% of training
    )

    # Resume from existing checkpoint if present and not yet at target.
    start_ep = 0
    if resume and os.path.isfile(save_path):
        try:
            agent.load(save_path)
            start_ep = agent.episodes_trained
            if start_ep >= episodes:
                print(f"Already at {start_ep:,} ≥ {episodes:,} episodes — nothing to do.")
                print(f"(delete {save_path} or pass --fresh to start over)")
                return agent
            print(f"Resuming from {save_path}: {start_ep:,} episodes, {agent.state_count():,} states")
        except Exception as exc:
            print(f"Could not resume from {save_path} ({exc}) — starting fresh")
            start_ep = 0

    remaining = episodes - start_ep
    print(f"CleanQLearningAgent training — target {episodes:,} self-play episodes ({remaining:,} remaining)")
    print(f"  α: {agent.alpha_start} → {agent.alpha_end}")
    print(f"  ε: {agent.epsilon_start} → {agent.epsilon_end} (decay over {agent.decay_episodes:,} ep)")
    print(f"  γ: {agent.gamma}")
    print(f"  checkpoint every: {checkpoint_every:,} episodes → {save_path}")
    print()

    game = TicTacToe()
    t0 = time.time()
    win_counts = {1: 0, -1: 0, 0: 0}
    next_print = 1000
    last_checkpoint = start_ep

    for ep in range(start_ep + 1, episodes + 1):
        w = agent.train_episode(game)
        win_counts[w] += 1

        if ep == next_print or ep == episodes:
            elapsed = time.time() - t0
            done_in_session = ep - start_ep
            speed = done_in_session / elapsed if elapsed > 0 else 0
            eta = (episodes - ep) / speed if speed > 0 else 0
            print(
                f"ep {ep:>7,} | states {agent.state_count():>5,} | "
                f"ε {agent.get_epsilon():.3f} | α {agent.get_alpha():.3f} | "
                f"P1 {win_counts[1]:>5,} P2 {win_counts[-1]:>5,} D {win_counts[0]:>5,} | "
                f"{speed:.0f} ep/s | ETA {eta:.0f}s"
            )
            next_print = min(next_print * 2 if next_print < 10_000 else next_print + 10_000, episodes)

        # Periodic checkpoint so the run is restart-safe.
        if checkpoint_every and ep - last_checkpoint >= checkpoint_every and ep < episodes:
            agent.save(save_path)
            last_checkpoint = ep

    total = time.time() - t0
    print(f"\nDone. {episodes - start_ep:,} new episodes in {total:.1f}s "
          f"({(episodes - start_ep)/max(total, 1e-9):.0f} ep/s). "
          f"Total episodes: {agent.episodes_trained:,}. States: {agent.state_count():,}.")

    agent.save(save_path)
    print(f"Saved to {save_path}")

    return agent


def main() -> None:
    # Usage: train_clean.py [EPISODES] [--fresh]
    args = [a for a in sys.argv[1:] if a != "--fresh"]
    resume = "--fresh" not in sys.argv
    episodes = int(args[0]) if args else 500_000
    save_path = os.environ.get("CLEAN_Q_PATH", "q_table_clean.json")
    agent = train(episodes=episodes, save_path=save_path, resume=resume)

    print("\nEvaluating trained agent (greedy policy)…")
    results = benchmark(agent, n_per_side=100)
    print_benchmark(f"After {agent.episodes_trained:,} episodes:", results)

    print(
        "\nA properly converged Q-learner should show 0 losses to BOTH random and minimax.\n"
        "If it still loses, train longer (more episodes), or check hyperparams."
    )


if __name__ == "__main__":
    main()
