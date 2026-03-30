import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  games: [], // Array of game results
  totalGames: 0,
  wins: 0,
  losses: 0,
  draws: 0,
  currentStreak: 0,
  bestStreak: 0,
  statsByDifficulty: {
    easy: { wins: 0, losses: 0, draws: 0 },
    medium: { wins: 0, losses: 0, draws: 0 },
    hard: { wins: 0, losses: 0, draws: 0 }
  }
}

const historySlice = createSlice({
  name: 'history',
  initialState,
  reducers: {
    addGame: (state, action) => {
      const gameResult = action.payload
      // Add to games array
      state.games.unshift(gameResult) // Add to beginning
      
      // Keep only last 50 games
      if (state.games.length > 50) {
        state.games = state.games.slice(0, 50)
      }
      
      // Update totals
      state.totalGames += 1
      
      if (gameResult.result === 'win') {
        state.wins += 1
        state.currentStreak += 1
        if (state.currentStreak > state.bestStreak) {
          state.bestStreak = state.currentStreak
        }
        
        // Update difficulty stats
        if (gameResult.difficulty && state.statsByDifficulty[gameResult.difficulty]) {
          state.statsByDifficulty[gameResult.difficulty].wins += 1
        }
      } else if (gameResult.result === 'loss') {
        state.losses += 1
        state.currentStreak = 0
        
        // Update difficulty stats
        if (gameResult.difficulty && state.statsByDifficulty[gameResult.difficulty]) {
          state.statsByDifficulty[gameResult.difficulty].losses += 1
        }
      } else if (gameResult.result === 'draw') {
        state.draws += 1
        state.currentStreak = 0
        
        // Update difficulty stats
        if (gameResult.difficulty && state.statsByDifficulty[gameResult.difficulty]) {
          state.statsByDifficulty[gameResult.difficulty].draws += 1
        }
      }
    },
    clearHistory: (state) => {
      return initialState
    }
  }
})

export const { addGame, clearHistory } = historySlice.actions

export default historySlice.reducer

