"""
Tic-Tac-Toe API Backend
Flask API server with Perfect Minimax AI agent
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from agents.perfect_agent import PerfectMinimaxAgent
from agents.easy_agent import EasyAgent
from agents.medium_agent import MediumAgent
from core.tictactoe import TicTacToe

app = Flask(__name__)
# Configure CORS to allow requests from GitHub Pages, localhost, and Render.com
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://xircons.github.io",
            "https://*.github.io",
            "http://localhost:3000",
            "http://localhost:5173",  # Vite default port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",  # Vite default port
            "http://localhost:5001",
            "http://127.0.0.1:5001",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "file://",
            "null"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Initialize the AI agents
easy_agent = EasyAgent()
medium_agent = MediumAgent()
hard_agent = PerfectMinimaxAgent()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Tic-Tac-Toe API is running",
        "agents": {
            "easy": easy_agent.name,
            "medium": medium_agent.name,
            "hard": hard_agent.name
        }
    })

@app.route('/api/move', methods=['POST'])
def get_ai_move():
    """
    Get AI move for given board state
    
    Expected JSON:
    {
        "board": [0, 1, -1, 0, 0, 0, 0, 0, 0],  # 9-element array: 0=empty, 1=X, -1=O
        "player": -1  # Current player: 1=X, -1=O (AI should be -1)
    }
    
    Returns:
    {
        "move": 4,  # Position index (0-8)
        "message": "AI plays position 4",
        "board": [0, 1, -1, 0, -1, 0, 0, 0, 0]  # Updated board
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        board = data.get('board')
        player = data.get('player')
        
        if not board:
            return jsonify({"error": "Board state is required"}), 400
        
        if not isinstance(board, list) or len(board) != 9:
            return jsonify({"error": "Board must be a list of 9 elements"}), 400
        
        if player is None:
            return jsonify({"error": "Player is required"}), 400
        
        # Validate board values
        for i, cell in enumerate(board):
            if cell not in [0, 1, -1]:
                return jsonify({"error": f"Invalid value {cell} at position {i}"}), 400
        
        # Create game instance
        game = TicTacToe()
        game.board = board.copy()
        game.current_player = player
        
        # Check if game is already over
        if game.check_winner():
            return jsonify({"error": "Game is already won"}), 400
        
        if len(game.get_available_actions()) == 0:
            return jsonify({"error": "No available moves"}), 400
        
        # Get AI move (hard difficulty)
        ai_move = hard_agent.choose_action(game)
        
        # Make the move to get updated board
        game.make_move(ai_move)
        
        return jsonify({
            "move": ai_move,
            "message": f"AI plays position {ai_move}",
            "board": game.board,
            "game_over": game.game_over,
            "winner": game.winner
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/move/easy', methods=['POST'])
def get_easy_ai_move():
    """Get easy AI move (random)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        board = data.get('board')
        player = data.get('player')
        
        if not board:
            return jsonify({"error": "Board state is required"}), 400
        
        if not isinstance(board, list) or len(board) != 9:
            return jsonify({"error": "Board must be a list of 9 elements"}), 400
        
        if player is None:
            return jsonify({"error": "Player is required"}), 400
        
        # Validate board values
        for i, cell in enumerate(board):
            if cell not in [0, 1, -1]:
                return jsonify({"error": f"Invalid value {cell} at position {i}"}), 400
        
        # Create game instance
        game = TicTacToe()
        game.board = board.copy()
        game.current_player = player
        
        # Check if game is already over
        if game.check_winner():
            return jsonify({"error": "Game is already won"}), 400
        
        if len(game.get_available_actions()) == 0:
            return jsonify({"error": "No available moves"}), 400
        
        # Get easy AI move
        ai_move = easy_agent.choose_action(game)
        
        # Make the move to get updated board
        game.make_move(ai_move)
        
        return jsonify({
            "move": ai_move,
            "message": f"Easy AI plays position {ai_move}",
            "board": game.board,
            "game_over": game.game_over,
            "winner": game.winner
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/move/medium', methods=['POST'])
def get_medium_ai_move():
    """Get medium AI move (heuristic)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        board = data.get('board')
        player = data.get('player')
        
        if not board:
            return jsonify({"error": "Board state is required"}), 400
        
        if not isinstance(board, list) or len(board) != 9:
            return jsonify({"error": "Board must be a list of 9 elements"}), 400
        
        if player is None:
            return jsonify({"error": "Player is required"}), 400
        
        # Validate board values
        for i, cell in enumerate(board):
            if cell not in [0, 1, -1]:
                return jsonify({"error": f"Invalid value {cell} at position {i}"}), 400
        
        # Create game instance
        game = TicTacToe()
        game.board = board.copy()
        game.current_player = player
        
        # Check if game is already over
        if game.check_winner():
            return jsonify({"error": "Game is already won"}), 400
        
        if len(game.get_available_actions()) == 0:
            return jsonify({"error": "No available moves"}), 400
        
        # Get medium AI move
        ai_move = medium_agent.choose_action(game)
        
        # Make the move to get updated board
        game.make_move(ai_move)
        
        return jsonify({
            "move": ai_move,
            "message": f"Medium AI plays position {ai_move}",
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
        
        # Validate board values
        for i, cell in enumerate(board):
            if cell not in [0, 1, -1]:
                return jsonify({"error": f"Invalid value {cell} at position {i}"}), 400
        
        # Create game instance
        game = TicTacToe()
        game.board = board.copy()
        
        # Check for winner
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
    print("AI agents loaded:")
    print(f"  - Easy: {easy_agent.name}")
    print(f"  - Medium: {medium_agent.name}")
    print(f"  - Hard: {hard_agent.name}")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/move - Get hard AI move")
    print("  POST /api/move/easy - Get easy AI move")
    print("  POST /api/move/medium - Get medium AI move")
    print("  POST /api/validate - Validate board state")
    
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
