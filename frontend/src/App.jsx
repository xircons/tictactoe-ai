import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Layout from './components/Layout'
import SlideMessage from './components/SlideMessage'
import AchievementNotification from './components/AchievementNotification'
import BackgroundMusic from './components/BackgroundMusic'
import SoundEffects from './components/SoundEffects'
import HomePage from './pages/HomePage'
import GamePage from './pages/GamePage'
import SettingsPage from './pages/SettingsPage'
import HistoryPage from './pages/HistoryPage'
import AboutPage from './pages/AboutPage'

function App() {
  const { showSlideMessage, slideMessage, animationSpeed, theme } = useSelector((state) => state.settings)

  // Apply animation speed and theme to body
  useEffect(() => {
    document.body.className = `animation-speed-${animationSpeed}`
    document.body.setAttribute('data-theme', theme)
  }, [animationSpeed, theme])

  // Initialize debug logging and generate stars
  useEffect(() => {
    console.log('[GAME INIT] Tic-Tac-Toe with AI - Redux + Router Edition')
    console.log('==========================================')

    // Generate stars
    const starsContainer = document.getElementById('stars')
    if (starsContainer) {
      starsContainer.innerHTML = ''
      
      for (let i = 0; i < 80; i++) {
        const star = document.createElement('div')
        star.className = 'star'
        star.style.left = Math.random() * 100 + '%'
        star.style.top = Math.random() * 100 + '%'
        star.style.animationDelay = Math.random() * 3 + 's'
        starsContainer.appendChild(star)
      }
    }

    // Add click sound to all buttons and navigation elements
    const addClickSoundsToElements = () => {
      const buttons = document.querySelectorAll('button')
      const navigationElements = document.querySelectorAll('.navigation')
      
      buttons.forEach(button => {
        // Remove existing listener to avoid duplicates
        button.removeEventListener('click', handleButtonClick)
        button.addEventListener('click', handleButtonClick)
      })
      
      navigationElements.forEach(navElement => {
        // Remove existing listener to avoid duplicates
        navElement.removeEventListener('click', handleButtonClick)
        navElement.addEventListener('click', handleButtonClick)
      })
    }

    const handleButtonClick = (e) => {
      // Play click sound for all button clicks and navigation clicks
      if (window.gameSounds) {
        window.gameSounds.playClick()
      }
    }

    // Add click sounds to existing elements
    addClickSoundsToElements()

    // Use MutationObserver to add click sounds to dynamically created elements
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if the added node is a button
            if (node.tagName === 'BUTTON') {
              node.addEventListener('click', handleButtonClick)
            }
            // Check if the added node has navigation class
            if (node.classList && node.classList.contains('navigation')) {
              node.addEventListener('click', handleButtonClick)
            }
            // Check for buttons and navigation elements within the added node
            const buttons = node.querySelectorAll && node.querySelectorAll('button')
            const navElements = node.querySelectorAll && node.querySelectorAll('.navigation')
            if (buttons) {
              buttons.forEach(button => {
                button.addEventListener('click', handleButtonClick)
              })
            }
            if (navElements) {
              navElements.forEach(navElement => {
                navElement.addEventListener('click', handleButtonClick)
              })
            }
          }
        })
      })
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true
    })

    // Cleanup
    return () => {
      observer.disconnect()
      const buttons = document.querySelectorAll('button')
      const navigationElements = document.querySelectorAll('.navigation')
      
      buttons.forEach(button => {
        button.removeEventListener('click', handleButtonClick)
      })
      
      navigationElements.forEach(navElement => {
        navElement.removeEventListener('click', handleButtonClick)
      })
    }
  }, [])

  return (
    <>
      <div className="stars" id="stars"></div>
      <BackgroundMusic />
      <SoundEffects />
      <SlideMessage 
        message={slideMessage}
        show={showSlideMessage}
      />
      <AchievementNotification />
      
      <div className="phone-container pixel-corners">
        <div className="phone-notch pixel-corners">
          <div className="phone-speaker"></div>
        </div>
        <div className="phone-screen pixel-corners">
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/game" element={<GamePage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </Layout>
        </div>
      </div>
    </>
  )
}

export default App
