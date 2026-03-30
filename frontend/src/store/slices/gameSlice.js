import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  board: ['', '', '', '', '', '', '', '', ''],
  currentPlayer: 'X',
  gameActive: false,
  scores: { X: 0, O: 0, draw: 0 },
  playerNames: { X: 'PLAYER', O: 'AI' },
  isPlayerTurn: true,
  apiAvailable: true,
  difficulty: 'hard', // 'easy', 'medium', 'hard'
  gameMode: 'ai', // 'ai' or 'human'
  currentGameStartTime: null,
  currentGameMoves: 0
}

const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    setBoard: (state, action) => {
      state.board = action.payload
    },
    setCurrentPlayer: (state, action) => {
      state.currentPlayer = action.payload
    },
    setGameActive: (state, action) => {
      state.gameActive = action.payload
    },
    updateScores: (state, action) => {
      const winner = action.payload
      state.scores[winner] = state.scores[winner] + 1
    },
    setPlayerNames: (state, action) => {
      state.playerNames = action.payload
    },
    setIsPlayerTurn: (state, action) => {
      state.isPlayerTurn = action.payload
    },
    setApiAvailable: (state, action) => {
      state.apiAvailable = action.payload
    },
    setDifficulty: (state, action) => {
      state.difficulty = action.payload
    },
    setGameMode: (state, action) => {
      state.gameMode = action.payload
    },
    makeMove: (state, action) => {
      const { index, player } = action.payload
      state.board[index] = player
      state.currentGameMoves += 1
    },
    switchPlayer: (state) => {
      state.currentPlayer = state.currentPlayer === 'X' ? 'O' : 'X'
      state.isPlayerTurn = !state.isPlayerTurn
    },
    resetGame: (state) => {
      state.board = ['', '', '', '', '', '', '', '', '']
      state.currentPlayer = 'X'
      state.gameActive = true
      state.isPlayerTurn = true
      state.currentGameStartTime = Date.now()
      state.currentGameMoves = 0
    },
    startGame: (state, action) => {
      const { playerName, player2Name, difficulty, gameMode } = action.payload
      state.playerNames.X = playerName.trim().toUpperCase() || 'PLAYER 1'
      state.playerNames.O = gameMode === 'ai' 
        ? 'AI' 
        : (player2Name ? player2Name.trim().toUpperCase() : 'PLAYER 2')
      state.difficulty = difficulty || 'hard'
      state.gameMode = gameMode || 'ai'
      state.gameActive = true
      state.isPlayerTurn = true
      state.currentPlayer = 'X'
      state.board = ['', '', '', '', '', '', '', '', '']
      state.currentGameStartTime = Date.now()
      state.currentGameMoves = 0
    },
    endGame: (state) => {
      state.gameActive = false
    },
    resetScores: (state) => {
      state.scores = { X: 0, O: 0, draw: 0 }
    },
    resetToInitial: (state) => {
      return initialState
    }
  }
})

export const {
  setBoard,
  setCurrentPlayer,
  setGameActive,
  updateScores,
  setPlayerNames,
  setIsPlayerTurn,
  setApiAvailable,
  setDifficulty,
  setGameMode,
  makeMove,
  switchPlayer,
  resetGame,
  startGame,
  endGame,
  resetScores,
  resetToInitial
} = gameSlice.actions

export default gameSlice.reducer

