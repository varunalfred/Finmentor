import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import ConversationSidebar from './ConversationSidebar';
import SatisfactionRatingModal from './SatisfactionRatingModal';
import MessageMetadata from './MessageMetadata';
import { MessageSkeleton } from '../common/Skeletons';
import './ChatInterface.css';

const ChatInterface = ({ 
  title = "FinAdvisor AI",
  placeholder = "Ask me anything about finance...",
  quickActions = [],
  endpoint = "/api/chat/",
  onSendMessage,
  registerCallbacks = null
}) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null); // Track conversation thread
  const [sidebarOpen, setSidebarOpen] = useState(false); // Sidebar toggle
  const [showRatingModal, setShowRatingModal] = useState(false); // Satisfaction rating modal
  const [isRecording, setIsRecording] = useState(false); // Voice recording state
  const [isUploading, setIsUploading] = useState(false); // File upload state
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Register callbacks with parent component
  useEffect(() => {
    if (registerCallbacks) {
      const toggleSidebar = () => setSidebarOpen(prev => !prev);
      registerCallbacks(
        toggleSidebar,
        handleNewConversation,
        messages.length > 0
      );
    }
  }, [messages.length]);

  const handleSendMessage = async (messageText) => {
    const text = messageText || inputText.trim();
    
    if (!text) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    setError(null);

    try {
      // Call the backend API using the centralized api service
      // Pass conversationId to continue the same conversation thread
      const result = await api.sendChatMessage(text, conversationId);

      if (!result.success) {
        throw new Error(result.error);
      }

      const data = result.data;

      // Store conversation_id from response to continue thread
      if (data.metadata?.conversation_id) {
        setConversationId(data.metadata.conversation_id);
      }

      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response || 'Sorry, I could not process your request.',
        timestamp: new Date().toISOString(),
        metadata: data.metadata || {}
      };

      setMessages(prev => [...prev, aiMessage]);

      // Check if we should prompt for satisfaction rating (every 50 conversations)
      if (data.metadata?.prompt_satisfaction_rating && conversationId) {
        // Show rating modal after a short delay (2 seconds)
        setTimeout(() => {
          setShowRatingModal(true);
          toast('🎉 You\'ve reached a milestone! Please rate your experience.', {
            duration: 4000,
          });
        }, 2000);
      }

      if (onSendMessage) {
        onSendMessage(text, data);
      }
    } catch (err) {
      console.error('Chat error:', err);
      toast.error('Failed to get response. Please try again.');
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action) => {
    setInputText(action);
    handleSendMessage(action);
  };

  const handleNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    setError(null);
  };

  const handleSelectConversation = async (conversation) => {
    try {
      // Load conversation messages
      const result = await api.getConversationMessages(conversation.id);
      
      if (result.success && result.data) {
        // Convert messages to UI format
        const loadedMessages = result.data.messages.map((msg, index) => ({
          id: msg.id || `loaded-${index}`,
          role: msg.role,
          content: msg.content,
          timestamp: msg.created_at,
          metadata: {
            confidence_score: msg.confidence_score,
            model_used: msg.model_used
          }
        }));
        
        setMessages(loadedMessages);
        setConversationId(conversation.id);
        setError(null);
      } else {
        setError('Failed to load conversation');
      }
    } catch (err) {
      console.error('Error loading conversation:', err);
      setError('Failed to load conversation');
    }
  };

  const handleSubmitRating = async (convId, rating) => {
    try {
      const result = await api.submitSatisfactionRating(convId, rating);
      if (result.success) {
        toast.success('Thank you for your feedback!');
      } else {
        toast.error('Failed to submit rating');
      }
    } catch (err) {
      console.error('Error submitting rating:', err);
      toast.error('Failed to submit rating');
    }
  };

  const handleVoiceInput = async () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      toast.success('Voice recording stopped');
      // TODO: Process audio and send to backend
      toast.error('Voice processing not yet implemented');
    } else {
      // Start recording
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast.error('Voice input not supported in your browser');
        return;
      }
      
      try {
        setIsRecording(true);
        toast.success('Recording... Click again to stop');
        // TODO: Implement actual audio recording
      } catch (err) {
        toast.error('Failed to access microphone');
        setIsRecording(false);
      }
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      toast.error('File too large. Maximum size is 10MB');
      return;
    }

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Only PDF and image files are supported');
      return;
    }

    setIsUploading(true);
    toast.loading('Processing file...');

    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Data = e.target?.result?.toString().split(',')[1];
        const inputType = file.type.startsWith('image/') ? 'image' : 'document';
        
        // TODO: Send to backend with file data
        toast.dismiss();
        toast.error('File upload processing not yet implemented');
        setIsUploading(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      toast.dismiss();
      toast.error('Failed to process file');
      setIsUploading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      <SatisfactionRatingModal
        isOpen={showRatingModal}
        onClose={() => setShowRatingModal(false)}
        onSubmit={handleSubmitRating}
        conversationId={conversationId}
      />
      
      <div className={`chat-interface ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <ConversationSidebar
          currentConversationId={conversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

      {/* Quick Actions */}
      {quickActions.length > 0 && messages.length === 0 && (
        <div className="quick-actions">
          <p className="quick-actions-label">Quick Actions:</p>
          <div className="quick-actions-buttons">
            {quickActions.map((action, index) => (
              <button
                key={index}
                className="quick-action-btn"
                onClick={() => handleQuickAction(action)}
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 && !isTyping && (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <p>Start a conversation!</p>
            <p className="empty-subtitle">Ask me anything about your finances</p>
          </div>
        )}

        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className={`message ${message.role} ${message.isError ? 'error' : ''}`}
            >
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-time">{formatTime(message.timestamp)}</div>
                {message.role === 'assistant' && message.metadata && (
                  <MessageMetadata metadata={message.metadata} />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isTyping && (
          <div className="message assistant typing">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}

      {/* Input Box */}
      <div className="input-container">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf,.jpg,.jpeg,.png"
          style={{ display: 'none' }}
        />
        
        <button
          className="input-action-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={isTyping || isUploading}
          title="Attach file (PDF, Image)"
        >
          📎
        </button>
        
        <button
          className={`input-action-btn ${isRecording ? 'recording' : ''}`}
          onClick={handleVoiceInput}
          disabled={isTyping || isUploading}
          title={isRecording ? "Stop recording" : "Voice input"}
        >
          {isRecording ? '⏹️' : '🎤'}
        </button>
        
        <textarea
          className="message-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          rows={1}
          disabled={isTyping || isRecording || isUploading}
        />
        
        <button
          className="send-button"
          onClick={() => handleSendMessage()}
          disabled={!inputText.trim() || isTyping || isRecording || isUploading}
        >
          <span className="send-icon">➤</span>
        </button>
      </div>
    </div>
    </>
  );
};

export default ChatInterface;
