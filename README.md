# FinMentor AI - Your Personal Financial Mentor

A revolutionary Flutter-based financial advisory platform powered by multi-agent AI architecture. FinMentor AI combines voice interaction, visual learning, and adaptive intelligence to make financial literacy accessible to everyone.

## 🚀 What Makes FinMentor AI Unique

Unlike traditional financial apps that either track expenses OR provide generic advice, FinMentor AI is the first platform to combine:

- **🤖 Multi-Agent Intelligence**: Specialized AI agents collaborate to provide comprehensive financial guidance
- **🎤 Voice-First Hybrid Interface**: Seamlessly switch between voice and text interaction
- **🎓 Progressive Learning System**: Gamified financial education that grows with your knowledge
- **🧠 Behavioral Coaching**: Detects and helps overcome emotional investing biases
- **🌍 True Localization**: Region-specific financial advice and regulations
- **👥 Social Learning**: Learn with peers and connect with mentors

## 📱 Key Features

### Core Capabilities
- **Hybrid Chat Interface**: Voice + Text input with visual responses
- **Real-time Market Data**: Live stock prices, news, and analysis
- **Personalized Advisory**: Tailored advice based on your goals and risk profile
- **Offline Mode**: Core features work without internet connection

### Unique Innovations
1. **Adaptive Explanation Levels**
   - Student Mode: Simple, educational explanations
   - Professional Mode: Technical analysis and advanced metrics
   - Elder Mode: Large text, slower speech, simplified terms

2. **Financial Therapy Mode**
   - Detects panic selling/FOMO buying
   - Provides emotional support during market volatility
   - Guides through decision-making frameworks

3. **Visual Context Understanding**
   - Point camera at any financial document
   - Get instant voice explanations
   - Interactive chart analysis

4. **Goal-Based Journey**
   - First Job → Emergency Fund
   - Marriage → Joint Planning
   - Kids → Education Fund
   - Retirement → Pension Optimization

## 🏗️ Architecture

```
FinMentor AI/
├── 📱 Flutter App (iOS/Android)
│   ├── Voice Interface (STT/TTS)
│   ├── Visual Components (Charts/Graphs)
│   ├── Offline Storage (SQLite)
│   └── State Management (Riverpod)
│
└── 🐍 Python Backend (FastAPI)
    ├── Multi-Agent System
    │   ├── Advisor Agent (Query Router)
    │   ├── Data Agent (Market Data)
    │   ├── Analysis Agent (Calculations)
    │   ├── Psychology Agent (Behavioral)
    │   └── Education Agent (Learning)
    ├── External APIs
    │   ├── Yahoo Finance
    │   ├── News APIs
    │   └── Economic Data
    └── Database (PostgreSQL + Redis)
```

## 🛠️ Tech Stack

### Mobile App (Flutter)
- **Framework**: Flutter 3.0+
- **State Management**: Riverpod
- **Voice**: speech_to_text, flutter_tts
- **HTTP Client**: Dio
- **Local Storage**: SQLite, Hive
- **Charts**: fl_chart, syncfusion_flutter_charts

### Backend (Python)
- **Framework**: FastAPI
- **Multi-Agent**: LangChain
- **Database**: PostgreSQL + Redis
- **ML/AI**: OpenAI API, Anthropic Claude
- **Data Sources**: yfinance, Alpha Vantage
- **Deployment**: Docker + Railway/Render

## 🚀 Quick Start

### Prerequisites
- Flutter SDK 3.0+
- Python 3.9+
- PostgreSQL 14+
- Redis 7+
- Android Studio / Xcode (for mobile development)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/finmentor-ai.git
cd finmentor-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Flutter App Setup

```bash
# Navigate to Flutter app directory
cd ../flutter_app

# Install dependencies
flutter pub get

# Run the app
flutter run

# For specific platform
flutter run -d ios      # iOS
flutter run -d android  # Android
```

## 📱 Project Structure

```
finmentor-ai/
├── flutter_app/           # Mobile application
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/      # UI screens
│   │   ├── widgets/      # Reusable components
│   │   ├── services/     # API, Voice, Storage
│   │   ├── models/       # Data models
│   │   └── providers/    # State management
│   └── assets/           # Images, fonts, etc.
│
├── backend/              # Python FastAPI backend
│   ├── main.py          # FastAPI application
│   ├── agents/          # Multi-agent system
│   ├── routers/         # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── utils/           # Helper functions
│
└── docs/                # Documentation
    ├── API.md
    ├── AGENTS.md
    └── DEPLOYMENT.md
```

## 🎯 Development Roadmap

### Phase 1: Foundation (Week 1-2) ✅
- [x] Market research and competitive analysis
- [x] System architecture design
- [ ] Flutter project setup
- [ ] FastAPI backend setup
- [ ] Basic chat interface

### Phase 2: Core Features (Week 3-4)
- [ ] Multi-agent system implementation
- [ ] Voice input integration
- [ ] Text-to-Speech responses
- [ ] Real-time market data integration
- [ ] Basic financial calculations

### Phase 3: Unique Features (Week 5-6)
- [ ] Progressive learning system
- [ ] Behavioral coaching
- [ ] Visual context understanding
- [ ] Offline mode
- [ ] Localization (2 regions)

### Phase 4: Polish & Testing (Week 7-8)
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] User testing
- [ ] Bug fixes
- [ ] Documentation

## 🎓 Learning Curriculum

### Level 1: Financial Basics
- What is saving and budgeting?
- Understanding income vs expenses
- Emergency fund basics

### Level 2: Investing Fundamentals
- Introduction to stocks and bonds
- Mutual funds and ETFs
- Risk and return concepts

### Level 3: Advanced Strategies
- Portfolio diversification
- Tax-efficient investing
- Retirement planning

### Level 4: Expert Topics
- Options and derivatives
- Alternative investments
- Quantitative analysis

## 📊 API Endpoints

### Core Endpoints
```
POST /api/chat          - Process user query (text/voice)
GET  /api/market/stock  - Get stock price and data
GET  /api/news          - Get financial news
POST /api/analyze       - Analyze portfolio/investment
GET  /api/education     - Get learning content
```

### User Management
```
POST /api/auth/register - User registration
POST /api/auth/login    - User login
GET  /api/user/profile  - Get user profile
PUT  /api/user/settings - Update preferences
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Flutter tests
cd flutter_app
flutter test

# Integration tests
flutter drive --target=test_driver/app.dart
```

## 📈 Performance Targets

- **Response Time**: < 2 seconds for voice queries
- **Offline Mode**: 80% features available offline
- **Accuracy**: 95% for market data, 90% for advice relevance
- **Uptime**: 99.9% availability
- **Scalability**: Support 10,000 concurrent users

## 🔒 Security & Privacy

- **End-to-end encryption** for sensitive data
- **Local voice processing** option for privacy
- **No storage** of financial credentials
- **GDPR/CCPA compliant** data handling
- **Regular security audits**

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- FastAPI for high-performance Python backend
- OpenAI Whisper for speech recognition
- LangChain for multi-agent orchestration
- Yahoo Finance for market data APIs

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for features
- **Email**: support@finmentor-ai.com
- **Discord**: Join our community server

## ⚠️ Disclaimer

FinMentor AI is an educational tool designed to improve financial literacy. It should not be considered as professional financial advice. Always consult with qualified financial advisors for investment decisions.

---

**Built with ❤️ for financial inclusion and education**

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)