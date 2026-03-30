import { createSlice } from '@reduxjs/toolkit'

// Define all achievements with icon paths
const cacheBuster = 'v1.0.0' // Stable cache busting that doesn't change on navigation
export const ACHIEVEMENTS = {
  FIRST_STEPS: {
    id: 'first_steps',
    name: 'First Steps',
    description: 'Complete your first game',
    icon: `./icons/one.png?v=${cacheBuster}`,
    requirement: { type: 'games_played', count: 1 }
  },
  WINNER: {
    id: 'winner',
    name: 'Winner',
    description: 'Win your first game',
    icon: `./icons/star.png?v=${cacheBuster}`,
    requirement: { type: 'wins', count: 1 }
  },
  DEDICATED: {
    id: 'dedicated',
    name: 'Dedicated',
    description: 'Win 5 games',
    icon: `./icons/boy.png?v=${cacheBuster}`,
    requirement: { type: 'wins', count: 5 }
  },
  CHAMPION: {
    id: 'champion',
    name: 'Champion',
    description: 'Win 10 games',
    icon: `./icons/confetti.png?v=${cacheBuster}`,
    requirement: { type: 'wins', count: 10 }
  },
  UNSTOPPABLE: {
    id: 'unstoppable',
    name: 'Unstoppable',
    description: 'Win 3 games in a row',
    icon: `./icons/arrowheads.png?v=${cacheBuster}`,
    requirement: { type: 'win_streak', count: 3 }
  },
  CHALLENGER: {
    id: 'challenger',
    name: 'Challenger',
    description: 'Beat Hard AI once',
    icon: `./icons/alien-pixelated-shape-of-a-digital-game.png?v=${cacheBuster}`,
    requirement: { type: 'hard_ai_win', count: 1 }
  },
  MARATHON: {
    id: 'marathon',
    name: 'Marathon',
    description: 'Play 25 games total',
    icon: `./icons/key.png?v=${cacheBuster}`,
    requirement: { type: 'games_played', count: 25 }
  },
  LEGEND: {
    id: 'legend',
    name: 'Legend',
    description: 'Win 25 games',
    icon: `./icons/light.png?v=${cacheBuster}`,
    requirement: { type: 'wins', count: 25 }
  }
}

const initialState = {
  unlocked: [], // Array of achievement IDs
  progress: {
    games_played: 0,
    wins: 0,
    win_streak: 0,
    hard_ai_wins: 0
  },
  recentlyUnlocked: null // For showing notification
}

const achievementsSlice = createSlice({
  name: 'achievements',
  initialState,
  reducers: {
    updateProgress: (state, action) => {
      const { gameResult, currentStreak, totalGames, totalWins } = action.payload
      
      // Update progress counters
      state.progress.games_played = totalGames
      state.progress.wins = totalWins
      state.progress.win_streak = currentStreak
      
      // Track hard AI wins
      if (gameResult.result === 'win' && gameResult.difficulty === 'hard') {
        state.progress.hard_ai_wins = (state.progress.hard_ai_wins || 0) + 1
      }
      
      // Check for newly unlocked achievements
      Object.values(ACHIEVEMENTS).forEach(achievement => {
        if (!state.unlocked.includes(achievement.id)) {
          let isUnlocked = false
          
          switch (achievement.requirement.type) {
            case 'games_played':
              isUnlocked = state.progress.games_played >= achievement.requirement.count
              break
            case 'wins':
              isUnlocked = state.progress.wins >= achievement.requirement.count
              break
            case 'win_streak':
              isUnlocked = state.progress.win_streak >= achievement.requirement.count
              break
            case 'hard_ai_win':
              isUnlocked = (state.progress.hard_ai_wins || 0) >= achievement.requirement.count
              break
          }
          
          if (isUnlocked) {
            state.unlocked.push(achievement.id)
            state.recentlyUnlocked = achievement.id
          }
        }
      })
    },
    clearRecentlyUnlocked: (state) => {
      state.recentlyUnlocked = null
    },
    resetAchievements: (state) => {
      return initialState
    }
  }
})

export const { updateProgress, clearRecentlyUnlocked, resetAchievements } = achievementsSlice.actions

export default achievementsSlice.reducer

