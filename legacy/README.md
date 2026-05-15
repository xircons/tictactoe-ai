# Legacy Code

Files here are **kept for historical reference only**. They are not imported by
anything in `src/`, `backend/`, or `frontend/` and are excluded from deployment.

## What's here

| File | What it was | Why retired |
|---|---|---|
| `agents/qlearning_agent.py` | `UltraAdvancedQLearningAgent` — tabular Q-learning with reward shaping, symmetry reduction (broken action remap), double-Q, Dyna-Q, MCTS evaluation, prioritized replay | Empirically failed to converge to optimal play even after 500k episodes. The clean baseline does. See the audit report. |
| `agents/baseline_agents.py` | Mixed agents (random, heuristic) — not wired into the API | Superseded by clean Q-learner in `src/agents/clean_qlearning_agent.py` |
| `training/train.py` | Trainer for the ultra-advanced agent | Ultra-advanced agent retired |
| `training/train_long.py` | Long-form training driver with extended ε decay | Same |

## The replacement

`CleanQLearningAgent` (`src/agents/clean_qlearning_agent.py`) — plain tabular
Q-learning, terminal rewards only (+1/-1/0), no symmetry, no machinery. Trained
by `src/training/train_clean.py`. Reaches optimal play (draws 60/60 vs minimax)
in ~85 seconds at 500k episodes.

## Why keep these files at all?

- Reproducibility of the empirical comparison in `docs/audit_report.md` (if you
  want to re-measure the failure modes).
- Reference for what *not* to do when adding complexity to an RL implementation.

You can safely delete this whole folder if you do not care about either.
