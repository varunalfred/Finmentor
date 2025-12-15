import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import ConversationSidebar from './ConversationSidebar';
import SatisfactionRatingModal from './SatisfactionRatingModal';
import MessageMetadata from './MessageMetadata';
import ConversationSettings from './ConversationSettings';
import DocumentManager from './DocumentManager';
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
  const [docRefreshTrigger, setDocRefreshTrigger] = useState(0);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null); // Track conversation thread
  const [sidebarOpen, setSidebarOpen] = useState(false); // Sidebar toggle
  const [showRatingModal, setShowRatingModal] = useState(false); // Satisfaction rating modal
  const [isRecording, setIsRecording] = useState(false); // Voice recording state
  const [isUploading, setIsUploading] = useState(false); // File upload state
  const [pendingAttachment, setPendingAttachment] = useState(null); // File waiting to be sent
  const [conversationVisibility, setConversationVisibility] = useState('private'); // Track if conversation is public/private
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const sidebarRefreshRef = useRef(null); // Ref to trigger sidebar refresh

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Auth Redirect Check
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        window.location.href = '/login';
      }
    };
    checkAuth();

    // Check for conversation ID in URL (from Community or elsewhere)
    const urlParams = new URLSearchParams(window.location.search);
    const urlConvId = urlParams.get('id');
    if (urlConvId) {
      handleSelectConversation({ id: urlConvId });
      // Use history.pushState to clean URL without reloading, if desired, 
      // or leave it to allow bookmarking.
    }

    // Optional: interval check
    const interval = setInterval(checkAuth, 5000);
    return () => clearInterval(interval);
  }, []);

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

  const handleSendMessage = async (content = inputText, type = 'text', filename = null) => {
    if (!content.trim() && type === 'text' && !pendingAttachment) return;

    // If we have a pending attachment, use that instead
    let messageContent = content;
    let messageType = type;
    let attachmentData = null;

    if (pendingAttachment) {
      messageType = pendingAttachment.type;
      attachmentData = pendingAttachment.data;
      // If user didn't type anything, use a default prompt
      if (!messageContent.trim()) {
        messageContent = `Analyze this document: ${pendingAttachment.name}`;
      }
    }

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
      // Add attachment info to UI if present
      attachment: pendingAttachment ? { name: pendingAttachment.name, type: pendingAttachment.type } : null
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setPendingAttachment(null); // Clear pending attachment
    setIsTyping(true);
    setError(null);

    try {
      // Call the backend API using the centralized api service
      // Pass conversationId to continue the same conversation thread

      // Prepare API call arguments
      const apiArgs = [messageContent, conversationId];

      // If we have attachment data (from pending attachment), add it to the API call
      // We need to modify how we call the API to support this hybrid mode
      // For now, we'll use the existing structure but pass the document data if present
      // Prepare payload for streaming
      const payload = {
        message: messageContent,
        conversation_id: conversationId,
        input_type: attachmentData ? 'text' : 'text', // Input is text ABOUT the doc.
        // If we have an attachment, pass its ID in context so backend knows what to look at
        context: pendingAttachment?.documentId ? { document_id: pendingAttachment.documentId } : null,
        user_profile: null // Let API handle defaults
      };

      // Standard text message setup (used for ALL types now)
      const aiMessageId = Date.now() + 1;
      const initialAiMessage = {
        id: aiMessageId,
        role: 'assistant',
        content: '',
        thoughts: [], // Array to store thinking steps
        timestamp: new Date().toISOString(),
        isStreaming: true
      };
      setMessages(prev => [...prev, initialAiMessage]);
      setIsTyping(false); // Hide generic typing indicator since we have a specific message placeholder now

      // Streaming callback
      let fullContent = '';
      let currentThoughts = [];

      await api.streamChatMessage(
        payload,
        (chunk) => {
          // As soon as we get ANY data, stop the generic "Typing" bubble
          setIsTyping(false);

          if (chunk.type === 'thought') {
            if (!currentThoughts.includes(chunk.content)) {
              currentThoughts.push(chunk.content);
              setMessages(prev => prev.map(msg =>
                msg.id === aiMessageId ? { ...msg, thoughts: [...currentThoughts] } : msg
              ));
            }
          } else if (chunk.type === 'token') {
            fullContent += chunk.content;
            setMessages(prev => prev.map(msg =>
              msg.id === aiMessageId ? { ...msg, content: fullContent } : msg
            ));
          } else if (chunk.type === 'error') {
            setMessages(prev => prev.map(msg =>
              msg.id === aiMessageId ? { ...msg, content: `Error: ${chunk.content}`, isStreaming: false } : msg
            ));
          } else if (chunk.type === 'metadata') {
            if (chunk.content && chunk.content.conversation_id) {
              setConversationId(chunk.content.conversation_id);
              // Refresh sidebar since we have a new conversation
              if (sidebarRefreshRef.current) {
                sidebarRefreshRef.current();
              }
            }
          }
        }
      );

      // Finalize message
      setMessages(prev => prev.map(msg => {
        if (msg.id === aiMessageId) {
          return { ...msg, isStreaming: false };
        }
        return msg;
      }));

      setIsTyping(false);

      // Refresh sidebar if new conversation
      if (!conversationId && sidebarRefreshRef.current) {
        sidebarRefreshRef.current();
      }

    } catch (err) {
      console.error('Chat error:', err);
      toast.error('Failed to get response. Please try again.');
      setError('Failed to get response. Please try again.');
      // Remove the placeholder if it failed completely (optional, but cleaner)
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputText);
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

        // Update visibility state if available in conversation object
        if (conversation.is_public !== undefined) {
          setConversationVisibility(conversation.is_public ? 'public' : 'private');
        } else if (result.data.conversation) {
          // Fallback to checking the response data if it contains conversation metadata
          setConversationVisibility(result.data.conversation.is_public ? 'public' : 'private');
        }

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
    // Check if browser supports Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      toast.error('Voice input not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      toast.info('Voice input stopped');
    } else {
      // Start speech recognition
      setIsRecording(true);

      const recognition = new SpeechRecognition();
      recognition.continuous = false; // Stop after one phrase
      recognition.lang = 'en-IN'; // Indian English (change as needed)
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        toast.success('🎤 Listening... Speak now!', { duration: 2000 });
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const confidence = event.results[0][0].confidence;

        setIsRecording(false);
        setInputText(transcript);

        toast.success(`Heard: "${transcript}"`, {
          duration: 3000,
          icon: '✅'
        });

        // Optionally auto-send after successful transcription
        // Uncomment to enable auto-send:
        // setTimeout(() => handleSendMessage(transcript), 500);
      };

      recognition.onerror = (event) => {
        setIsRecording(false);

        let errorMessage = 'Speech recognition failed';
        if (event.error === 'no-speech') {
          errorMessage = 'No speech detected. Please try again.';
        } else if (event.error === 'audio-capture') {
          errorMessage = 'Microphone not accessible';
        } else if (event.error === 'not-allowed') {
          errorMessage = 'Microphone permission denied';
        }

        toast.error(errorMessage);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      try {
        recognition.start();
      } catch (err) {
        setIsRecording(false);
        toast.error('Failed to start voice recognition');
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
    const loadingToast = toast.loading(`Processing ${file.name}...`);

    try {
      const reader = new FileReader();

      reader.onload = async (e) => {
        const base64Data = e.target?.result?.toString().split(',')[1];
        const inputType = file.type.startsWith('image/') ? 'image' : 'document';

        try {
          // 1. Upload to backend immediately (Background Processing)
          const uploadResult = await api.uploadDocument(base64Data, file.name, conversationId);

          if (!uploadResult.success) {
            throw new Error(uploadResult.error || 'Upload failed');
          }

          // 2. Set as pending attachment with the returned ID
          setPendingAttachment({
            name: file.name,
            type: inputType,
            data: base64Data, // Keep for preview if needed
            documentId: uploadResult.data.document_id // Store the ID!
          });

          toast.dismiss(loadingToast);
          toast.success('File processed & ready! Type your message.');

          // Trigger document list update
          setDocRefreshTrigger(prev => prev + 1);

        } catch (err) {
          toast.dismiss(loadingToast);
          toast.error('Failed to process file');
          console.error('File processing error:', err);
        } finally {
          setIsUploading(false);
          // Clear file input
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
        }
      };

      reader.onerror = () => {
        toast.dismiss(loadingToast);
        toast.error('Failed to read file');
        setIsUploading(false);
      };

      reader.readAsDataURL(file);

    } catch (err) {
      toast.dismiss(loadingToast);
      toast.error('Failed to upload file');
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
          onRefreshReady={(refetchFn) => {
            sidebarRefreshRef.current = refetchFn;
          }}
        />

        {/* Conversation Tools - Settings and Document Manager */}
        {conversationId && (
          <div className="conversation-tools">
            <ConversationSettings
              conversationId={conversationId}
              currentVisibility={conversationVisibility}
              onVisibilityChange={(newVisibility) => {
                setConversationVisibility(newVisibility);
                toast.success(`Conversation is now ${newVisibility}`);
              }}
            />
            <DocumentManager
              conversationId={conversationId}
              refreshTrigger={docRefreshTrigger}
            />
          </div>
        )}

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
                  {/* Thoughts / Reasoning Steps */}
                  {message.thoughts && message.thoughts.length > 0 && (
                    <div className="message-thoughts">
                      <details>
                        <summary>
                          {message.isStreaming ? 'Thinking...' : 'View Thought Process'}
                        </summary>
                        <div className="thought-timeline">
                          {message.thoughts.map((thought, idx) => {
                            let icon = '🤔';
                            let typeClass = 'thinking';

                            if (thought.toLowerCase().includes('tool') || thought.toLowerCase().includes('using')) {
                              icon = '🛠️';
                              typeClass = 'tool';
                            } else if (thought.toLowerCase().includes('search') || thought.toLowerCase().includes('retriev') || thought.toLowerCase().includes('context')) {
                              icon = '🔍';
                              typeClass = 'search';
                            } else if (thought.toLowerCase().includes('analyz')) {
                              icon = '⚡';
                              typeClass = 'analysis';
                            }

                            return (
                              <div key={idx} className={`thought-step ${typeClass}`}>
                                <span className="thought-icon">{icon}</span>
                                <span className="thought-text">{thought}</span>
                              </div>
                            );
                          })}
                        </div>
                      </details>
                    </div>
                  )}

                  {/* Main Content */}
                  <div className="message-text">
                    {message.content}
                    {/* Only show blinking cursor if we are streaming and have content, OR if we have no thoughts yet */}
                    {message.isStreaming && (!message.thoughts || message.thoughts.length === 0 || message.content) && (
                      <span className="cursor">|</span>
                    )}
                  </div>

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
            className="send-btn"
            onClick={() => handleSendMessage()}
            disabled={(!inputText.trim() && !pendingAttachment) || isTyping || isUploading}
            title={isUploading ? "Processing file..." : "Send message"}
          >
            {isUploading ? (
              <span className="loading-dots">...</span>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </>
  );
};

export default ChatInterface;
