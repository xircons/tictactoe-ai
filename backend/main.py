"""
Tic-Tac-Toe API Backend
Flask API server with Q-learning inference (epsilon-greedy by difficulty)
"""

import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from agents.qlearning_agent import QLearningInferenceAgent, EPSILON_BY_DIFFICULTY
from core.tictactoe import TicTacToe

app = Flask(__name__)

# Allowed origins for the API. Set ALLOWED_ORIGINS env var to a comma-separated
# list to extend at runtime — e.g. "https://my-app.vercel.app,https://example.com"
# — without editing this file.
#
# NOTE: flask-cors interprets any string containing regex metacharacters (like
# `*`) as a regex pattern, NOT a glob. So "https://*.vercel.app" is a BROKEN
# regex (it matches "https://.vercel.app", not real subdomains). Use proper
# regex patterns below — and `re.compile(...)` so flask-cors uses them as-is.
_default_origins = [
    # Vercel — production frontends and preview deployments (any *.vercel.app)
    re.compile(r"^https://.*\.vercel\.app$"),
    # GitHub Pages (legacy)
    re.compile(r"^https://.*\.github\.io$"),
    # Local development
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5001",
    "http://127.0.0.1:5001",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "file://",
    "null",
]
_extra = os.environ.get("ALLOWED_ORIGINS", "").strip()
_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

CORS(app, resources={
    r"/api/*": {
        "origins": _origins,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False,
    }
})

# The agent handles its own path resolution: Q_TABLE_PATH env var, then
# backend/ or repo-root q_table_clean.json (preferred) → q_table.json (legacy).
q_agent = QLearningInferenceAgent()
if q_agent.loaded_path:
    print(f"Q-table path: {q_agent.loaded_path}")


def _parse_move_request(data):
    """
    Validate move request JSON. Returns (game, difficulty, None) on success,
    or (None, None, (response, status)) on error.
    """
    if not data:
        return None, None, (jsonify({"error": "No JSON data provided"}), 400)

    board = data.get("board")
    player = data.get("player")

    if not board:
        return None, None, (jsonify({"error": "Board state is required"}), 400)

    if not isinstance(board, list) or len(board) != 9:
        return None, None, (jsonify({"error": "Board must be a list of 9 elements"}), 400)

    if player is None:
        return None, None, (jsonify({"error": "Player is required"}), 400)

    for i, cell in enumerate(board):
        if cell not in [0, 1, -1]:
            return None, None, (jsonify({"error": f"Invalid value {cell} at position {i}"}), 400)

    game = TicTacToe()
    game.board = board.copy()
    game.current_player = player

    if game.check_winner():
        return None, None, (jsonify({"error": "Game is already won"}), 400)

    if len(game.get_available_actions()) == 0:
        return None, None, (jsonify({"error": "No available moves"}), 400)

    difficulty = (data.get("difficulty") or "hard").lower()
    return game, difficulty, None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Tic-Tac-Toe API is running",
        "agent": "Q-Learning (epsilon-greedy)",
        "q_table_loaded": q_agent.is_ready(),
        "q_states": q_agent.state_count(),
        "load_error": q_agent.load_error,
        "policy": {
            "epsilon_by_difficulty": EPSILON_BY_DIFFICULTY,
        }
    })


@app.route('/api/move', methods=['POST'])
def get_ai_move():
    """
    Get AI move for given board state and difficulty (epsilon-greedy).

    Expected JSON:
    {
        "board": [0, 1, -1, 0, 0, 0, 0, 0, 0],
        "player": -1,
        "difficulty": "easy" | "medium" | "hard"
    }
    difficulty defaults to "hard" if omitted.
    """
    try:
        data = request.get_json()
        game, difficulty, err = _parse_move_request(data)
        if err:
            return err

        ai_move = q_agent.choose_move(game, difficulty)
        game.make_move(ai_move)

        return jsonify({
            "move": ai_move,
            "message": f"AI ({difficulty}) plays position {ai_move}",
            "board": game.board,
            "game_over": game.game_over,
            "winner": game.winner
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/validate', methods=['POST'])
def validate_board():
    """
    Validate board state and return game status

    Expected JSON:
    {
        "board": [0, 1, -1, 0, 0, 0, 0, 0, 0]
    }

    Returns:
    {
        "valid": true,
        "game_over": false,
        "winner": null,
        "available_moves": [3, 4, 5, 6, 7, 8]
    }
    """
    try:
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({"error": "Board state is required"}), 400

        board = data['board']

        if not isinstance(board, list) or len(board) != 9:
            return jsonify({"error": "Board must be a list of 9 elements"}), 400

        for i, cell in enumerate(board):
            if cell not in [0, 1, -1]:
                return jsonify({"error": f"Invalid value {cell} at position {i}"}), 400

        game = TicTacToe()
        game.board = board.copy()

        game.check_winner()

        return jsonify({
            "valid": True,
            "game_over": game.game_over,
            "winner": game.winner,
            "available_moves": game.get_available_actions()
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == '__main__':
    print("Starting Tic-Tac-Toe API server...")
    print(f"Q-learning inference: loaded={q_agent.is_ready()}, states={q_agent.state_count()}")
    if q_agent.load_error:
        print(f"  Note: {q_agent.load_error} (API will use random legal moves as fallback)")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/move - Get AI move (body: board, player, difficulty)")
    print("  POST /api/validate - Validate board state")

    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
