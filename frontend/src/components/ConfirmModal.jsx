import React from 'react'
import PropTypes from 'prop-types'

const ConfirmModal = ({ show, title, message, onConfirm, onCancel }) => {
  if (!show) return null

  return (
    <div className="win-modal active">
      <div className="win-modal-content">
        <div className="confirm-title">{title}</div>
        <div className="confirm-message">{message}</div>
        <div className="confirm-buttons">
          <button className="play-again-btn" onClick={onConfirm}>
            YES
          </button>
          <button className="play-again-btn new-game-btn" onClick={onCancel}>
            NO
          </button>
        </div>
      </div>
    </div>
  )
}

ConfirmModal.propTypes = {
  show: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired
}

export default ConfirmModal

