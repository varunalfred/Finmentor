import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Zap, Brain, TrendingUp } from 'lucide-react';

const MessageMetadata = ({ metadata }) => {
  if (!metadata) return null;

  const {
    sentiment_score,
    processing_time,
    confidence,
    tokens_used
  } = metadata;

  // Sentiment emoji based on score
  const getSentimentEmoji = (score) => {
    if (!score) return null;
    if (score >= 0.7) return '😊';
    if (score >= 0.4) return '😐';
    return '😞';
  };

  // Confidence badge color
  const getConfidenceBadge = (conf) => {
    if (!conf) return null;
    if (conf >= 0.8) return { text: 'High', color: 'bg-green-500' };
    if (conf >= 0.5) return { text: 'Medium', color: 'bg-yellow-500' };
    return { text: 'Low', color: 'bg-red-500' };
  };

  const confidenceBadge = getConfidenceBadge(confidence);

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="mt-2 flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400"
    >
      {/* Sentiment Score */}
      {sentiment_score !== undefined && (
        <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
          <TrendingUp className="w-3 h-3" />
          <span>{getSentimentEmoji(sentiment_score)}</span>
          <span>{(sentiment_score * 100).toFixed(0)}%</span>
        </div>
      )}

      {/* Confidence */}
      {confidenceBadge && (
        <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
          <Brain className="w-3 h-3" />
          <span className={`w-2 h-2 rounded-full ${confidenceBadge.color}`} />
          <span>{confidenceBadge.text}</span>
        </div>
      )}

      {/* Processing Time */}
      {processing_time !== undefined && (
        <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
          <Clock className="w-3 h-3" />
          <span>{processing_time.toFixed(2)}s</span>
        </div>
      )}

      {/* Tokens Used */}
      {tokens_used !== undefined && (
        <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
          <Zap className="w-3 h-3" />
          <span>{tokens_used} tokens</span>
        </div>
      )}
    </motion.div>
  );
};

export default MessageMetadata;
