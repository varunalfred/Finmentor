# Important Design Decisions & Patterns

## 1. Singleton vs Per-Request Pattern

### DatabaseService - SINGLETON ✅
**What:** Single instance for entire application lifetime
**Why:** Holds connection pool/factory, not actual connections
**How:**
```python
class DatabaseService:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.engine = create_async_engine(...)  # Pool
        self.AsyncSessionLocal = sessionmaker(...)  # Factory
```
**Usage:** `db_service.AsyncSessionLocal()` creates NEW session per request

### AuthService - PER-REQUEST ✅
**What:** New instance created for each HTTP request
**Why:** Holds database session (stateful, transaction-scoped)
**How:**
```python
def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)  # New instance with fresh session

@router.post("/login")
async def login(auth_service: AuthService = Depends(get_auth_service)):
    ...  # Each request gets own AuthService + own db session
```
**Critical:** Session is per-request, not shared across requests

---

## 2. LangChain Version Compatibility

### Decision: Use LangChain 0.2.x (Stable)
**What:** Pinned to specific stable version
**Why:** 
- LangChain 0.3.x has breaking import changes
- 0.2.x is well-documented and stable
- Import paths are consistent

**Versions:**
```txt
langchain==0.2.16
langchain-core==0.2.38
langchain-community==0.2.16
langchain-openai==0.1.23
langchain-google-genai==1.0.10
```

**Removed:** Try-except fallback blocks for multiple versions
**Reason:** We pin versions in requirements.txt, so multi-version support adds unnecessary complexity

---

## 2.5. DSPy LLM Configuration (CRITICAL!)

### Decision: Use dspy.LM() with LiteLLM format
**What:** DSPy uses LiteLLM under the hood for all LLM providers
**Why:** 
- Modern DSPy (3.x) removed provider-specific classes (`dspy.Google`, `dspy.OpenAI`, etc.)
- Uses unified `dspy.LM()` interface with "provider/model" format
- LiteLLM handles API compatibility across 100+ providers

**How:**
```python
# ❌ OLD (doesn't work in DSPy 3.x)
lm = dspy.Google(api_key="...", model="gemini-pro")
lm = dspy.OpenAI(model="gpt-3.5-turbo")

# ✅ NEW (correct for DSPy 3.x)
# API keys should be in environment variables
lm = dspy.LM(model="gemini/gemini-1.5-flash")
lm = dspy.LM(model="openai/gpt-3.5-turbo")
lm = dspy.LM(model="anthropic/claude-3-haiku-20240307")
```

**Supported Providers:**
- Gemini: `gemini/gemini-1.5-flash`, `gemini/gemini-1.5-pro`
- OpenAI: `openai/gpt-3.5-turbo`, `openai/gpt-4`
- Claude: `anthropic/claude-3-haiku-20240307`, `anthropic/claude-3-sonnet-20240229`

**Environment Variables:**
- Gemini: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Claude: `ANTHROPIC_API_KEY`

---

## 3. DuckDuckGo Search - Sync Only

### Decision: Use ddgs package (renamed from duckduckgo-search)
**What:** DuckDuckGo Search integration for web searches without API keys
**Why:** 
- Package was renamed from `duckduckgo-search` to `ddgs` (version 9.7.1+)
- Newer versions removed AsyncDDGS (async version)
- Sync version is fast enough for our use case

**How:**
```python
from ddgs import DDGS  # New package name

self.ddg_sync = DDGS()
# Use in async context (runs fast enough)
results = self.ddg_sync.text(query, max_results=5)
```

**Package:**
```txt
# Old (deprecated)
duckduckgo-search==6.3.5

# New (current)
ddgs==9.7.1
```

**Impact:** Minimal - search is fast, async overhead not needed

---

## 4. PGVector - Optional Feature

### Decision: Graceful fallback to JSON
**What:** System works with or without PGVector extension
**Why:** Not all PostgreSQL installations have PGVector
**How:**
```python
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False

# In model:
embedding = Column(Vector(1536) if PGVECTOR_AVAILABLE else JSON)
```
**Trade-off:** JSON embeddings work but less efficient for similarity search

---

## 5. Service Layer Architecture

### Pattern: Service + Repository
**What:** Business logic in services, data access in services
**Why:** Separation of concerns, testability, reusability

**Structure:**
```
routers/        → HTTP endpoints (thin layer)
    ↓
services/       → Business logic (AuthService, ConversationService)
    ↓
models/         → Database models (User, Message, etc.)
```

**Example:**
```python
# Router (thin)
@router.post("/login")
async def login(auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.authenticate_user(username, password)
    return create_token(user)

# Service (thick - has business logic)
class AuthService:
    async def authenticate_user(self, username, password):
        # 1. Find user
        # 2. Verify password
        # 3. Update last login
        # 4. Log activity
        return user
```

---

## 6. ConversationService Integration

### Decision: AuthService uses ConversationService
**What:** Auth events logged via conversation service
**Why:** Track user activity, audit trail, analytics
**How:**
```python
class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_service = ConversationService(db)
    
    async def authenticate_user(...):
        # After successful login
        await self.conversation_service.log_user_activity(
            user_id=user.id,
            activity_type="login",
            details={"username": username}
        )
```
**Benefit:** Centralized activity logging, user statistics

---

## 7. Database Session Management

### Pattern: FastAPI Dependency Injection
**What:** Sessions created/destroyed per request automatically
**How:**
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_service.AsyncSessionLocal() as session:
        try:
            yield session  # Endpoint uses session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Auto-rollback on error
        finally:
            await session.close()  # Always close
```
**Benefits:**
- No manual session management
- Automatic cleanup
- Transaction safety

---

## 8. Environment-Based Configuration

### Decision: .env for secrets, code for defaults
**What:** Sensitive data in .env, safe defaults in code
**How:**
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/finmentor")
```
**Security:**
- Production: All values in .env
- Development: Defaults work out-of-box
- Never commit .env to git

---

## 9. API Provider Fallback Chain

### Pattern: Primary → Fallback → Local
**What:** Multiple providers with graceful degradation

**LLM Providers:**
1. Gemini (free tier, primary)
2. OpenAI (paid, fallback)
3. SentenceTransformers (local, last resort)

**Search Providers:**
1. DuckDuckGo (free, always available)
2. Google Custom Search (optional, paid)
3. SerpAPI (optional, paid)

**Why:** System works in multiple configurations (free, premium, offline)

---

## 10. JWT Token Authentication

### Pattern: Stateless bearer tokens
**What:** JWT tokens for user authentication
**How:**
```python
# Create token
token = jwt.encode(
    {"sub": username, "user_id": user.id, "exp": expiry},
    SECRET_KEY,
    algorithm="HS256"
)

# Verify token
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```
**Benefits:**
- No server-side session storage needed
- Scalable (stateless)
- Standard OAuth2 compatible

**Security:**
- 30-minute expiry
- Refresh token support
- Logout via client-side token discard

---

## 11. Code Simplification Rules

### When to Keep Compatibility Code
✅ **KEEP** for:
- Optional features (PGVector, premium APIs)
- Multiple valid providers (Gemini/OpenAI/Local)
- External dependencies we don't control

❌ **REMOVE** for:
- Libraries we pin in requirements.txt
- Deprecated patterns
- Unused fallback paths

**Example:**
```python
# ✅ GOOD - Optional feature
try:
    from pgvector import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

# ❌ BAD - We pin LangChain version anyway
try:
    from langchain.agents import create_react_agent
except ImportError:
    try:
        from langchain_community.agents import create_react_agent
    except ImportError:
        create_react_agent = None
```

---

## 12. Import Organization

### Standard Order:
```python
# 1. Standard library
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select
import dspy

# 3. Local imports
from models.database import User
from services.database import get_db
from services.auth_service import AuthService
```

**Why:** Readability, PEP 8 compliance, easier to track dependencies

---

## 13. Error Handling Pattern

### Standard Pattern:
```python
try:
    # Business logic
    result = await service.do_something()
    return success_response(result)
    
except HTTPException:
    raise  # Re-raise HTTP exceptions as-is
    
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    raise HTTPException(status_code=400, detail="User-friendly message")
    
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Principles:**
- Catch specific exceptions first
- Log errors for debugging
- Return user-friendly messages
- Don't expose internal details

---

## 14. Async/Await Usage

### When to Use Async:
✅ **DO** use for:
- Database operations
- HTTP requests
- File I/O
- Any I/O-bound operations

❌ **DON'T** use for:
- CPU-bound calculations
- Simple data transformations
- Synchronous library calls

**Example:**
```python
# ✅ Good
async def get_user(user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ❌ Unnecessary
async def calculate_sum(a: int, b: int):  # Pure computation
    return a + b
```

---

## 15. Testing Strategy

### Levels:
1. **Unit Tests** - Individual functions/methods
2. **Integration Tests** - Services + database
3. **API Tests** - Full endpoint testing

### Test Files Location:
```
tests/
    test_01_initial_setup.py       # Environment, deps, DB
    test_db_connection.py          # Database connectivity
    test_multiagent.py             # Agent system
    test_singletons.py             # Singleton patterns
```

**Run tests:** `pytest tests/` (when implemented)

---

## Quick Reference

| Pattern | When to Use |
|---------|-------------|
| **Singleton** | Connection pools, factories, config managers |
| **Per-Request** | Business logic services with DB sessions |
| **Try-Except** | Optional features, external dependencies |
| **Async** | I/O operations (DB, HTTP, files) |
| **Dependency Injection** | Session management, service creation |
| **Environment Variables** | Secrets, API keys, database URLs |

---

**Last Updated:** November 5, 2025
**Maintained By:** Development Team
