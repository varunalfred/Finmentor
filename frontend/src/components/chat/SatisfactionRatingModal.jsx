import React, { useState } from 'react';
import './SatisfactionRatingModal.css';

const SatisfactionRatingModal = ({ isOpen, onClose, onSubmit, conversationId }) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (rating === 0) return;
    
    setIsSubmitting(true);
    await onSubmit(conversationId, rating);
    setIsSubmitting(false);
    setRating(0);
    setHoveredRating(0);
    onClose();
  };

  const handleClose = () => {
    setRating(0);
    setHoveredRating(0);
    onClose();
  };

  return (
    <div className="rating-modal-overlay" onClick={handleClose}>
      <div className="rating-modal" onClick={(e) => e.stopPropagation()}>
        <div className="rating-modal-header">
          <h3>How was your experience?</h3>
          <button className="rating-modal-close" onClick={handleClose}>×</button>
        </div>
        
        <div className="rating-modal-body">
          <p>Your feedback helps us improve FinAdvisor AI</p>
          
          <div className="star-rating">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                className={`star ${star <= (hoveredRating || rating) ? 'active' : ''}`}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
                disabled={isSubmitting}
              >
                ★
              </button>
            ))}
          </div>
          
          <div className="rating-labels">
            <span>Poor</span>
            <span>Excellent</span>
          </div>
        </div>
        
        <div className="rating-modal-footer">
          <button 
            className="rating-btn rating-btn-secondary" 
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Skip
          </button>
          <button 
            className="rating-btn rating-btn-primary" 
            onClick={handleSubmit}
            disabled={rating === 0 || isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SatisfactionRatingModal;
