import React, { useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { 
  makeMove, 
  switchPlayer, 
  endGame, 
  updateScores, 
  resetGame as resetGameAction,
  setApiAvailable,
  setIsPlayerTurn
} from '../store/slices/gameSlice'
import { showSlideMessage, hideSlideMessage } from '../store/slices/settingsSlice'
import { addGame } from '../store/slices/historySlice'
import { updateProgress } from '../store/slices/achievementsSlice'
import GameScreen from '../components/GameScreen'
import WinModal from '../components/WinModal'
import API_CONFIG from '../config/api'

// Win patterns
const winPatterns = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6]
]

const GamePage = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  
  // Get state from Redux
  const {
    board,
    currentPlayer,
    gameActive,
    scores,
    playerNames,
    isPlayerTurn,
    apiAvailable,
    difficulty,
    gameMode,
    currentGameStartTime,
    currentGameMoves
  } = useSelector((state) => state.game)
  
  const history = useSelector((state) => state.history)
  
  const [showWinModalState, setShowWinModalState] = React.useState(false)
  const [winMessage, setWinMessage] = React.useState('')
  const gameEndingRef = React.useRef(false)

  // Redirect if no active game (but not if showing win modal or game is ending)
  useEffect(() => {
    console.log('[EFFECT] gameActive:', gameActive, 'showWinModalState:', showWinModalState, 'gameEnding:', gameEndingRef.current)
    if (!gameActive && !showWinModalState && !gameEndingRef.current) {
      console.log('[EFFECT] Navigating to home')
      navigate('/')
    }
  }, [gameActive, showWinModalState, navigate])

  // Show slide message helper
  const displaySlideMessage = useCallback((message, duration = 3000) => {
    dispatch(showSlideMessage(message))
    setTimeout(() => {
      dispatch(hideSlideMessage())
    }, duration)
  }, [dispatch])

  // API Helper Functions
  const convertBoardToAPI = useCallback((board) => {
    return board.map(cell => {
      if (cell === 'X') return 1
      if (cell === 'O') return -1
      return 0
    })
  }, [])

  const getAIMoveFromAPI = useCallback(async (currentBoard) => {
    try {
      const apiBoard = convertBoardToAPI(currentBoard)
      
      // Determine endpoint based on difficulty
      let endpoint = API_CONFIG.ENDPOINTS.MOVE
      if (difficulty === 'easy') {
        endpoint = '/api/move/easy'
      } else if (difficulty === 'medium') {
        endpoint = '/api/move/medium'
      }
      
      const apiUrl = API_CONFIG.getBaseUrl() + endpoint
      
      console.log(`[AI REQUEST] Calling ${difficulty} AI...`)
      console.log('   API URL:', apiUrl)
      console.log('   Board State:', apiBoard)
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          board: apiBoard,
          player: -1
        })
      })
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('[AI RESPONSE] Move received:', data.move)
      
      return data
      
    } catch (error) {
      console.error('[API ERROR] Failed to connect to backend:', error)
      dispatch(setApiAvailable(false))
      displaySlideMessage('API UNAVAILABLE - USING RANDOM AI', 3000)
      return null
    }
  }, [convertBoardToAPI, difficulty, dispatch, displaySlideMessage])

  // Check for winner
  const checkWinner = useCallback((board, player) => {
    return winPatterns.some(pattern => {
      return pattern.every(idx => board[idx] === player)
    })
  }, [])

  // Handle game end
  const handleGameEnd = useCallback((winner) => {
    console.log('[GAME END] Winner:', winner)
    
    // Mark that game is ending to prevent redirect
    gameEndingRef.current = true
    
    let message = ''
    let result = ''
    
    if (winner === 'draw') {
      message = 'DRAW GAME!'
      result = 'draw'
    } else {
      const winnerName = playerNames[winner]
      message = `${winnerName} WINS!`
      
      if (winner === 'X') {
        result = 'win'
      } else {
        result = 'loss'
      }
    }
    
    // Set modal state BEFORE ending game to prevent redirect
    console.log('[GAME END] Setting modal state:', message)
    setWinMessage(message)
    setShowWinModalState(true)
    
    // Now end the game and update scores
    dispatch(endGame())
    if (winner === 'draw') {
      dispatch(updateScores('draw'))
    } else if (winner === 'X') {
      dispatch(updateScores('X'))
    } else {
      dispatch(updateScores('O'))
    }
    
    // Don't show slide message on game end - win modal will display the result
    // displaySlideMessage(message, 1000)
    
    // Save game to history
    const gameResult = {
      date: new Date().toISOString(),
      result,
      duration: currentGameStartTime ? Math.floor((Date.now() - currentGameStartTime) / 1000) : 0,
      moves: currentGameMoves,
      difficulty: gameMode === 'ai' ? difficulty : 'human',
      playerName: playerNames.X,
      opponent: playerNames.O
    }
    
    dispatch(addGame(gameResult))
    
    // Update achievements
    dispatch(updateProgress({
      gameResult,
      currentStreak: result === 'win' ? history.currentStreak + 1 : 0,
      totalGames: history.totalGames + 1,
      totalWins: result === 'win' ? history.wins + 1 : history.wins
    }))
    
  }, [dispatch, playerNames, currentGameStartTime, currentGameMoves, gameMode, difficulty, history, displaySlideMessage])

  // Handle cell click
  const handleCellClick = useCallback(async (index) => {
    if (board[index] !== '' || !gameActive || !isPlayerTurn) {
      // Play cant-click sound for taken cells
      if (window.gameSounds && board[index] !== '') {
        window.gameSounds.playCantClick()
      }
      return
    }
    
    // Play click sound for valid moves
    if (window.gameSounds) {
      window.gameSounds.playClick()
    }
    
    // Make player move
    dispatch(makeMove({ index, player: currentPlayer }))
    const newBoard = [...board]
    newBoard[index] = currentPlayer
    
    // Check if player won
    if (checkWinner(newBoard, currentPlayer)) {
      handleGameEnd(currentPlayer)
      return
    }
    
    // Check for draw
    if (newBoard.every(cell => cell !== '')) {
      handleGameEnd('draw')
      return
    }
    
    // Switch to AI turn
    dispatch(switchPlayer())
    dispatch(setIsPlayerTurn(false))
    displaySlideMessage('AI IS THINKING...', 1000)
    
    // AI makes move after delay
    setTimeout(() => {
      makeAIMove(newBoard)
    }, 1000)
    
  }, [board, gameActive, isPlayerTurn, currentPlayer, dispatch, checkWinner, handleGameEnd, displaySlideMessage])

  // AI move logic
  const makeAIMove = useCallback(async (currentBoard) => {
    // Get available moves
    const availableMoves = []
    for (let i = 0; i < 9; i++) {
      if (currentBoard[i] === '') {
        availableMoves.push(i)
      }
    }
    
    if (availableMoves.length === 0) return
    
    let aiMove
    
    // Try API if available and in AI mode
    if (apiAvailable && gameMode === 'ai') {
      const apiResult = await getAIMoveFromAPI(currentBoard)
      if (apiResult && typeof apiResult.move === 'number') {
        aiMove = apiResult.move
      }
    }
    
    // Fallback to random move
    if (aiMove === null || aiMove === undefined) {
      aiMove = availableMoves[Math.floor(Math.random() * availableMoves.length)]
    }
    
    // Make AI move
    dispatch(makeMove({ index: aiMove, player: 'O' }))
    const newBoard = [...currentBoard]
    newBoard[aiMove] = 'O'
    
    // Check if AI won
    if (checkWinner(newBoard, 'O')) {
      console.log('[AI] AI wins! Calling handleGameEnd')
      // Play game over sound when AI wins
      if (window.gameSounds) {
        window.gameSounds.playGameOver()
      }
      setTimeout(() => {
        handleGameEnd('O')
      }, 100)
      return
    }
    
    // Check for draw
    if (newBoard.every(cell => cell !== '')) {
      console.log('[AI] Draw! Calling handleGameEnd')
      setTimeout(() => {
        handleGameEnd('draw')
      }, 100)
      return
    }
    
    // Switch back to player
    dispatch(switchPlayer())
    dispatch(setIsPlayerTurn(true))
    displaySlideMessage(`${playerNames.X}'S TURN`, 2000)
    
  }, [apiAvailable, gameMode, dispatch, getAIMoveFromAPI, checkWinner, handleGameEnd, playerNames, displaySlideMessage])

  // Handle human vs human mode
  const handleCellClickHuman = useCallback((index) => {
    if (board[index] !== '' || !gameActive) {
      // Play cant-click sound for taken cells
      if (window.gameSounds && board[index] !== '') {
        window.gameSounds.playCantClick()
      }
      return
    }
    
    // Play click sound for valid moves
    if (window.gameSounds) {
      window.gameSounds.playClick()
    }
    
    // Make move for current player
    dispatch(makeMove({ index, player: currentPlayer }))
    const newBoard = [...board]
    newBoard[index] = currentPlayer
    
    // Check if current player won
    if (checkWinner(newBoard, currentPlayer)) {
      handleGameEnd(currentPlayer)
      return
    }
    
    // Check for draw
    if (newBoard.every(cell => cell !== '')) {
      handleGameEnd('draw')
      return
    }
    
    // Switch player
    dispatch(switchPlayer())
    const nextPlayer = currentPlayer === 'X' ? 'O' : 'X'
    displaySlideMessage(`${playerNames[nextPlayer]}'S TURN`, 2000)
    
  }, [board, gameActive, currentPlayer, dispatch, checkWinner, handleGameEnd, playerNames, displaySlideMessage])

  const handleReset = () => {
    dispatch(resetGameAction())
    setShowWinModalState(false)
    gameEndingRef.current = false
    displaySlideMessage('GAME RESET!', 1500)
  }

  const handleBackToMain = () => {
    setShowWinModalState(false)
    gameEndingRef.current = false
    navigate('/')
  }

  console.log('[RENDER] showWinModalState:', showWinModalState, 'winMessage:', winMessage)
  
  return (
    <>
      <GameScreen 
        show={gameActive || showWinModalState}
        board={board}
        scores={scores}
        playerNames={playerNames}
        onCellClick={gameMode === 'ai' ? handleCellClick : handleCellClickHuman}
        onResetGame={handleReset}
        onBackToMain={handleBackToMain}
      />
      
      <WinModal 
        show={showWinModalState}
        message={winMessage}
        onPlayAgain={handleReset}
        onNewGame={handleBackToMain}
      />
    </>
  )
}

export default GamePage

