import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, MessageSquare, Clock, Zap } from 'lucide-react';

const ConversationAnalytics = ({ conversations }) => {
  if (!conversations || conversations.length === 0) {
    return null;
  }

  // Calculate analytics
  const totalMessages = conversations.reduce((sum, conv) => sum + (conv.total_messages || 0), 0);
  const avgSentiment = conversations.reduce((sum, conv) => sum + (conv.sentiment || 0), 0) / conversations.length;
  const topicDistribution = conversations.reduce((acc, conv) => {
    const topic = conv.topic || 'general';
    acc[topic] = (acc[topic] || 0) + 1;
    return acc;
  }, {});

  const topicData = Object.entries(topicDistribution).map(([name, value]) => ({ name, value }));
  
  const COLORS = ['#8FABD4', '#435663', '#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF'];

  const stats = [
    {
      label: 'Total Conversations',
      value: conversations.length,
      icon: MessageSquare,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      label: 'Total Messages',
      value: totalMessages,
      icon: Zap,
      color: 'text-green-500',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      label: 'Avg Sentiment',
      value: `${(avgSentiment * 100).toFixed(0)}%`,
      icon: TrendingUp,
      color: 'text-purple-500',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg"
    >
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Conversation Analytics
      </h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`${stat.bgColor} rounded-lg p-4 flex items-center gap-4`}
          >
            <div className={`${stat.color} p-3 rounded-full bg-white dark:bg-gray-800`}>
              <stat.icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Topic Distribution */}
      {topicData.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Topics Discussed
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={topicData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {topicData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  );
};

export default ConversationAnalytics;
