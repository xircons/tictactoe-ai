import React from 'react'
import PropTypes from 'prop-types'

const SlideMessage = ({ message, show }) => {
  return (
    <div className={`slide-message ${show ? 'show' : 'hide'}`}>
      {message}
    </div>
  )
}

SlideMessage.propTypes = {
  message: PropTypes.string.isRequired,
  show: PropTypes.bool.isRequired
}

export default SlideMessage
