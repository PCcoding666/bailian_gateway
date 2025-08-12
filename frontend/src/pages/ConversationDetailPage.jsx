import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { conversationAPI } from '../services/api'

const ConversationDetailPage = ({ user }) => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [conversation, setConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadConversation()
  }, [id])

  const loadConversation = async () => {
    try {
      setLoading(true)
      const conversationResult = await conversationAPI.get(id)
      const messagesResult = await conversationAPI.getMessages(id)
      
      setConversation(conversationResult.data)
      setMessages(messagesResult.data.messages)
    } catch (err) {
      setError(err.message || 'Failed to load conversation')
    } finally {
      setLoading(false)
    }
  }

  const handleEditConversation = async () => {
    const newTitle = prompt('Enter new conversation title:', conversation?.title)
    if (newTitle && newTitle !== conversation?.title) {
      try {
        const result = await conversationAPI.update(id, { title: newTitle })
        setConversation(result.data)
      } catch (err) {
        alert('Failed to update conversation title')
      }
    }
  }

  const handleDeleteConversation = async () => {
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await conversationAPI.delete(id)
        navigate('/')
      } catch (err) {
        alert('Failed to delete conversation')
      }
    }
  }

  const handleContinueConversation = () => {
    navigate(`/conversations/${id}`)
  }

  if (loading) {
    return <div className="page-container">Loading...</div>
  }

  if (error) {
    return <div className="page-container error">{error}</div>
  }

  return (
    <div className="conversation-detail-page">
      {/* Breadcrumb */}
      <nav className="breadcrumb">
        <a href="/">Home</a> &gt; 
        <a href="/">Conversation List</a> &gt; 
        <span>Conversation Details</span>
      </nav>

      {/* Conversation Info */}
      <div className="conversation-info">
        <div className="info-header">
          <h1>{conversation?.title}</h1>
          <div className="actions">
            <button onClick={handleEditConversation}>Edit</button>
            <button onClick={handleDeleteConversation} className="danger">Delete</button>
          </div>
        </div>
        
        <div className="info-details">
          <div className="info-item">
            <strong>Model:</strong> {conversation?.model_name}
          </div>
          <div className="info-item">
            <strong>Created:</strong> {new Date(conversation?.created_at).toLocaleString()}
          </div>
          <div className="info-item">
            <strong>Last Updated:</strong> {new Date(conversation?.updated_at).toLocaleString()}
          </div>
          <div className="info-item">
            <strong>Status:</strong> 
            <span className={`status ${conversation?.status === 1 ? 'active' : 'ended'}`}>
              {conversation?.status === 1 ? 'In Progress' : 'Ended'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="messages-section">
        <h2>Message History</h2>
        <div className="messages-list">
          {messages.map(message => (
            <div key={message.id} className={`message-item ${message.role}`}>
              <div className="message-header">
                <span className="message-role">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </span>
                <span className="message-time">
                  {new Date(message.created_at).toLocaleString()}
                </span>
              </div>
              <div className="message-content">
                {message.content.map((content, index) => (
                  <div key={index} className="content-item">
                    {content.type === 'text' && <p>{content.text}</p>}
                    {content.type === 'image_url' && (
                      <img src={content.image_url.url} alt="Image content" />
                    )}
                    {content.type === 'video_url' && (
                      <video src={content.video_url.url} controls />
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="page-actions">
        <button onClick={handleContinueConversation}>Continue Conversation</button>
        <button onClick={() => navigate('/')}>Return to List</button>
      </div>
    </div>
  )
}

export default ConversationDetailPage