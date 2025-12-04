import React, { useState } from 'react';
import './ConversationSettings.css';

const ConversationSettings = ({ conversationId, currentVisibility = 'private', onVisibilityChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [showConfirmDialog, setShowConfirmDialog] = useState(false);
    const [pendingVisibility, setPendingVisibility] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleVisibilityToggle = (newVisibility) => {
        if (newVisibility === 'public') {
            // Show confirmation for making public
            setPendingVisibility(newVisibility);
            setShowConfirmDialog(true);
        } else {
            // Can make private without confirmation
            changeVisibility(newVisibility);
        }
    };

    const changeVisibility = async (visibility) => {
        setIsLoading(true);
        try {
            const endpoint = visibility === 'public'
                ? `/api/chat/conversations/${conversationId}/make-public`
                : `/api/chat/conversations/${conversationId}/make-private`;

            const token = localStorage.getItem('access_token');
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to update visibility');
            }

            const data = await response.json();

            // Notify parent component
            if (onVisibilityChange) {
                onVisibilityChange(visibility, data);
            }

            setShowConfirmDialog(false);
            setPendingVisibility(null);

            // Show success message
            alert(`Conversation is now ${visibility}`);

        } catch (error) {
            console.error('Error updating visibility:', error);
            alert('Failed to update conversation visibility. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleConfirm = () => {
        if (pendingVisibility) {
            changeVisibility(pendingVisibility);
        }
    };

    const handleCancel = () => {
        setShowConfirmDialog(false);
        setPendingVisibility(null);
    };

    return (
        <div className="conversation-settings">
            <button
                className="settings-toggle-btn"
                onClick={() => setIsOpen(!isOpen)}
                title="Conversation Settings"
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 1v6m0 6v6m-6-6h6m6 0h-6" />
                </svg>
            </button>

            {isOpen && (
                <div className="settings-dropdown">
                    <div className="settings-header">
                        <h3>Conversation Settings</h3>
                        <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
                    </div>

                    <div className="settings-content">
                        <div className="setting-item">
                            <div className="setting-info">
                                <h4>Visibility</h4>
                                <p className="setting-description">
                                    {currentVisibility === 'public'
                                        ? 'This conversation is shared with the community'
                                        : 'This conversation is private to you'}
                                </p>
                            </div>

                            <div className="visibility-toggle">
                                <button
                                    className={`visibility-btn ${currentVisibility === 'private' ? 'active' : ''}`}
                                    onClick={() => handleVisibilityToggle('private')}
                                    disabled={isLoading}
                                >
                                    🔒 Private
                                </button>
                                <button
                                    className={`visibility-btn ${currentVisibility === 'public' ? 'active' : ''}`}
                                    onClick={() => handleVisibilityToggle('public')}
                                    disabled={isLoading}
                                >
                                    🌍 Public
                                </button>
                            </div>
                        </div>

                        {currentVisibility === 'public' && (
                            <div className="public-info">
                                <p className="info-text">
                                    ℹ️ Your conversation and all uploaded documents are visible to the community.
                                    Others can search and learn from your shared knowledge.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Confirmation Dialog */}
            {showConfirmDialog && (
                <div className="confirm-overlay">
                    <div className="confirm-dialog">
                        <h3>⚠️ Make Conversation Public?</h3>
                        <div className="confirm-content">
                            <p>
                                This will share your conversation and all uploaded documents with the community.
                            </p>
                            <ul className="confirm-list">
                                <li>✓ Others can view your conversation</li>
                                <li>✓ Your documents become searchable</li>
                                <li>✓ Helps build community knowledge</li>
                                <li>⚠️ Cannot be undone immediately</li>
                            </ul>
                            <p className="confirm-note">
                                <strong>Note:</strong> You can make it private again later, but others may have already seen it.
                            </p>
                        </div>
                        <div className="confirm-actions">
                            <button
                                className="btn-cancel"
                                onClick={handleCancel}
                                disabled={isLoading}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn-confirm"
                                onClick={handleConfirm}
                                disabled={isLoading}
                            >
                                {isLoading ? 'Sharing...' : 'Yes, Make Public'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ConversationSettings;
