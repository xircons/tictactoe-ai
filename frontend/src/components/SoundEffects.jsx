import React, { useRef, useEffect } from 'react'
import { useSelector } from 'react-redux'

const SoundEffects = () => {
  const clickSoundRef = useRef(null)
  const cantClickSoundRef = useRef(null)
  const gameOverSoundRef = useRef(null)
  const startSoundRef = useRef(null)
  
  const { soundEnabled, soundVolume } = useSelector((state) => state.settings)

  // Set volume for all sounds when settings change
  useEffect(() => {
    const sounds = [clickSoundRef, cantClickSoundRef, gameOverSoundRef, startSoundRef]
    sounds.forEach(soundRef => {
      if (soundRef.current) {
        soundRef.current.volume = soundVolume / 100
      }
    })
  }, [soundVolume])

  // Play click sound
  const playClick = () => {
    console.log('[SOUND DEBUG] playClick called, soundEnabled:', soundEnabled, 'volume:', soundVolume)
    if (soundEnabled && clickSoundRef.current) {
      clickSoundRef.current.currentTime = 0
      clickSoundRef.current.play().catch(error => {
        console.warn('[SOUND] Click sound error:', error)
      })
    } else {
      console.log('[SOUND DEBUG] Click sound not played - soundEnabled:', soundEnabled, 'ref exists:', !!clickSoundRef.current)
    }
  }

  // Play cant-click sound
  const playCantClick = () => {
    if (soundEnabled && cantClickSoundRef.current) {
      cantClickSoundRef.current.currentTime = 0
      cantClickSoundRef.current.play().catch(error => {
        console.warn('[SOUND] Cant-click sound error:', error)
      })
    }
  }

  // Play game over sound
  const playGameOver = () => {
    if (soundEnabled && gameOverSoundRef.current) {
      gameOverSoundRef.current.currentTime = 0
      gameOverSoundRef.current.play().catch(error => {
        console.warn('[SOUND] Game over sound error:', error)
      })
    }
  }

  // Play start sound
  const playStart = () => {
    if (soundEnabled && startSoundRef.current) {
      startSoundRef.current.currentTime = 0
      startSoundRef.current.play().catch(error => {
        console.warn('[SOUND] Start sound error:', error)
      })
    }
  }

  // Expose sound functions globally for easy access
  useEffect(() => {
    window.gameSounds = {
      playClick,
      playCantClick,
      playGameOver,
      playStart
    }
    
    return () => {
      delete window.gameSounds
    }
  }, [soundEnabled])

  return (
    <>
      <audio ref={clickSoundRef} preload="auto">
        <source src="./sounds/sound-effect/click.mp3?v=1.0.0" type="audio/mpeg" />
      </audio>
      
      <audio ref={cantClickSoundRef} preload="auto">
        <source src="./sounds/sound-effect/cant-click.mp3?v=1.0.0" type="audio/mpeg" />
      </audio>
      
      <audio ref={gameOverSoundRef} preload="auto">
        <source src="./sounds/sound-effect/game-over.mp3?v=1.0.0" type="audio/mpeg" />
      </audio>
      
      <audio ref={startSoundRef} preload="auto">
        <source src="./sounds/sound-effect/start.mp3?v=1.0.0" type="audio/mpeg" />
      </audio>
    </>
  )
}

export default SoundEffects
