import React, { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { setTheme, setSoundEnabled, setAnimationSpeed, setSoundVolume, setMusicVolume, setMusicEnabled } from '../store/slices/settingsSlice'

const SettingsPage = () => {
  const dispatch = useDispatch()
  const settings = useSelector((state) => state.settings)
  const { theme, soundEnabled, musicEnabled, animationSpeed } = settings
  const soundVolume = settings.soundVolume ?? 70
  const musicVolume = settings.musicVolume ?? 50

  useEffect(() => {
    console.log('[SettingsPage] Settings state:', settings)
    console.log('[SettingsPage] soundVolume:', soundVolume, 'musicVolume:', musicVolume)
  }, [settings, soundVolume, musicVolume])

  return (
    <div className="settings-page">
      <h1 className="page-title">SETTINGS</h1>
      
      <div className="settings-container">
        <div className="setting-section">
          <h2 className="setting-label">THEME</h2>
          <div className="setting-options">
                    <button
                      className={`setting-btn ${theme === 'arcade' ? 'active' : ''}`}
                      onClick={() => dispatch(setTheme('arcade'))}
                    >
                      ARCADE
                    </button>
                    <button
                      className={`setting-btn ${theme === 'silver-frost' ? 'active' : ''}`}
                      onClick={() => dispatch(setTheme('silver-frost'))}
                    >
                      SILVER FROST
                    </button>
                    <button
                      className={`setting-btn ${theme === 'neon-cyber' ? 'active' : ''}`}
                      onClick={() => dispatch(setTheme('neon-cyber'))}
                    >
                      NEON CYBER
                    </button>
          </div>
        </div>
        
        <div className="setting-section">
          <h2 className="setting-label">SOUND EFFECTS</h2>
          <div className="setting-options">
            <button 
              className={`setting-btn ${soundEnabled ? 'active' : ''}`}
              onClick={() => dispatch(setSoundEnabled(true))}
            >
              ON
            </button>
            <button 
              className={`setting-btn ${!soundEnabled ? 'active' : ''}`}
              onClick={() => dispatch(setSoundEnabled(false))}
            >
              OFF
            </button>
          </div>
          
          <div className="volume-controls">
            <div className="volume-control">
              <label className="volume-label">
                SOUND EFFECTS VOLUME: {soundVolume}%
              </label>
              <input 
                type="range"
                min="0"
                max="100"
                value={soundVolume}
                onChange={(e) => dispatch(setSoundVolume(Number(e.target.value)))}
                className="volume-slider"
                disabled={!soundEnabled}
              />
            </div>
          </div>
        </div>
        
        <div className="setting-section">
          <h2 className="setting-label">BACKGROUND MUSIC</h2>
          <div className="setting-options">
            <button 
              className={`setting-btn ${musicEnabled ? 'active' : ''}`}
              onClick={() => dispatch(setMusicEnabled(true))}
            >
              ON
            </button>
            <button 
              className={`setting-btn ${!musicEnabled ? 'active' : ''}`}
              onClick={() => dispatch(setMusicEnabled(false))}
            >
              OFF
            </button>
          </div>
          
          <div className="volume-controls">
            <div className="volume-control">
              <label className="volume-label">
                MUSIC VOLUME: {musicVolume}%
              </label>
              <input 
                type="range"
                min="0"
                max="100"
                value={musicVolume}
                onChange={(e) => dispatch(setMusicVolume(Number(e.target.value)))}
                className="volume-slider"
                disabled={!musicEnabled}
              />
            </div>
          </div>
        </div>
        
        <div className="setting-section">
          <h2 className="setting-label">ANIMATION SPEED</h2>
          <div className="setting-options">
            <button 
              className={`setting-btn ${animationSpeed === 'slow' ? 'active' : ''}`}
              onClick={() => dispatch(setAnimationSpeed('slow'))}
            >
              SLOW
            </button>
            <button 
              className={`setting-btn ${animationSpeed === 'normal' ? 'active' : ''}`}
              onClick={() => dispatch(setAnimationSpeed('normal'))}
            >
              NORMAL
            </button>
            <button 
              className={`setting-btn ${animationSpeed === 'fast' ? 'active' : ''}`}
              onClick={() => dispatch(setAnimationSpeed('fast'))}
            >
              FAST
            </button>
          </div>
        </div>
        
        <div className="setting-info">
          <p>Settings are automatically saved to your browser.</p>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage

