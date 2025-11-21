# Testing TODO List - Smart Orchestrator & Multi-Agent System

## 📋 Test Script Availability Summary

**Status:** 8/11 test scripts available ✅  
**Missing:** 2 test scripts need to be created ⚠️  
**Manual Testing:** 1 item requires manual testing ℹ️

---

## Phase 1: Foundation Tests (Database & Core Features)

### ✅ Test 1: Database Connection
- **File:** `tests/test_db_connection.py`
- **Status:** Script EXISTS ✅
- **Command:** `python tests/test_db_connection.py`
- **What it tests:**
  - PostgreSQL connection
  - PGVector extension installed
  - Database tables created
  - Connection pooling works
- **Expected Result:** "✅ Database connection successful!"

### ✅ Test 2: RAG-First Implementation
- **File:** `tests/test_rag_first.py`
- **Status:** Script EXISTS ✅
- **Command:** `python tests/test_rag_first.py`
- **What it tests:**
  - Knowledge base queried before LLM calls
  - ConceptExplanation signature has KB fields
  - FinancialAnalysis signature has KB fields
  - Source attribution works
  - Relevance scoring functional
- **Expected Result:** RAG context retrieved with sources

### ✅ Test 3: Individual Agents
- **File:** `tests/test_individual_agents.py`
- **Status:** Script EXISTS ✅
- **Command:** `python tests/test_individual_agents.py`
- **What it tests:**
  - All 13 specialized agents individually
  - 6-second delays (safe for 10 RPM free tier)
  - Each DSPy signature works correctly
  - Keyword validation
  - KB usage tracking
- **Expected Time:** ~78 seconds (13 agents × 6 seconds)
- **Expected Result:** Success rate report for all agents

---

## Phase 2: Core Component Tests (Rate Limiting & Dependencies)

### ✅ Test 4: Rate Limiting
- **File:** `tests/test_smart_orchestrator.py` (function: `test_rate_limiting()`)
- **Status:** Function EXISTS ✅ (inside smart orchestrator test)
- **Command:** Run as part of smart orchestrator suite OR extract to standalone
- **What it tests:**
  - TokenBucketRateLimiter (10 RPM enforcement)
  - RateLimitedExecutor (2 concurrent batching)
  - 15 requests with 10 RPM limit
  - Token refill mechanism
- **Expected Result:** "✅ Rate limiting test complete!"
- **Note:** Currently commented out in main test to save time

### ✅ Test 5: Dependency Graph
- **File:** `tests/test_smart_orchestrator.py` (function: `test_dependency_graph()`)
- **Status:** Function EXISTS ✅ (inside smart orchestrator test)
- **Command:** Run as part of smart orchestrator suite
- **What it tests:**
  - Agent dependencies correctly defined
  - Execution stages built properly
  - Circular dependency detection
  - Invalid agent selection handling
- **Expected Result:** "✅ Dependency graph test complete!"

---

## Phase 3: Smart Orchestrator Tests

### ✅ Test 6: Smart Orchestrator - Simple Query
- **File:** `tests/test_smart_orchestrator.py` (function: `test_smart_orchestrator_simple()`)
- **Status:** Function EXISTS ✅
- **Command:** Run as part of smart orchestrator suite
- **What it tests:**
  - Single agent execution (EDUCATION)
  - Rate limiting for simple query
  - Response generation
  - Metadata tracking
- **Test Query:** "What is a P/E ratio?"
- **Expected Agents:** 1 (EDUCATION)
- **Expected Stages:** 1
- **Expected Time:** ~3 seconds

### ✅ Test 7: Smart Orchestrator - Complex Query
- **File:** `tests/test_smart_orchestrator.py` (function: `test_smart_orchestrator_complex()`)
- **Status:** Function EXISTS ✅
- **Command:** Run as part of smart orchestrator suite
- **What it tests:**
  - Multi-agent execution (5 agents)
  - Dependency-aware staging
  - Context passing between agents
  - Batched parallel execution (2 concurrent)
  - Rate-limited execution
- **Test Query:** "I want to invest $10,000 in technology stocks. What should I do?"
- **Expected Agents:** 5 (MARKET_ANALYST, TECHNICAL_ANALYSIS, RISK_ASSESSMENT, PORTFOLIO_OPTIMIZER, TAX_ADVISOR)
- **Expected Stages:** 4
- **Expected Time:** ~12 seconds
- **Expected Flow:**
  ```
  Stage 0: [MARKET_ANALYST, TECHNICAL_ANALYSIS] → parallel
  Stage 1: [RISK_ASSESSMENT] → uses Stage 0 outputs
  Stage 2: [PORTFOLIO_OPTIMIZER] → uses Stage 1 output
  Stage 3: [TAX_ADVISOR] → uses Stage 2 output
  ```

### ✅ Test 8: Smart Orchestrator - Full Suite
- **File:** `tests/test_smart_orchestrator.py`
- **Status:** Script EXISTS ✅
- **Command:** `python tests/test_smart_orchestrator.py`
- **What it tests:**
  - All of the above (Tests 4-7)
  - Dependency validation
  - Rate limit enforcement
  - Stress tests (commented out by default)
- **Includes:**
  - `test_dependency_graph()`
  - `test_rate_limiting()` (commented out)
  - `test_smart_orchestrator_simple()`
  - `test_smart_orchestrator_complex()`
  - `test_rate_limit_enforcement()` (commented out)
- **Expected Result:** "✅ ALL TESTS COMPLETE!"

---

## Phase 4: Integration Tests (API & End-to-End)

### ℹ️ Test 9: Main Application Startup
- **File:** `main.py`
- **Status:** Manual testing required ℹ️
- **Command:** `uvicorn main:app --reload`
- **What to verify:**
  - FastAPI server starts without errors
  - SmartMultiAgentOrchestrator initializes
  - Rate limiting configured (10 RPM, 2 concurrent)
  - Database connection established
  - Health endpoint responds
- **Endpoints to check:**
  - `http://localhost:8000/` - Root
  - `http://localhost:8000/health` - Health check
  - `http://localhost:8000/docs` - Swagger UI
- **Expected Logs:**
  ```
  INFO: Starting FinMentor AI Backend...
  INFO: Database initialized
  INFO: Multi-agent system initialized with rate limiting (10 RPM, 2 concurrent)
  INFO: Backend started successfully!
  INFO: Uvicorn running on http://127.0.0.1:8000
  ```

### ⚠️ Test 10: API Endpoints
- **File:** `tests/test_api_endpoints.py`
- **Status:** NEEDS TO BE CREATED ⚠️
- **What it should test:**
  - Chat endpoint POST request
  - Authentication (if enabled)
  - Request/response format
  - Error handling
  - Rate limiting via API
- **Test Cases:**
  ```python
  # Simple query
  POST /api/chat
  {
    "message": "What is a P/E ratio?",
    "user_id": "test_user"
  }
  
  # Complex query
  POST /api/chat
  {
    "message": "Analyze my portfolio",
    "user_id": "test_user",
    "context": {"portfolio": [...]}
  }
  ```
- **Alternative:** Manual testing with Postman/curl/FastAPI docs

### ⚠️ Test 11: Multi-Agent Integration (End-to-End)
- **File:** `tests/test_e2e_integration.py`
- **Status:** NEEDS TO BE CREATED ⚠️
- **What it should test:**
  - Full pipeline: User Query → RAG → Intent Detection → Agent Selection → Dependency-Aware Execution → Synthesis → Response
  - Complex multi-agent queries via API
  - Response quality
  - Performance benchmarks
- **Test Scenarios:**
  1. Educational query (simple)
  2. Market analysis query (moderate)
  3. Portfolio optimization query (complex)
  4. Risk assessment query (critical)
- **Success Criteria:**
  - Correct intent detected
  - Appropriate agents selected
  - Execution stages follow dependencies
  - Rate limits respected
  - Coherent final response

---

## Phase 5: Review & Documentation

### Test 12: Review Test Results & Fix Issues
- **Status:** After all tests complete
- **Actions:**
  1. Review all test outputs
  2. Document any failures
  3. Fix errors or warnings
  4. Optimize performance if needed
  5. Update documentation
- **Deliverables:**
  - Test results summary
  - Issue log with resolutions
  - Performance metrics
  - Updated README with test instructions

---

## 🛠️ Scripts to Create

### 1. API Endpoint Test Script

**File:** `tests/test_api_endpoints.py`

**Template:**
```python
"""
API Endpoint Tests
Tests FastAPI endpoints for chat, auth, and orchestration
"""

import requests
import pytest
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_chat_simple_query():
    """Test simple educational query"""
    payload = {
        "message": "What is a P/E ratio?",
        "user_id": "test_user"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0

def test_chat_complex_query():
    """Test complex multi-agent query"""
    payload = {
        "message": "I want to invest $10,000 in tech stocks",
        "user_id": "test_user"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "metadata" in data
    assert data["metadata"]["total_agents"] > 1

def test_rate_limiting():
    """Test rate limiting enforcement"""
    # Send 15 rapid requests
    results = []
    for i in range(15):
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": f"Test query {i}",
            "user_id": "test_user"
        })
        results.append(response.status_code)
    
    # All should succeed (rate limiter handles batching)
    assert all(r == 200 for r in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 2. End-to-End Integration Test Script

**File:** `tests/test_e2e_integration.py`

**Template:**
```python
"""
End-to-End Integration Tests
Tests complete pipeline from query to response
"""

import asyncio
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_educational_query_e2e():
    """Test simple educational query end-to-end"""
    print("\n" + "="*70)
    print("E2E TEST 1: Educational Query")
    print("="*70)
    
    start = datetime.now()
    
    payload = {
        "message": "What is diversification?",
        "user_id": "e2e_test_user"
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print(f"✅ Response received in {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()['response'][:200]}...")

async def test_portfolio_optimization_e2e():
    """Test complex portfolio optimization end-to-end"""
    print("\n" + "="*70)
    print("E2E TEST 2: Portfolio Optimization (Multi-Agent)")
    print("="*70)
    
    start = datetime.now()
    
    payload = {
        "message": "I have $50,000 to invest. I'm 30 years old with moderate risk tolerance. What portfolio allocation do you recommend?",
        "user_id": "e2e_test_user",
        "context": {
            "age": 30,
            "risk_tolerance": "moderate",
            "investment_amount": 50000
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    data = response.json()
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print(f"✅ Response received in {elapsed:.2f}s")
    print(f"Agents used: {data.get('metadata', {}).get('total_agents', 'N/A')}")
    print(f"Stages: {data.get('metadata', {}).get('total_stages', 'N/A')}")
    print(f"Response preview: {data['response'][:300]}...")

if __name__ == "__main__":
    asyncio.run(test_educational_query_e2e())
    asyncio.run(test_portfolio_optimization_e2e())
```

---

## 📊 Testing Priority Order

1. **Phase 1** (Foundation) - CRITICAL ⚠️
   - Must pass before proceeding
   - Database must work for all other tests

2. **Phase 2** (Components) - HIGH PRIORITY 🔴
   - Rate limiting is critical for production
   - Dependency graph ensures correct execution

3. **Phase 3** (Orchestrator) - HIGH PRIORITY 🔴
   - Core functionality of the system
   - Must work before API testing

4. **Phase 4** (Integration) - MEDIUM PRIORITY 🟡
   - Can be tested manually if scripts not ready
   - FastAPI docs provide interactive testing

5. **Phase 5** (Review) - ONGOING ♻️
   - Continuous throughout testing

---

## 🚀 Quick Start Commands

```bash
# Phase 1: Foundation
python tests/test_db_connection.py
python tests/test_rag_first.py
python tests/test_individual_agents.py

# Phase 2 & 3: Components & Orchestrator
python tests/test_smart_orchestrator.py

# Phase 4: Start server
uvicorn main:app --reload

# Phase 4: Manual API testing (in another terminal)
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a P/E ratio?", "user_id": "test"}'

# Or use FastAPI docs
# Visit: http://localhost:8000/docs
```

---

## ✅ Checklist

- [ ] Phase 1: All foundation tests pass
- [ ] Phase 2: Rate limiting and dependency tests pass
- [ ] Phase 3: Smart orchestrator tests pass
- [ ] Phase 4: Server starts without errors
- [ ] Phase 4: API endpoints respond correctly
- [ ] Phase 4: Multi-agent queries work end-to-end
- [ ] Phase 5: All issues documented and resolved
- [ ] Bonus: Create `test_api_endpoints.py` script
- [ ] Bonus: Create `test_e2e_integration.py` script

---

## 📝 Notes

- Tests 1-8 can be run immediately (scripts exist)
- Test 9 is manual (start server and verify)
- Tests 10-11 need scripts OR can test manually
- Rate limiting tests are commented out by default to save time
- Individual agents test takes ~78 seconds (13 agents × 6s delay)
- Complex orchestrator test takes ~12 seconds (4 stages)

---

**Last Updated:** 2025-11-12  
**Status:** Ready for testing ✅  
**Missing Scripts:** 2 (optional - can test manually)
