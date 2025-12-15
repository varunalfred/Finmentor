import React, { useState, useEffect } from 'react';
import './DocumentManager.css';

const DocumentManager = ({ conversationId, refreshTrigger }) => {
    const [documents, setDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showManager, setShowManager] = useState(false);

    useEffect(() => {
        if (conversationId) {
            fetchDocuments();
        }
    }, [conversationId, refreshTrigger]);

    const fetchDocuments = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || ''}/api/chat/documents/mine?conversation_id=${conversationId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) throw new Error('Failed to fetch documents');

            const data = await response.json();
            setDocuments(data.documents || []);
        } catch (error) {
            console.error('Error fetching documents:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (documentId) => {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            const token = localStorage.getItem('access_token');
            const userId = localStorage.getItem('user_id'); // You may need to store this

            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/chat/documents/${documentId}?user_id=${userId}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) throw new Error('Failed to delete document');

            // Remove from local state
            setDocuments(prev => prev.filter(doc => doc.id !== documentId));
            alert('Document deleted successfully');
        } catch (error) {
            console.error('Error deleting document:', error);
            alert('Failed to delete document');
        }
    };

    const formatFileSize = (bytes) => {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    return (
        <div className="document-manager">
            <button
                className="toggle-manager-btn"
                onClick={() => setShowManager(!showManager)}
                title="Manage Documents"
            >
                📄 Documents ({documents.length})
            </button>

            {showManager && (
                <div className="manager-panel">
                    <div className="panel-header">
                        <h3>📚 Your Documents</h3>
                        <button className="close-panel-btn" onClick={() => setShowManager(false)}>
                            ×
                        </button>
                    </div>

                    {isLoading && (
                        <div className="loading">Loading documents...</div>
                    )}

                    {!isLoading && documents.length === 0 && (
                        <div className="empty-docs">
                            <p>No documents uploaded yet</p>
                            <small>Upload PDFs in your conversations to see them here</small>
                        </div>
                    )}

                    {!isLoading && documents.length > 0 && (
                        <div className="documents-list">
                            {documents.map((doc) => (
                                <div key={doc.id} className="document-item">
                                    <div className="doc-icon">📄</div>
                                    <div className="doc-info">
                                        <div className="doc-name">{doc.filename}</div>
                                        <div className="doc-meta">
                                            <span>{formatFileSize(doc.file_size)}</span>
                                            <span>•</span>
                                            <span>{doc.total_pages} pages</span>
                                            <span>•</span>
                                            <span>{doc.is_public ? '🌍 Public' : '🔒 Private'}</span>
                                        </div>
                                    </div>
                                    <button
                                        className="delete-doc-btn"
                                        onClick={() => handleDelete(doc.id)}
                                        title="Delete document"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default DocumentManager;
