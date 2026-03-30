import React, { useState } from 'react'
import PropTypes from 'prop-types'

const NameEntryScreen = ({ show, onStartGame }) => {
  const [playerName, setPlayerName] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onStartGame(playerName)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  if (!show) return null

  return (
    <div className="name-entry-screen">
      <div className="welcome-title">TIC<br />TAC<br />TOE</div>
      <div className="form-container">
        <div>
          <label className="input-label">PLAYER NAME</label>
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

NameEntryScreen.propTypes = {
  show: PropTypes.bool.isRequired,
  onStartGame: PropTypes.func.isRequired
}

export default NameEntryScreen
