import React, { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import PropTypes from 'prop-types'
import { clearRecentlyUnlocked, ACHIEVEMENTS } from '../store/slices/achievementsSlice'

const AchievementNotification = () => {
  const dispatch = useDispatch()
  const recentlyUnlocked = useSelector((state) => state.achievements.recentlyUnlocked)
  
  useEffect(() => {
    if (recentlyUnlocked) {
      const timer = setTimeout(() => {
        dispatch(clearRecentlyUnlocked())
      }, 5000)
      
      return () => clearTimeout(timer)
    }
  }, [recentlyUnlocked, dispatch])
  
  if (!recentlyUnlocked) return null
  
  const achievement = ACHIEVEMENTS[Object.keys(ACHIEVEMENTS).find(
    key => ACHIEVEMENTS[key].id === recentlyUnlocked
  )]
  
  if (!achievement) return null
  
  return (
    <div className="achievement-notification">
      <div className="achievement-notification-content">
        <div className="achievement-notification-icon">
          <img src={achievement.icon} alt={achievement.name} />
        </div>
        <div className="achievement-notification-text">
          <div className="achievement-notification-title">ACHIEVEMENT UNLOCKED!</div>
          <div className="achievement-notification-name">{achievement.name}</div>
          <div className="achievement-notification-desc">{achievement.description}</div>
        </div>
      </div>
    </div>
  )
}

AchievementNotification.propTypes = {}

export default AchievementNotification

