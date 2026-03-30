import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import PropTypes from 'prop-types'

const Navigation = ({ isInGame }) => {
  const location = useLocation()
  
  // When there are 5 links (isInGame = true), display in 2 rows
  // When there are 4 links (isInGame = false), display in 1 row
  
  if (isInGame) {
    // 5 links: Row 1: [HOME][HISTORY], Row 2: [GAME][SETTINGS][ABOUT]
    return (
      <nav className="navigation">
        <div className="nav-links nav-links-two-rows">
          <div className="nav-row">
            <Link 
              to="/" 
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              HOME
            </Link>
            <Link 
              to="/history" 
              className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}
            >
              HISTORY
            </Link>
          </div>
          <div className="nav-row">
            <Link 
              to="/game" 
              className={`nav-link ${location.pathname === '/game' ? 'active' : ''}`}
            >
              GAME
            </Link>
            <Link 
              to="/settings" 
              className={`nav-link ${location.pathname === '/settings' ? 'active' : ''}`}
            >
              SETTINGS
            </Link>
            <Link 
              to="/about" 
              className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}
            >
              ABOUT
            </Link>
          </div>
        </div>
      </nav>
    )
  }
  
  // 4 links: Single row: [HOME][HISTORY][SETTINGS][ABOUT]
  return (
    <nav className="navigation">
      <div className="nav-links nav-links-single-row">
        <Link 
          to="/" 
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          HOME
        </Link>
        <Link 
          to="/history" 
          className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}
        >
          HISTORY
        </Link>
        <Link 
          to="/settings" 
          className={`nav-link ${location.pathname === '/settings' ? 'active' : ''}`}
        >
          SETTINGS
        </Link>
        <Link 
          to="/about" 
          className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}
        >
          ABOUT
        </Link>
      </div>
    </nav>
  )
}

Navigation.propTypes = {
  isInGame: PropTypes.bool
}

Navigation.defaultProps = {
  isInGame: false
}

export default Navigation

