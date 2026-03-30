import React from 'react'
import PropTypes from 'prop-types'

const WinModal = ({ show, message, onPlayAgain, onNewGame }) => {
  if (!show) return null

  return (
    <div className="win-modal active">
      <div className="win-modal-content">
        <div className="win-message">{message}</div>
        <button className="play-again-btn" onClick={onPlayAgain}>
          PLAY AGAIN
        </button>
        <button className="play-again-btn new-game-btn" onClick={onNewGame}>
          BACK TO MAIN
        </button>
      </div>
    </div>
  )
}

WinModal.propTypes = {
  show: PropTypes.bool.isRequired,
  message: PropTypes.string.isRequired,
  onPlayAgain: PropTypes.func.isRequired,
  onNewGame: PropTypes.func.isRequired
}

export default WinModal
