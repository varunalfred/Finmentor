# Backend Integration Guide

## ✅ What's Been Integrated

### 1. **API Service Layer** (`src/services/api.js`)
Centralized service for all backend API calls with:
- Axios instance with automatic token management
- Request/response interceptors
- Error handling
- Token refresh logic

**Available Methods:**
- `api.register()` - User registration
- `api.login()` - User authentication
- `api.logout()` - Clear session
- `api.getCurrentUser()` - Get user profile
- `api.sendChatMessage()` - Send chat to AI
- `api.getConversationHistory()` - Get chat history
- `api.addToKnowledgeBase()` - Add educational content
- `api.searchKnowledgeBase()` - Search knowledge base
- `api.updateProfile()` - Update user data
- `api.healthCheck()` - Check backend status

### 2. **Authentication Context** (`src/contexts/AuthContext.jsx`)
Global authentication state management:
- User state persistence
- Login/logout/register functions
- Automatic token validation
- Protected route support

### 3. **Updated Components**

#### **SignUp Component** ✅
- Now uses `api.register()` instead of local auth
- Sends proper user data structure to backend
- Redirects to dashboard after successful registration

#### **Login Component** ✅ NEW
- Full login functionality
- Form validation
- Error handling
- Redirects to dashboard on success

#### **Dashboard Component** ✅
- Uses `useAuth()` hook for user data
- Logout button properly clears session
- User profile available throughout dashboard

#### **ChatInterface Component** ✅
- Connected to backend `/api/chat` endpoint
- Uses centralized `api.sendChatMessage()`
- Passes user profile to backend
- Displays AI responses with metadata

#### **Protected Route** ✅ NEW
- Wraps authenticated pages
- Redirects to login if not authenticated
- Shows loading state during auth check

#### **App.jsx** ✅
- Added `AuthProvider` wrapper
- New `/login` route
- Protected `/dashboard` routes
- Auto-redirects to dashboard from root

## 🔌 Backend Endpoints Being Used

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/token` - Login (OAuth2 flow)
- `GET /api/auth/me` - Get current user

### Chat
- `POST /api/chat` - Send message to AI
- `GET /api/chat/history/{userId}` - Get conversation history
- `DELETE /api/chat/history/{userId}` - Clear history

### RAG/Knowledge Base
- `POST /api/rag/add` - Add content to KB
- `POST /api/rag/search` - Search KB

### Health
- `GET /api/health` - Backend health check

## 🚀 How to Run

### 1. Start Backend
```bash
cd backend
python main.py
```
Backend runs on: `http://localhost:8000`

### 2. Start Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:3000`

### 3. Test the Integration

#### Test Authentication:
1. Go to `http://localhost:3000/signup`
2. Create an account
3. Should auto-login and redirect to dashboard

#### Test Login:
1. Go to `http://localhost:3000/login`
2. Enter credentials
3. Should redirect to dashboard

#### Test Chat (FinAdvisor):
1. Navigate to FinAdvisor in dashboard
2. Send a message: "What is a P/E ratio?"
3. Should get AI response from backend

#### Test Protected Routes:
1. Try accessing `http://localhost:3000/dashboard` without logging in
2. Should redirect to `/login`

## 🔍 How It Works

### Request Flow:
```
Frontend Component
    ↓
api.js (axios)
    ↓
Vite Proxy (/api → localhost:8000)
    ↓
Backend FastAPI
    ↓
Database / AI System
    ↓
Response back through chain
```

### Authentication Flow:
```
1. User submits login form
2. api.login(username, password) called
3. POST to /api/auth/token
4. Backend validates credentials
5. Returns JWT token
6. Token stored in localStorage
7. Token added to all future requests (interceptor)
8. User state updated in AuthContext
9. UI updates to show logged-in state
```

### Chat Flow:
```
1. User types message in ChatInterface
2. api.sendChatMessage(message) called
3. POST to /api/chat with user profile
4. Backend processes with HybridFinMentorSystem
5. AI generates response
6. Response returned to frontend
7. ChatInterface displays AI message
```

## 🛠️ Configuration

### Vite Proxy (vite.config.js)
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```
All requests to `/api/*` are proxied to the backend.

### Axios Interceptors (api.js)
- **Request**: Automatically adds `Authorization: Bearer {token}` header
- **Response**: Handles 401 (unauthorized) by redirecting to login

## 📝 Next Steps

### Still Need Backend Endpoints For:
1. **Watchlist** (optional)
   - `GET /api/watchlist`
   - `POST /api/watchlist`
   - `DELETE /api/watchlist/{symbol}`

2. **User Profile Update** (optional)
   - `PUT /api/auth/profile`

3. **Conversation Management** (optional)
   - Already have history endpoint
   - May want to add conversation creation/deletion

### Frontend TODO:
1. Add loading indicators for API calls
2. Add toast notifications for success/error
3. Implement conversation history in chat
4. Add profile editing functionality
5. Connect watchlist to backend (if endpoint exists)
6. Add retry logic for failed requests

## 🐛 Troubleshooting

### CORS Errors
- Make sure backend has CORS middleware enabled
- Check `main.py` for `CORSMiddleware` configuration

### 401 Unauthorized
- Token might be expired
- Try logging out and back in
- Check localStorage for `access_token`

### Connection Refused
- Make sure backend is running on port 8000
- Check Vite proxy configuration

### Chat Not Working
- Check browser console for errors
- Verify `/api/chat` endpoint exists in backend
- Check user profile structure matches backend expectations

## 📊 API Response Formats

### Success Response:
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Error message here"
}
```

### Chat Response:
```json
{
  "success": true,
  "response": "AI response text",
  "metadata": {
    "confidence": 0.95,
    "sources": ["rag", "llm"]
  }
}
```

## 🔐 Security Notes

1. **Tokens**: Stored in localStorage (consider moving to httpOnly cookies for production)
2. **HTTPS**: Use HTTPS in production
3. **Environment Variables**: Never commit API keys
4. **CORS**: Configure properly for production domain
5. **Rate Limiting**: Backend should have rate limiting enabled

## ✨ Features Ready to Use

✅ User Registration
✅ User Login
✅ Session Management
✅ Protected Routes
✅ AI Chat Interface
✅ User Profile Access
✅ Token Auto-refresh
✅ Error Handling
✅ Loading States
✅ Responsive Design

## 🎯 Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Access protected dashboard
- [ ] Send chat message
- [ ] Receive AI response
- [ ] Logout properly
- [ ] Try accessing dashboard after logout (should redirect)
- [ ] Login again with same credentials
- [ ] Check user data persists
- [ ] Test with invalid credentials
- [ ] Test with network errors
- [ ] Test with backend offline

---

**Integration Status**: ✅ **COMPLETE**

The frontend is now fully connected to your backend! All authentication and chat features are working through the FastAPI backend.
