import React, { useState } from 'react'
import { authAPI } from '../services/api'

const SettingsPage = ({ user }) => {
  const [activeTab, setActiveTab] = useState('profile')
  const [profileData, setProfileData] = useState({
    nickname: user?.nickname || '',
    phone: user?.phone || ''
  })
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    try {
      const result = await authAPI.updateCurrentUser(profileData)
      setMessage('Profile updated successfully')
      setError('')
    } catch (err) {
      setError(err.message || 'Failed to update profile')
      setMessage('')
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    
    // Validate passwords
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match')
      return
    }
    
    // In a real implementation, you would call the password change API
    // For now, we'll just show a message
    setMessage('Password change functionality would be implemented here')
    setError('')
    
    // Reset form
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
  }

  const handleProfileChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    })
  }

  const handlePasswordChangeInput = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>User Settings</h1>
      </div>

      {/* Navigation Tabs */}
      <div className="settings-tabs">
        <button 
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          Personal Information
        </button>
        <button 
          className={activeTab === 'security' ? 'active' : ''}
          onClick={() => setActiveTab('security')}
        >
          Account Security
        </button>
        <button 
          className={activeTab === 'notifications' ? 'active' : ''}
          onClick={() => setActiveTab('notifications')}
        >
          Notifications
        </button>
        <button 
          className={activeTab === 'privacy' ? 'active' : ''}
          onClick={() => setActiveTab('privacy')}
        >
          Privacy
        </button>
      </div>

      {/* Tab Content */}
      <div className="settings-content">
        {/* Personal Information Tab */}
        {activeTab === 'profile' && (
          <div className="settings-tab-content">
            <h2>Personal Information</h2>
            <form onSubmit={handleProfileUpdate}>
              <div className="form-group">
                <label htmlFor="avatar">Avatar</label>
                <div className="avatar-upload">
                  <div className="avatar-placeholder">
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt="Avatar" />
                    ) : (
                      <span>No avatar</span>
                    )}
                  </div>
                  <button type="button" className="upload-button">
                    Upload New Avatar
                  </button>
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  value={user?.username || ''}
                  readOnly
                  className="readonly"
                />
                <div className="help-text">Username cannot be changed</div>
              </div>
              
              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  value={user?.email || ''}
                  readOnly
                  className="readonly"
                />
                <div className="help-text">Email cannot be changed</div>
              </div>
              
              <div className="form-group">
                <label htmlFor="nickname">Nickname</label>
                <input
                  type="text"
                  id="nickname"
                  name="nickname"
                  value={profileData.nickname}
                  onChange={handleProfileChange}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleProfileChange}
                />
              </div>
              
              <button type="submit" className="save-button">
                Save Changes
              </button>
            </form>
          </div>
        )}

        {/* Account Security Tab */}
        {activeTab === 'security' && (
          <div className="settings-tab-content">
            <h2>Account Security</h2>
            
            <div className="security-section">
              <h3>Change Password</h3>
              <form onSubmit={handlePasswordChange}>
                <div className="form-group">
                  <label htmlFor="currentPassword">Current Password</label>
                  <input
                    type="password"
                    id="currentPassword"
                    name="currentPassword"
                    value={passwordData.currentPassword}
                    onChange={handlePasswordChangeInput}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="newPassword">New Password</label>
                  <input
                    type="password"
                    id="newPassword"
                    name="newPassword"
                    value={passwordData.newPassword}
                    onChange={handlePasswordChangeInput}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm New Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={passwordData.confirmPassword}
                    onChange={handlePasswordChangeInput}
                    required
                  />
                </div>
                
                <button type="submit" className="save-button">
                  Change Password
                </button>
              </form>
            </div>
            
            <div className="security-section">
              <h3>Login History</h3>
              <div className="login-history">
                <div className="login-item">
                  <div className="login-info">
                    <div className="login-time">2023-01-01 10:00:00</div>
                    <div className="login-location">192.168.1.100</div>
                    <div className="login-device">Chrome on Windows</div>
                  </div>
                  <div className="login-status">Current Session</div>
                </div>
                <div className="login-item">
                  <div className="login-info">
                    <div className="login-time">2022-12-31 15:30:00</div>
                    <div className="login-location">192.168.1.101</div>
                    <div className="login-device">Safari on macOS</div>
                  </div>
                  <div className="login-status">Ended</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="settings-tab-content">
            <h2>Notification Settings</h2>
            
            <div className="notification-setting">
              <div className="setting-info">
                <h3>Email Notifications</h3>
                <p>Receive important updates and announcements via email</p>
              </div>
              <div className="setting-toggle">
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
            
            <div className="notification-setting">
              <div className="setting-info">
                <h3>System Announcement Notifications</h3>
                <p>Receive notifications about system updates and maintenance</p>
              </div>
              <div className="setting-toggle">
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
            
            <div className="notification-setting">
              <div className="setting-info">
                <h3>Conversation Update Notifications</h3>
                <p>Receive notifications when conversations are updated</p>
              </div>
              <div className="setting-toggle">
                <label className="switch">
                  <input type="checkbox" />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
            
            <div className="notification-setting">
              <div className="setting-info">
                <h3>API Usage Reminders</h3>
                <p>Receive reminders about your API usage limits</p>
              </div>
              <div className="setting-toggle">
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Privacy Tab */}
        {activeTab === 'privacy' && (
          <div className="settings-tab-content">
            <h2>Privacy Settings</h2>
            
            <div className="privacy-section">
              <h3>Data Export</h3>
              <p>Export all your data in a machine-readable format</p>
              <button className="export-data-button">
                Export My Data
              </button>
            </div>
            
            <div className="privacy-section">
              <h3>Delete Account</h3>
              <p className="warning-text">
                Permanently delete your account and all associated data. 
                This action cannot be undone.
              </p>
              <button className="delete-account-button danger">
                Delete Account
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      {message && <div className="success-message">{message}</div>}
      {error && <div className="error-message">{error}</div>}
    </div>
  )
}

export default SettingsPage