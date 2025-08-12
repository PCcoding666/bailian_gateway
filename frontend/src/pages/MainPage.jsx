import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { conversationAPI } from '../services/api'

const MainPage = ({ user, onLogout }) => {
  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  // Load conversations on component mount
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const result = await conversationAPI.list()
      setConversations(result.data.conversations)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }

  const createConversation = async () => {
    try {
      const result = await conversationAPI.create({
        model_name: 'qwen-vl-max-latest',
        title: 'New Conversation'
      })
      setConversations([result.data, ...conversations])
      setCurrentConversation(result.data)
      setMessages([])
    } catch (err) {
      console.error('Failed to create conversation:', err)
    }
  }

  const selectConversation = async (conversation) => {
    setCurrentConversation(conversation)
    try {
      const result = await conversationAPI.getMessages(conversation.id)
      setMessages(result.data.messages)
    } catch (err) {
      console.error('Failed to load messages:', err)
      setMessages([])
    }
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !currentConversation) return

    const messageContent = [{
      type: 'text',
      text: newMessage
    }]

    // Add user message to UI immediately
    const userMessage = {
      id: Date.now(),
      conversation_id: currentConversation.id,
      user_id: user.id,
      role: 'user',
      content_type: 'text',
      content: messageContent,
      status: 1,
      created_at: new Date().toISOString()
    }
    
    setMessages([...messages, userMessage])
    setNewMessage('')

    try {
      // Send message to backend
      const result = await conversationAPI.sendMessage(currentConversation.id, messageContent)
      
      // Add assistant response
      // In a real implementation, you would get the actual response from the API
      // For now, we'll simulate it
      setTimeout(() => {
        const assistantMessage = {
          id: Date.now() + 1,
          conversation_id: currentConversation.id,
          user_id: 0,
          role: 'assistant',
          content_type: 'text',
          content: [{ type: 'text', text: 'This is a simulated response from the AI assistant.' }],
          status: 1,
          created_at: new Date().toISOString()
        }
        setMessages(prev => [...prev, assistantMessage])
      }, 1000)
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  return (
    <div className="main-page">
      {/* Header */}
      <header className="main-header">
        <div className="header-left">
          <h1>Bailian AI Platform</h1>
        </div>
        <div className="header-right">
          <button onClick={createConversation}>New Conversation</button>
          <div className="user-menu">
            <span>Welcome, {user?.nickname || user?.username}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </header>

      <div className="main-content">
        {/* Conversations Sidebar */}
        <aside className="conversations-sidebar">
          <div className="sidebar-header">
            <h2>Conversations</h2>
          </div>
          <div className="conversations-list">
            {conversations.map(conversation => (
              <div 
                key={conversation.id} 
                className={`conversation-item ${currentConversation?.id === conversation.id ? 'active' : ''}`}
                onClick={() => selectConversation(conversation)}
              >
                <div className="conversation-title">{conversation.title}</div>
                <div className="conversation-model">{conversation.model_name}</div>
                <div className="conversation-time">
                  {new Date(conversation.updated_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Chat Area */}
        <main className="chat-area">
          {currentConversation ? (
            <>
              <div className="chat-header">
                <h2>{currentConversation.title}</h2>
                <div className="chat-model">Model: {currentConversation.model_name}</div>
              </div>
              
              <div className="messages-container">
                {messages.map(message => (
                  <div 
                    key={message.id} 
                    className={`message ${message.role}`}
                  >
                    <div className="message-content">
                      {message.content.map((content, index) => (
                        <div key={index}>
                          {content.type === 'text' && <p>{content.text}</p>}
                          {content.type === 'image_url' && (
                            <img src={content.image_url.url} alt="Uploaded content" />
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="message-time">
                      {new Date(message.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="message-input-area">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type your message here..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage()
                    }
                  }}
                />
                <button onClick={handleSendMessage} disabled={!newMessage.trim()}>
                  Send
                </button>
              </div>
            </>
          ) : (
            <div className="no-conversation-selected">
              <h3>Select a conversation or create a new one</h3>
              <button onClick={createConversation}>New Conversation</button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default MainPage