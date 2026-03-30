import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { clearHistory } from '../store/slices/historySlice'
import { ACHIEVEMENTS, resetAchievements } from '../store/slices/achievementsSlice'
import { resetScores } from '../store/slices/gameSlice'
import ConfirmModal from '../components/ConfirmModal'

const HistoryPage = () => {
  const dispatch = useDispatch()
  const history = useSelector((state) => state.history)
  const achievements = useSelector((state) => state.achievements)
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [visibleGames, setVisibleGames] = useState(5)
  
  const winRate = history.totalGames > 0 
    ? ((history.wins / history.totalGames) * 100).toFixed(1)
    : 0
  
  const handleShowMore = () => {
    setVisibleGames(prev => prev + 5)
  }
  
  const displayedGames = history.games.slice(0, visibleGames)
  const hasMoreGames = visibleGames < history.games.length

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatDate = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="history-page">
      <h1 className="page-title">GAME HISTORY</h1>
      
      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-label">TOTAL GAMES</div>
          <div className="stat-value">{history.totalGames}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">WIN RATE</div>
          <div className="stat-value">{winRate}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">BEST STREAK</div>
          <div className="stat-value">{history.bestStreak}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">WINS</div>
          <div className="stat-value win">{history.wins}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">DRAWS</div>
          <div className="stat-value draw">{history.draws}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">LOSSES</div>
          <div className="stat-value loss">{history.losses}</div>
        </div>
      </div>
      
      <div className="difficulty-stats">
        <h2 className="section-title">PERFORMANCE BY DIFFICULTY</h2>
        <div className="difficulty-cards">
          <div className="difficulty-card">
            <div className="difficulty-name">EASY</div>
            <div className="difficulty-stats-row">
              <span>Wins: {history.statsByDifficulty.easy.wins}</span>
              <span>Losses: {history.statsByDifficulty.easy.losses}</span>
              <span>Draws: {history.statsByDifficulty.easy.draws}</span>
            </div>
          </div>
          <div className="difficulty-card">
            <div className="difficulty-name">MEDIUM</div>
            <div className="difficulty-stats-row">
              <span>Wins: {history.statsByDifficulty.medium.wins}</span>
              <span>Losses: {history.statsByDifficulty.medium.losses}</span>
              <span>Draws: {history.statsByDifficulty.medium.draws}</span>
            </div>
          </div>
          <div className="difficulty-card">
            <div className="difficulty-name">HARD</div>
            <div className="difficulty-stats-row">
              <span>Wins: {history.statsByDifficulty.hard.wins}</span>
              <span>Losses: {history.statsByDifficulty.hard.losses}</span>
              <span>Draws: {history.statsByDifficulty.hard.draws}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="achievements-section">
        <h2 className="section-title">ACHIEVEMENTS</h2>
        <div className="achievements-grid">
          {Object.values(ACHIEVEMENTS).map((achievement) => {
            const isUnlocked = achievements.unlocked.includes(achievement.id)
            return (
              <div 
                key={achievement.id}
                className={`achievement-card ${isUnlocked ? 'unlocked' : 'locked'}`}
              >
                <div className="achievement-icon">
                  <img src={achievement.icon} alt={achievement.name} />
                </div>
                <div className="achievement-name">{achievement.name}</div>
                <div className="achievement-desc">{achievement.description}</div>
              </div>
            )
          })}
        </div>
      </div>
      
      <div className="recent-games">
        <h2 className="section-title">RECENT GAMES</h2>
        {history.games.length === 0 ? (
          <div className="no-games">No games played yet!</div>
        ) : (
          <>
            <div className="games-list">
              {displayedGames.map((game, index) => (
                <div key={index} className={`game-item ${game.result}`}>
                  <div className="game-result">
                    {game.result === 'win' && '🏆 WIN'}
                    {game.result === 'loss' && '❌ LOSS'}
                    {game.result === 'draw' && '🤝 DRAW'}
                  </div>
                  <div className="game-details">
                    <span>{game.playerName} vs {game.opponent}</span>
                    <span className="game-meta">
                      {game.difficulty !== 'human' && `${game.difficulty.toUpperCase()} • `}
                      {formatDuration(game.duration)} • {game.moves} moves
                    </span>
                    <span className="game-date">{formatDate(game.date)}</span>
                  </div>
                </div>
              ))}
            </div>
            {hasMoreGames && (
              <button 
                className="show-more-btn"
                onClick={handleShowMore}
              >
                SHOW MORE ({history.games.length - visibleGames} MORE)
              </button>
            )}
          </>
        )}
      </div>
      
      {history.totalGames > 0 && (
        <>
          <button 
            className="clear-history-btn"
            onClick={() => setShowConfirmModal(true)}
          >
            CLEAR HISTORY
          </button>
          
          <ConfirmModal
            show={showConfirmModal}
            title="CLEAR HISTORY?"
            message="Are you sure you want to clear all game history, achievements, and scores? This action cannot be undone."
            onConfirm={() => {
              dispatch(clearHistory())
              dispatch(resetAchievements())
              dispatch(resetScores())
              setShowConfirmModal(false)
            }}
            onCancel={() => setShowConfirmModal(false)}
          />
        </>
      )}
    </div>
  )
}

export default HistoryPage

