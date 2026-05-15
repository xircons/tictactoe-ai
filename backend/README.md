# Tic-Tac-Toe API Backend

Flask API that serves **one trained Q-table** (`q_table.json`). Difficulty (`easy`, `medium`, `hard`) is implemented with **epsilon-greedy** exploration on the same policy: higher epsilon means more random legal moves.

## Features

- **Single Q-learning policy**: loads `q_table.json` once at process start
- **Epsilon by difficulty**: easy 0.75, medium 0.25, hard 0.0 (greedy on Q)
- **Fallback**: if the file is missing, unreadable, or a state is absent from the table, the API returns a **random legal** move (HTTP 200) so clients keep working
- **REST + CORS**: same CORS setup as before for GitHub Pages and local dev

## Q-table file

- **Default path**: `backend/q_table.json` (same directory as `main.py` when resolved from the repo)
- **Training output**: run `python src/training/train.py` from the project root; then copy or symlink the generated `q_table.json` into `backend/`
- **Override**: set environment variable **`Q_TABLE_PATH`** to an absolute path (recommended on Render) if the file is not in the default location

On Render (and similar hosts), commit `backend/q_table.json` or bake it into the deploy artifact; otherwise the service runs in random-move fallback until you add the file.

## API Endpoints

### Health Check

```
GET /api/health
```

Returns `q_table_loaded`, `q_states`, `load_error` (if any), and `policy.epsilon_by_difficulty`.

### Get AI Move

```
POST /api/move
```

**Request:**

```json
{
    "board": [0, 1, -1, 0, 0, 0, 0, 0, 0],
    "player": -1,
    "difficulty": "medium"
}
```

- `difficulty`: `"easy"` | `"medium"` | `"hard"` — defaults to `"hard"` if omitted
- `board`: nine cells, `0` empty, `1` X, `-1` O
- `player`: side to move (AI is typically `-1`)

**Response:**

```json
{
    "move": 4,
    "message": "AI (medium) plays position 4",
    "board": [0, 1, -1, 0, -1, 0, 0, 0, 0],
    "game_over": false,
    "winner": null
}
```

### Validate Board

```
POST /api/validate
```

Same as before; see request/response examples in the repository root `README.md` if needed.

## Board Representation

The board is a 9-element array:

- `0` = empty
- `1` = X
- `-1` = O

Indices:

```
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

## Setup

### Local development

1. From repository root: `pip install -r requirements.txt`
2. Copy trained weights: `cp q_table.json backend/q_table.json` (after training)
3. Start API from repository root: `python backend/main.py` (default port **5001**)

Or from `backend/`: `python main.py` (ensure `pip install` was run from root so imports resolve; running from root is simplest).

### Test with curl

```bash
curl http://localhost:5001/api/health

curl -X POST http://localhost:5001/api/move \
  -H "Content-Type: application/json" \
  -d '{"board": [1, 0, 0, 0, 0, 0, 0, 0, 0], "player": -1, "difficulty": "hard"}'

curl -X POST http://localhost:5001/api/validate \
  -H "Content-Type: application/json" \
  -d '{"board": [1, 0, 0, 0, 0, 0, 0, 0, 0]}'
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `PORT` | Listen port (default `5001` when using `python backend/main.py`) |
| `FLASK_ENV` | Set to `production` for production |
| `Q_TABLE_PATH` | Optional path to `q_table.json` |

## Production deployment

Build still uses root `requirements.txt`. Start command should run gunicorn from the `backend` directory (see `deployment/render.yaml`). Set `Q_TABLE_PATH` if the JSON file is not at `backend/q_table.json`.

## Troubleshooting

1. **Always random moves**: check `GET /api/health` for `q_table_loaded: false` and `load_error`
2. **CORS**: extend `origins` in `main.py` if you add a new frontend origin
3. **Port in use**: set `PORT` to another value
