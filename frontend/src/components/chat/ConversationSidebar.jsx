import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useConversations, useDeleteConversation } from '../../hooks/useApi';
import { ConversationSkeleton } from '../common/Skeletons';
import ConversationAnalytics from './ConversationAnalytics';
import './ConversationSidebar.css';

const ConversationSidebar = ({ 
  currentConversationId, 
  onSelectConversation, 
  onNewConversation,
  isOpen,
  onClose 
}) => {
  const [showAnalytics, setShowAnalytics] = useState(false);
  const { data, isLoading, error, refetch } = useConversations(50, 0);
  const deleteConversationMutation = useDeleteConversation();

  const conversations = data?.data?.conversations || [];

  const handleSelectConversation = (conversation) => {
    onSelectConversation(conversation);
    if (window.innerWidth < 768) {
      onClose(); // Close sidebar on mobile after selection
    }
  };

  const handleDeleteConversation = async (e, conversationId) => {
    e.stopPropagation(); // Prevent triggering conversation select
    
    if (!window.confirm('Delete this conversation?')) {
      return;
    }

    deleteConversationMutation.mutate(conversationId, {
      onSuccess: () => {
        // If deleted conversation was active, start new
        if (conversationId === currentConversationId) {
          onNewConversation();
        }
        refetch(); // Refresh the list
      }
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className={`conversation-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h3>Conversations</h3>
        <button 
          className="close-sidebar-btn"
          onClick={onClose}
          aria-label="Close sidebar"
        >
          ×
        </button>
      </div>

      <div className="sidebar-actions">
        <button 
          className="new-conversation-btn-sidebar" 
          onClick={() => {
            onNewConversation();
            if (window.innerWidth < 768) onClose();
          }}
        >
          + New Conversation
        </button>
        
        {conversations.length > 0 && (
          <button
            className="analytics-toggle-btn"
            onClick={() => setShowAnalytics(!showAnalytics)}
          >
            {showAnalytics ? '📊 Hide Stats' : '📊 Show Stats'}
          </button>
        )}
      </div>

      {showAnalytics && conversations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <ConversationAnalytics conversations={conversations} />
        </motion.div>
      )}

      <div className="conversations-list">
        {isLoading && <ConversationSkeleton />}

        {error && (
          <div className="sidebar-error">
            <p>Failed to load conversations</p>
            <button onClick={() => refetch()}>Retry</button>
          </div>
        )}

        {!isLoading && !error && conversations.length === 0 && (
          <div className="sidebar-empty">
            <p>No conversations yet</p>
            <p className="sidebar-empty-subtitle">Start chatting to create your first conversation</p>
          </div>
        )}

        {!isLoading && !error && conversations.map((conversation) => (
          <div
            key={conversation.id}
            className={`conversation-item ${conversation.id === currentConversationId ? 'active' : ''}`}
            onClick={() => handleSelectConversation(conversation)}
          >
            <div className="conversation-content">
              <h4 className="conversation-title">{conversation.title || 'Untitled'}</h4>
              <div className="conversation-meta">
                <span className="conversation-date">
                  {formatDate(conversation.updated_at || conversation.created_at)}
                </span>
                {conversation.total_messages > 0 && (
                  <span className="conversation-messages">
                    {conversation.total_messages} messages
                  </span>
                )}
              </div>
            </div>
            <button
              className="delete-conversation-btn"
              onClick={(e) => handleDeleteConversation(e, conversation.id)}
              aria-label="Delete conversation"
              title="Delete conversation"
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationSidebar;
