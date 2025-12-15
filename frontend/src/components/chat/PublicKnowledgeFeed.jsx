import React, { useState, useEffect } from 'react';
import './PublicKnowledgeFeed.css';

const PublicKnowledgeFeed = () => {
    const [conversations, setConversations] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [sortBy, setSortBy] = useState('recent'); // recent, popular, upvoted
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchPublicConversations();
    }, [sortBy]);

    const fetchPublicConversations = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || ''}/api/chat/conversations/public?sort_by=${sortBy}&limit=20`,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Failed to fetch public conversations');
            }

            const data = await response.json();
            setConversations(data.conversations || []);
        } catch (err) {
            console.error('Error fetching public conversations:', err);
            setError('Failed to load public conversations. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleUpvote = async (conversationId) => {
        try {
            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/chat/conversations/${conversationId}/upvote`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Failed to upvote');
            }

            const data = await response.json();

            // Update local state
            setConversations(prev => prev.map(conv =>
                conv.id === conversationId
                    ? { ...conv, upvote_count: data.upvote_count }
                    : conv
            ));
        } catch (err) {
            console.error('Error upvoting:', err);
            alert('Failed to upvote. Please try again.');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="public-knowledge-feed">
            <div className="feed-header">
                <div className="header-content">
                    <h2>🌍 Community Knowledge</h2>
                    <p className="header-subtitle">
                        Explore conversations and documents shared by the community
                    </p>
                </div>

                <div className="sort-controls">
                    <button
                        className={`sort-btn ${sortBy === 'recent' ? 'active' : ''}`}
                        onClick={() => setSortBy('recent')}
                    >
                        🕐 Recent
                    </button>
                    <button
                        className={`sort-btn ${sortBy === 'popular' ? 'active' : ''}`}
                        onClick={() => setSortBy('popular')}
                    >
                        🔥 Popular
                    </button>
                    <button
                        className={`sort-btn ${sortBy === 'upvoted' ? 'active' : ''}`}
                        onClick={() => setSortBy('upvoted')}
                    >
                        ⭐ Top Rated
                    </button>
                </div>
            </div>

            {isLoading && (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading community knowledge...</p>
                </div>
            )}

            {error && (
                <div className="error-state">
                    <p>❌ {error}</p>
                    <button onClick={fetchPublicConversations} className="retry-btn">
                        Try Again
                    </button>
                </div>
            )}

            {!isLoading && !error && conversations.length === 0 && (
                <div className="empty-state">
                    <div className="empty-icon">📚</div>
                    <h3>No Public Conversations Yet</h3>
                    <p>Be the first to share your knowledge with the community!</p>
                </div>
            )}

            {!isLoading && !error && conversations.length > 0 && (
                <div className="conversations-grid">
                    {conversations.map((conv) => (
                        <div key={conv.id} className="conversation-card">
                            <div className="card-header">
                                <div className="topic-badge">{conv.topic || 'General'}</div>
                                <div className="card-meta">
                                    <span className="author">👤 {conv.author}</span>
                                    <span className="date">{formatDate(conv.shared_at)}</span>
                                </div>
                            </div>

                            <h3 className="card-title">{conv.title || 'Untitled Conversation'}</h3>

                            <div className="card-stats">
                                <div className="stat-item">
                                    <span className="stat-icon">👁️</span>
                                    <span className="stat-value">{conv.view_count}</span>
                                    <span className="stat-label">views</span>
                                </div>
                                <div className="stat-item">
                                    <span className="stat-icon">📄</span>
                                    <span className="stat-value">{conv.document_count}</span>
                                    <span className="stat-label">docs</span>
                                </div>
                                <div className="stat-item upvote-stat">
                                    <button
                                        className="upvote-btn"
                                        onClick={() => handleUpvote(conv.id)}
                                        title="Upvote this conversation"
                                    >
                                        <span className="stat-icon">⬆️</span>
                                        <span className="stat-value">{conv.upvote_count}</span>
                                    </button>
                                </div>
                            </div>

                            <div className="card-actions">
                                <button
                                    className="view-btn"
                                    onClick={() => window.location.href = `/dashboard/chat?id=${conv.id}`}
                                >
                                    View Conversation →
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default PublicKnowledgeFeed;
