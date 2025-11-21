# Agent-to-Agent Communication Analysis

## Current Implementation: How Our Agents Communicate

### 🔍 Current Approach: **Context Passing via Enriched Prompts**

Our system uses a **simple but effective** communication pattern:

```python
# Agent A completes
result_a = {"analysis": "Tech sector shows strong growth..."}

# Agent B receives Agent A's output in its prompt
enriched_prompt = f"""
{original_query}

**Context from Market Analyst:**
Tech sector shows strong growth...

Based on the above analysis, assess the risk...
"""

# Agent B processes with context
result_b = process(enriched_prompt)
```

**Flow:**
```
Stage 1: Market Analyst → Analysis: "Tech bullish, P/E ratios high"
         ↓ (stored in memory)
Stage 2: Risk Assessor receives:
         Original Query: "Should I invest in tech?"
         + Context: "Market Analyst says: Tech bullish, P/E ratios high"
         → Produces: "High growth potential, moderate volatility risk"
         ↓ (stored in memory)
Stage 3: Portfolio Optimizer receives:
         Original Query + Market Analysis + Risk Assessment
         → Produces: "60% tech stocks, 40% bonds"
```

---

## 📚 Research: Multi-Agent Communication Protocols

### 1. **ACL (Agent Communication Language)** - FIPA Standard

**What it is:**
- Formal language for agent communication
- Based on speech act theory (inform, request, propose, agree, refuse)
- Industry standard from Foundation for Intelligent Physical Agents (FIPA)

**Message Structure:**
```xml
<message>
  <sender>MarketAnalystAgent</sender>
  <receiver>RiskAssessorAgent</receiver>
  <performative>INFORM</performative>
  <content>
    {
      "market_trend": "bullish",
      "sector": "technology",
      "confidence": 0.85
    }
  </content>
  <ontology>financial-analysis</ontology>
  <protocol>contract-net</protocol>
</message>
```

**Performatives:**
- `INFORM` - Share information
- `REQUEST` - Ask for action
- `PROPOSE` - Suggest a plan
- `ACCEPT/REFUSE` - Respond to proposals
- `QUERY-IF/QUERY-REF` - Ask questions

**Pros:**
- ✅ Standardized
- ✅ Clear semantics
- ✅ Handles complex negotiations

**Cons:**
- ❌ Complex overhead for simple systems
- ❌ Requires message parsing infrastructure
- ❌ Slower than direct passing

---

### 2. **Blackboard Architecture** (Shared Memory)

**What it is:**
- All agents read/write to a shared "blackboard"
- Agents monitor the blackboard for relevant information
- No direct agent-to-agent messages

**Implementation:**
```python
class Blackboard:
    def __init__(self):
        self.data = {
            "market_analysis": None,
            "risk_assessment": None,
            "portfolio_recommendation": None
        }
        self.subscribers = {}
    
    def post(self, key, value, author):
        """Agent posts data to blackboard"""
        self.data[key] = {
            "value": value,
            "author": author,
            "timestamp": datetime.now()
        }
        # Notify subscribers
        if key in self.subscribers:
            for agent in self.subscribers[key]:
                agent.notify(key, value)
    
    def read(self, key):
        """Agent reads data from blackboard"""
        return self.data.get(key)

# Usage
blackboard = Blackboard()

# Market Analyst posts
blackboard.post("market_analysis", {
    "trend": "bullish",
    "confidence": 0.85
}, author="MarketAnalyst")

# Risk Assessor reads
market_data = blackboard.read("market_analysis")
```

**Pros:**
- ✅ Decoupled agents
- ✅ Easy to add new agents
- ✅ Natural for parallel processing

**Cons:**
- ❌ No explicit flow control
- ❌ Race conditions possible
- ❌ Hard to track dependencies

---

### 3. **Message Queue (Event-Driven)**

**What it is:**
- Agents communicate via asynchronous message queues
- Each agent has an inbox
- Messages are delivered asynchronously

**Implementation:**
```python
import asyncio
from collections import deque

class MessageQueue:
    def __init__(self):
        self.queues = {}  # agent_id -> queue
    
    async def send(self, to_agent, message):
        """Send message to agent's inbox"""
        if to_agent not in self.queues:
            self.queues[to_agent] = deque()
        self.queues[to_agent].append(message)
    
    async def receive(self, agent_id):
        """Agent reads from its inbox"""
        if agent_id in self.queues and self.queues[agent_id]:
            return self.queues[agent_id].popleft()
        return None

# Usage
mq = MessageQueue()

# Market Analyst sends to Risk Assessor
await mq.send("risk_assessor", {
    "from": "market_analyst",
    "type": "market_analysis",
    "data": {"trend": "bullish"}
})

# Risk Assessor receives
message = await mq.receive("risk_assessor")
```

**Pros:**
- ✅ Asynchronous (no blocking)
- ✅ Scalable
- ✅ Can replay messages

**Cons:**
- ❌ More complex error handling
- ❌ Message ordering issues
- ❌ Requires queue infrastructure

---

### 4. **Contract Net Protocol** (Negotiation)

**What it is:**
- Agents negotiate via bidding
- Manager agent announces task
- Agents bid based on capability
- Manager selects best bidder

**Flow:**
```
Manager: "I need a risk assessment"
         ↓
Agent A: "I can do it, confidence: 0.7, cost: 5 tokens"
Agent B: "I can do it, confidence: 0.9, cost: 8 tokens"
Agent C: "I cannot do this task"
         ↓
Manager: Selects Agent B (highest confidence)
         ↓
Agent B: Executes task, returns result
```

**Implementation:**
```python
class ContractNet:
    async def announce_task(self, task):
        """Manager announces task"""
        bids = []
        for agent in self.agents:
            bid = await agent.bid(task)
            if bid:
                bids.append((agent, bid))
        
        # Select best bid
        winner = max(bids, key=lambda x: x[1]["confidence"])
        result = await winner[0].execute(task)
        return result

class Agent:
    async def bid(self, task):
        """Agent evaluates if it can do task"""
        if self.can_handle(task):
            return {
                "confidence": self.estimate_confidence(task),
                "cost": self.estimate_cost(task)
            }
        return None
```

**Pros:**
- ✅ Optimal agent selection
- ✅ Handles agent failures
- ✅ Load balancing

**Cons:**
- ❌ High overhead
- ❌ Complex for simple tasks
- ❌ Slow (negotiation takes time)

---

### 5. **Direct Method Invocation** (Our Current Approach)

**What it is:**
- Agents directly call each other's methods
- Results passed as function parameters
- Orchestrator manages the flow

**Implementation:**
```python
# What we currently do
async def execute_pipeline(query):
    # Stage 1
    market_result = await market_analyst.analyze(query)
    
    # Stage 2 - receives Stage 1 output
    risk_result = await risk_assessor.assess(
        query=query,
        market_context=market_result  # Direct passing
    )
    
    # Stage 3 - receives Stage 1 & 2 outputs
    portfolio_result = await portfolio_optimizer.optimize(
        query=query,
        market_context=market_result,
        risk_context=risk_result
    )
    
    return portfolio_result
```

**Pros:**
- ✅ Simple and fast
- ✅ Easy to debug
- ✅ Clear data flow
- ✅ No infrastructure overhead
- ✅ Type-safe with Python typing

**Cons:**
- ❌ Tight coupling
- ❌ Hard to parallelize (we solved with stages!)
- ❌ No async retry/recovery

---

## 🎯 Comparison Table

| Protocol | Complexity | Speed | Scalability | Best For |
|----------|-----------|-------|-------------|----------|
| **Direct Invocation** (Ours) | ⭐ Low | ⭐⭐⭐ Fast | ⭐⭐ Medium | Simple pipelines, clear dependencies |
| **ACL** | ⭐⭐⭐ High | ⭐⭐ Medium | ⭐⭐⭐ High | Complex negotiations, distributed systems |
| **Blackboard** | ⭐⭐ Medium | ⭐⭐⭐ Fast | ⭐⭐⭐ High | Many parallel agents, emergent behavior |
| **Message Queue** | ⭐⭐ Medium | ⭐⭐ Medium | ⭐⭐⭐ High | Async processing, event-driven |
| **Contract Net** | ⭐⭐⭐ High | ⭐ Slow | ⭐⭐⭐ High | Dynamic agent selection, load balancing |

---

## 💡 Recommendation for Our System

### Current Implementation is GOOD! ✅

**Why:**
1. **Clear Dependencies** - We know Risk Assessor needs Market Analyst
2. **Rate Limits** - Can't afford async complexity with 10 RPM
3. **Debugging** - Easy to trace data flow
4. **Performance** - No message parsing overhead

### When to Consider Alternatives:

**Use Blackboard if:**
- ❌ We have 20+ agents (currently have ~13)
- ❌ Agents don't have clear dependencies (ours do!)
- ❌ Need emergent behavior (not our use case)

**Use Message Queue if:**
- ❌ Processing millions of requests (we're on free tier!)
- ❌ Need async retry/recovery (LLM calls are expensive to retry)
- ❌ Distributed across servers (single server is fine)

**Use ACL if:**
- ❌ Building a marketplace of agents
- ❌ Agents from different vendors
- ❌ Complex negotiations needed

**Use Contract Net if:**
- ❌ Multiple agents can do same task
- ❌ Need dynamic load balancing
- ❌ Agent availability changes

### Our Sweet Spot: Enhanced Direct Invocation ✅

**What we have:**
```python
# Simple, clear, fast
Stage 1: [Agent A, Agent B] → parallel (2 concurrent, rate limited)
Stage 2: [Agent C] → receives A & B outputs in enriched prompt
Stage 3: [Agent D, Agent E] → parallel, receive C's output

# No complex protocols needed!
# Direct passing with dependency graph = perfect!
```

---

## 🚀 Potential Enhancement: Structured Message Passing

**If** we want to make communication more robust (without the overhead), we could add a **lightweight message structure**:

```python
from dataclasses import dataclass
from typing import Any, Dict
from enum import Enum

class MessageType(Enum):
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"
    QUERY = "query"

@dataclass
class AgentMessage:
    """Lightweight message structure"""
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    confidence: float
    timestamp: datetime
    
    def to_context_string(self) -> str:
        """Convert to enriched prompt context"""
        return f"""
**{self.from_agent.replace('_', ' ').title()}:**
Type: {self.message_type.value}
Confidence: {self.confidence:.2f}
{json.dumps(self.content, indent=2)}
"""

# Usage in orchestrator
class EnhancedOrchestrator:
    async def _build_enriched_query(self, query: str, messages: List[AgentMessage]) -> str:
        """Build query with structured messages"""
        if not messages:
            return query
        
        context_parts = [msg.to_context_string() for msg in messages]
        
        return f"""
{query}

**Context from Previous Agents:**
{"".join(context_parts)}

Based on the above context, provide your analysis.
"""

# Agent creates message
message = AgentMessage(
    from_agent="market_analyst",
    to_agent="risk_assessor",
    message_type=MessageType.ANALYSIS,
    content={
        "trend": "bullish",
        "sector": "technology",
        "key_metrics": {"pe_ratio": 25, "growth_rate": 0.15}
    },
    confidence=0.85,
    timestamp=datetime.now()
)
```

**Benefits:**
- ✅ Structured data (easier to parse)
- ✅ Confidence tracking
- ✅ Message types (analysis vs warning vs recommendation)
- ✅ Still simple (no protocol overhead)
- ✅ Better logging/debugging

**Trade-offs:**
- ⚠️ More code (but not much)
- ⚠️ Still not distributed (fine for our use case)

---

## 📊 Our Communication Pattern (Detailed)

### Current Flow:

```
1. Orchestrator receives query
   ↓
2. Dependency Graph determines stages:
   Stage 0: [Market Analyst, Technical Analysis]
   Stage 1: [Risk Assessment]
   Stage 2: [Portfolio Optimizer]
   Stage 3: [Tax Advisor]
   ↓
3. Stage 0 executes (parallel):
   - Market Analyst analyzes query
   - Technical Analysis analyzes query
   Both get: Original query only
   ↓
4. Results stored in dictionary:
   all_results = {
       AgentType.MARKET_ANALYST: {
           "agent": "market_analyst",
           "result": {"analysis": "Tech sector bullish..."},
           "success": True
       },
       AgentType.TECHNICAL_ANALYSIS: {
           "agent": "technical_analysis",
           "result": {"indicators": "RSI overbought..."},
           "success": True
       }
   }
   ↓
5. Stage 1 executes:
   - Risk Assessment checks dependencies: needs MARKET_ANALYST, TECHNICAL_ANALYSIS
   - Orchestrator builds enriched query:
     """
     Original query: Should I invest in tech?
     
     Context from Market Analyst:
     Tech sector bullish, strong fundamentals...
     
     Context from Technical Analysis:
     RSI overbought, potential pullback...
     
     Based on this, assess the risk...
     """
   - Risk Assessment processes enriched query
   ↓
6. Stage 2 executes:
   - Portfolio Optimizer receives outputs from Stage 0 AND Stage 1
   - Creates portfolio with full context
   ↓
7. Orchestrator synthesizes all results into final response
```

### Communication Method:

**Type:** Context Enrichment (Prompt Engineering)

**Mechanism:**
- Agent outputs stored in dictionary (in-memory)
- Downstream agents receive outputs in their prompts
- No separate messaging layer needed

**Data Format:**
```python
{
    "agent": "market_analyst",
    "result": {
        "analysis": "string",
        "confidence": 0.85,
        "recommendation": "string"
    },
    "success": True,
    "timestamp": "2025-11-12T10:30:00"
}
```

---

## ✅ Verdict: Should We Change Our Communication Protocol?

### Answer: **NO - Current approach is optimal for our use case**

**Reasons:**
1. ✅ **Rate Limited (10 RPM)** - Can't afford protocol overhead
2. ✅ **Clear Dependencies** - Dependency graph handles this perfectly
3. ✅ **Simple Debugging** - Easy to see what each agent received
4. ✅ **Fast** - No message serialization/deserialization
5. ✅ **Type Safe** - Python typing catches errors
6. ✅ **Gemini Context Window** - 128K tokens, can fit all context in prompt

### When to Reconsider (Future):

**If** any of these become true:
- [ ] More than 50 agents
- [ ] Distributed across multiple servers
- [ ] Agents from different vendors/teams
- [ ] Need async retry/recovery
- [ ] Processing millions of requests/day
- [ ] Multiple agents can do same task (need selection)

**Then** consider:
- Message Queue for distribution
- Blackboard for many parallel agents
- Contract Net for dynamic selection

---

## 🎓 Academic References

**Multi-Agent Communication:**
1. FIPA (Foundation for Intelligent Physical Agents) - ACL Specification
2. Wooldridge, M. (2009) - "An Introduction to MultiAgent Systems"
3. Russell & Norvig - "Artificial Intelligence: A Modern Approach" (Chapter 11)

**Blackboard Systems:**
4. Engelmore & Morgan (1988) - "Blackboard Systems"
5. Hayes-Roth, B. (1985) - "A Blackboard Architecture for Control"

**Contract Net Protocol:**
6. Smith, R. G. (1980) - "The Contract Net Protocol"

**Modern LLM Multi-Agent:**
7. AutoGen (Microsoft Research) - Uses message passing
8. LangGraph - Uses state graphs
9. CrewAI - Uses sequential/parallel orchestration (similar to ours!)

---

## 🚀 Conclusion

**Our current implementation:**
- ✅ Uses **Direct Invocation** with **Dependency-Aware Staging**
- ✅ Enhanced with **Rate Limiting** and **Batched Parallelism**
- ✅ Communication via **Context Enrichment** (prompt engineering)

**This is perfect for:**
- ✅ Financial advisory system (our use case)
- ✅ API rate limits (10 RPM free tier)
- ✅ Clear agent dependencies
- ✅ Single-server deployment
- ✅ 13 specialized agents

**No need for complex protocols like ACL, Blackboard, or Message Queues at our scale.**

**Key insight:** We're not building a distributed AI marketplace—we're building a focused financial advisor with clear workflows. Our approach matches our requirements perfectly! 🎯
