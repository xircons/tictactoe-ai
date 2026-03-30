import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  theme: 'arcade', // 'arcade', 'silver-frost', 'neon-cyber'
  soundEnabled: false, // Sound effects disabled by default
  soundVolume: 50, // 0-100
  musicEnabled: false, // Background music disabled by default
  musicVolume: 50, // 0-100
  animationSpeed: 'normal', // 'slow', 'normal', 'fast'
  playerAvatar: 'default',
  showSlideMessage: false,
  slideMessage: '',
  lastDifficulty: 'hard', // Remember last selected difficulty
  lastGameMode: 'ai' // Remember last selected game mode
}

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.theme = action.payload
    },
    setSoundEnabled: (state, action) => {
      state.soundEnabled = action.payload
    },
    setMusicEnabled: (state, action) => {
      state.musicEnabled = action.payload
    },
    setAnimationSpeed: (state, action) => {
      state.animationSpeed = action.payload
    },
    setPlayerAvatar: (state, action) => {
      state.playerAvatar = action.payload
    },
    showSlideMessage: (state, action) => {
      state.showSlideMessage = true
      state.slideMessage = action.payload
    },
    hideSlideMessage: (state) => {
      state.showSlideMessage = false
    },
    toggleSound: (state) => {
      state.soundEnabled = !state.soundEnabled
    },
    toggleMusic: (state) => {
      state.musicEnabled = !state.musicEnabled
    },
    setSoundVolume: (state, action) => {
      state.soundVolume = action.payload
    },
    setMusicVolume: (state, action) => {
      state.musicVolume = action.payload
    },
    setLastDifficulty: (state, action) => {
      state.lastDifficulty = action.payload
    },
    setLastGameMode: (state, action) => {
      state.lastGameMode = action.payload
    }
  }
})

export const {
  setTheme,
  setSoundEnabled,
  setMusicEnabled,
  setAnimationSpeed,
  setPlayerAvatar,
  showSlideMessage,
  hideSlideMessage,
  toggleSound,
  toggleMusic,
  setSoundVolume,
  setMusicVolume,
  setLastDifficulty,
  setLastGameMode
} = settingsSlice.actions

export default settingsSlice.reducer

