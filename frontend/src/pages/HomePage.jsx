import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { startGame } from '../store/slices/gameSlice'
import { showSlideMessage, hideSlideMessage, setLastDifficulty, setLastGameMode } from '../store/slices/settingsSlice'

const HomePage = () => {
  const lastDifficulty = useSelector(state => state.settings.lastDifficulty)
  const lastGameMode = useSelector(state => state.settings.lastGameMode)
  const theme = useSelector(state => state.settings.theme)
  
  const [playerName, setPlayerName] = useState('')
  const [player2Name, setPlayer2Name] = useState('')
  const [difficulty, setDifficulty] = useState(lastDifficulty)
  const [gameMode, setGameMode] = useState(lastGameMode)
  const navigate = useNavigate()
  const dispatch = useDispatch()
  
  // Get the appropriate logo based on theme
  const getLogoSrc = () => {
    // Use a stable cache busting parameter that doesn't change on navigation
    const cacheBuster = 'v1.0.0' // This stays the same across page navigations
    switch(theme) {
      case 'silver-frost':
        return `./images/tictactoe-silver-frost.png?v=${cacheBuster}`
      case 'neon-cyber':
        return `./images/tictactoe-neon-cyber.png?v=${cacheBuster}`
      case 'arcade':
      default:
        return `./images/tictactoe.png?v=${cacheBuster}`
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const name = playerName.trim().toUpperCase() || 'PLAYER 1'
    const name2 = gameMode === 'human' 
      ? (player2Name.trim().toUpperCase() || 'PLAYER 2')
      : 'AI'
    
    // Save the selected difficulty and game mode for next time
    dispatch(setLastDifficulty(difficulty))
    dispatch(setLastGameMode(gameMode))
    
    dispatch(startGame({ 
      playerName: name,
      player2Name: name2,
      difficulty, 
      gameMode 
    }))
    
    // Play start sound when game begins
    if (window.gameSounds) {
      window.gameSounds.playStart()
    }
    
    const difficultyText = difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
    const opponent = gameMode === 'ai' ? `${difficultyText} AI` : name2
    dispatch(showSlideMessage(`GAME STARTED! ${name} VS ${opponent}`))
    
    // Hide slide message after 2 seconds
    setTimeout(() => {
      dispatch(hideSlideMessage())
    }, 2000)
    
    navigate('/game')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  return (
    <div className="home-page">
      <div className="welcome-title">
        <img src={getLogoSrc()} alt="TIC TAC TOE" />
      </div>
      
      <div className="form-container">
        <div className="input-group">
          <label className="input-label">{gameMode === 'human' ? 'PLAYER 1' : 'PLAYER NAME'}</label>
          <input 
            type="text" 
            className="pixel-input" 
            placeholder="ENTER NAME" 
            maxLength="12"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            onKeyPress={handleKeyPress}
          />
        </div>
        
        {gameMode === 'human' && (
          <div className="input-group">
            <label className="input-label">PLAYER 2</label>
            <input 
              type="text" 
              className="pixel-input" 
              placeholder="ENTER NAME" 
              maxLength="12"
              value={player2Name}
              onChange={(e) => setPlayer2Name(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>
        )}
        
        <div className="input-group">
          <label className="input-label">GAME MODE</label>
          <div className="mode-selector">
            <button 
              className={`mode-btn ${gameMode === 'ai' ? 'active' : ''}`}
              onClick={() => setGameMode('ai')}
              type="button"
            >
              VS AI
            </button>
            <button 
              className={`mode-btn ${gameMode === 'human' ? 'active' : ''}`}
              onClick={() => setGameMode('human')}
              type="button"
            >
              VS FRIEND
            </button>
          </div>
        </div>
        
        {gameMode === 'ai' && (
          <div className="input-group">
            <label className="input-label">DIFFICULTY</label>
            <div className="difficulty-selector">
              <button 
                className={`diff-btn ${difficulty === 'easy' ? 'active' : ''}`}
                onClick={() => setDifficulty('easy')}
                type="button"
              >
                EASY
              </button>
              <button 
                className={`diff-btn ${difficulty === 'medium' ? 'active' : ''}`}
                onClick={() => setDifficulty('medium')}
                type="button"
              >
                MEDIUM
              </button>
              <button 
                className={`diff-btn ${difficulty === 'hard' ? 'active' : ''}`}
                onClick={() => setDifficulty('hard')}
                type="button"
              >
                HARD
              </button>
            </div>
          </div>
        )}
        
        <button 
          className="start-btn" 
          onClick={handleSubmit}
        >
          START GAME
        </button>
      </div>
    </div>
  )
}

export default HomePage

