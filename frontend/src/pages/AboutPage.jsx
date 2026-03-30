import React from 'react'

const AboutPage = () => {
  return (
    <div className="about-page">
      <h1 className="page-title">ABOUT</h1>
      
      <div className="about-container">
        <div className="about-section">
          <h2 className="about-heading">TIC-TAC-TOE AI</h2>
          <p className="about-text">
            A modern implementation of the classic Tic-Tac-Toe game featuring 
            multiple AI difficulty levels powered by advanced algorithms.
          </p>
        </div>
        
        <div className="about-section">
          <h2 className="about-heading">AI DIFFICULTY LEVELS</h2>
          <div className="difficulty-info">
            <div className="info-item">
              <span className="info-label">EASY</span>
              <p>Random moves - Perfect for beginners</p>
            </div>
            <div className="info-item">
              <span className="info-label">MEDIUM</span>
              <p>Strategic heuristic AI - Moderate challenge</p>
            </div>
            <div className="info-item">
              <span className="info-label">HARD</span>
              <p>Perfect Minimax AI - Unbeatable opponent</p>
            </div>
          </div>
        </div>
        
        <div className="about-section">
          <h2 className="about-heading">FEATURES</h2>
          <ul className="features-list">
            <li>Multiple AI difficulty levels</li>
            <li>Human vs Human mode</li>
            <li>Game statistics tracking</li>
            <li>Achievement system</li>
            <li>Customizable themes</li>
            <li>Persistent game history</li>
            <li>Responsive design</li>
          </ul>
        </div>
        
        <div className="about-section">
          <h2 className="about-heading">TECHNOLOGY</h2>
          <ul className="tech-list">
            <li>React 18 with Hooks</li>
            <li>Redux Toolkit for state management</li>
            <li>React Router for navigation</li>
            <li>Python Flask backend</li>
            <li>Minimax algorithm with Alpha-Beta pruning</li>
          </ul>
        </div>
        
        <div className="about-section">
          <h2 className="about-heading">HOW TO PLAY</h2>
          <ol className="instructions-list">
            <li>Enter your name on the home screen</li>
            <li>Choose your game mode (vs AI or vs FRIEND)</li>
            <li>Select AI difficulty level (if playing vs AI)</li>
            <li>Click START GAME to begin</li>
            <li>Click on an empty cell to make your move</li>
            <li>Get three in a row to win!</li>
          </ol>
        </div>
        
        <div className="about-section credits">
          <h2 className="about-heading">CREDITS</h2>
          <p className="about-text">
          Coding and development by @xircons
          </p>
          <p className="about-text version">
            Version 1.0.1
          </p>
        </div>
      </div>
    </div>
  )
}

export default AboutPage

