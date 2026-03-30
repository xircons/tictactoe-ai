import { configureStore } from '@reduxjs/toolkit'
import gameReducer from './slices/gameSlice'
import settingsReducer from './slices/settingsSlice'
import historyReducer from './slices/historySlice'
import achievementsReducer from './slices/achievementsSlice'

// Load state from localStorage
const loadState = () => {
  try {
    const serializedState = localStorage.getItem('tictactoe_state')
    if (serializedState === null) {
      return undefined
    }
    return JSON.parse(serializedState)
  } catch (err) {
    console.error('Error loading state from localStorage:', err)
    return undefined
  }
}

// Save state to localStorage
const saveState = (state) => {
  try {
    const serializedState = JSON.stringify({
      settings: state.settings,
      history: state.history,
      achievements: state.achievements
      // Don't persist game state - fresh game on reload
    })
    localStorage.setItem('tictactoe_state', serializedState)
  } catch (err) {
    console.error('Error saving state to localStorage:', err)
  }
}

// Create the store
const store = configureStore({
  reducer: {
    game: gameReducer,
    settings: settingsReducer,
    history: historyReducer,
    achievements: achievementsReducer
  },
  preloadedState: loadState()
})

// Subscribe to store changes and save to localStorage
store.subscribe(() => {
  saveState(store.getState())
})

export default store

