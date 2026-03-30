import React from 'react'
import { useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import Navigation from './Navigation'

const Layout = ({ children }) => {
  const gameActive = useSelector((state) => state.game.gameActive)
  
  return (
    <div className={`app-layout ${gameActive ? 'in-game' : ''}`}>
      <Navigation isInGame={gameActive} />
      <div className="page-content">
        {children}
      </div>
    </div>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired
}

export default Layout

