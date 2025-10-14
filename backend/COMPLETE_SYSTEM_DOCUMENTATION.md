# Complete FinMentor AI System Documentation

## System Overview
FinMentor AI is a sophisticated multi-agent financial advisory system that combines:
- **DSPy** for structured reasoning
- **LangChain** for tool orchestration
- **Agentic RAG** for intelligent context retrieval
- **PostgreSQL with PGVector** for vector embeddings

---

## 1. ENTRY POINT: `main.py`

```python
# Application starts here when you run: uvicorn main:app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This runs ONCE when the app starts:
    1. Initialize database connection
    2. Create hybrid AI system with config
    3. Create orchestrator for multi-agent coordination
    """

    # These are singleton instances - only created once
    hybrid_system = HybridFinMentorSystem(config)  # Main AI brain
    orchestrator = MultiAgentOrchestrator(hybrid_system)  # Agent coordinator
```

**Flow**: User → FastAPI → Routers → Services → Response

---

## 2. CHAT ROUTER: `routers/chat.py`

```python
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Main endpoint - ALL queries come here
    Handles: text, voice, images, documents
    """

    # Step 1: Process input based on type
    if request.input_type == "voice":
        # Convert voice to text (TODO: implement Whisper)
        processed_message = await process_voice_input(request.voice_data)

    # Step 2: Get AI system instance
    system = get_hybrid_system(db)  # Gets or creates singleton

    # Step 3: Use RAG to understand context
    rag_context = await rag_service.retrieve_and_generate_context(
        query=processed_message,
        user_id=user_id
    )
    # rag_context contains:
    # - intent (what user wants)
    # - relevant past conversations
    # - educational content

    # Step 4: Process through AI system
    result = await system.process_query(
        query=processed_message,
        user_profile=request.user_profile,
        rag_context=rag_context
    )

    # Step 5: Store in database
    # - Save user message with embedding
    # - Save AI response with embedding
    # - These embeddings enable future RAG retrieval
```

**Key Point**: This ONE endpoint handles EVERYTHING - no need for separate market/education/portfolio endpoints!

---

## 3. AGENTIC RAG: `services/agentic_rag.py`

```python
class AgenticRAG:
    """
    Smart retrieval system that UNDERSTANDS queries
    Not just keyword matching - it knows INTENT
    """

    def classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """
        Step 1: What does the user want?

        Example: "What did we discuss about Apple stock last week?"
        → Intent: HISTORICAL_REFERENCE
        → Confidence: 0.9
        """

        # Check patterns in query
        if "last time" or "previously" in query:
            return QueryIntent.HISTORICAL_REFERENCE
        elif "what is" or "explain" in query:
            return QueryIntent.EDUCATIONAL_QUERY
        elif "should I buy" in query:
            return QueryIntent.PORTFOLIO_ADVICE  # CRITICAL - needs verification!

    def plan_retrieval(self, intent: QueryIntent) -> Dict:
        """
        Step 2: Based on intent, decide WHERE to search

        HISTORICAL → Search past conversations
        EDUCATIONAL → Search knowledge base
        PORTFOLIO → Search everything + verify
        """

        if intent == QueryIntent.PORTFOLIO_ADVICE:
            plan["sources"] = ["conversations", "education", "market"]
            plan["needs_verification"] = True  # Double-check advice!

    async def retrieve_from_conversations(self, query_embedding):
        """
        Step 3: Use PGVector for similarity search

        SQL: SELECT * FROM messages
             WHERE embedding <-> query_embedding < threshold
             ORDER BY distance

        This finds semantically similar past conversations
        Not just keyword matching - MEANING matching!
        """
```

**Magic**: RAG understands INTENT, not just keywords!

---

## 4. HYBRID CORE: `agents/hybrid_core.py`

```python
class HybridFinMentorSystem:
    """
    The BRAIN - combines DSPy reasoning + LangChain tools
    """

    def __init__(self):
        # Initialize DSPy (reasoning engine)
        self._init_dspy()  # Sets up Gemini/OpenAI/Claude

        # Create specialized agents
        self.dspy_reasoner = DSPyFinancialReasoner()
        # This contains 13 specialized agents:
        # - technical_analysis
        # - sentiment_analysis
        # - portfolio_optimization
        # - risk_assessment
        # - tax_implications
        # ... and more

        # Initialize LangChain (tool orchestration)
        self._init_langchain()
        # Creates tools that agents can use:
        # - get_stock_data (real Yahoo Finance data)
        # - calculate_portfolio_metrics
        # - calculate_position_size
        # ... and more

    async def process_query(self, query, user_profile, rag_context):
        """
        Main processing pipeline
        """

        # Step 1: Check complexity
        if query_is_complex:
            # Use orchestrator for multi-agent processing
            return await orchestrator.process_complex_query()

        # Step 2: Single agent processing
        # Route to appropriate DSPy signature
        if "risk" in query:
            result = self.dspy_reasoner.assess_risk(...)

        # Step 3: Use tools if needed
        if needs_market_data:
            data = await self.financial_tools.get_real_stock_data("AAPL")
            # Returns REAL data from Yahoo Finance!

        # Step 4: Generate response
        # Combines reasoning + real data
```

---

## 5. DSPy AGENTS: `agents/specialized_signatures.py`

```python
class MarketTechnicalAnalysis(dspy.Signature):
    """
    DSPy signature = structured reasoning template
    Defines inputs → reasoning → outputs
    """

    # INPUTS (what the agent needs)
    symbol = dspy.InputField(desc="stock symbol")
    timeframe = dspy.InputField(desc="1d, 1w, 1m")
    price_data = dspy.InputField(desc="historical prices")

    # OUTPUTS (what the agent produces)
    trend = dspy.OutputField(desc="bullish/bearish/neutral")
    support_levels = dspy.OutputField(desc="key support prices")
    indicators = dspy.OutputField(desc="RSI, MACD analysis")
    recommendation = dspy.OutputField(desc="buy/hold/sell")
    confidence = dspy.OutputField(desc="0-100 score")
```

**Each signature is a specialized expert agent!**

---

## 6. ORCHESTRATOR: `agents/orchestrator.py`

```python
class MultiAgentOrchestrator:
    """
    Coordinates multiple agents for complex queries
    Like a project manager for AI agents
    """

    def assess_complexity(self, query, intent):
        """
        How complex is this query?

        SIMPLE: "What is a P/E ratio?" → 1 agent
        MODERATE: "Compare AAPL and MSFT" → 2-3 agents
        COMPLEX: "Analyze my portfolio" → 5+ agents
        CRITICAL: "Should I sell everything?" → ALL agents + verification
        """

        if intent == QueryIntent.PORTFOLIO_ADVICE:
            if "everything" or "all" in query:
                return QueryComplexity.CRITICAL  # Maximum caution!

    def select_agents(self, query, intent, complexity):
        """
        Pick the right agents for the job

        Portfolio query → Portfolio Manager + Risk Assessor + Tax Advisor
        Market query → Market Analyst + News Analyst
        """

        if complexity == QueryComplexity.CRITICAL:
            # Use ALL relevant agents for critical decisions
            agents = [PORTFOLIO, RISK, TAX, BEHAVIORAL, MARKET]

    async def execute_agents(self, agents, query, context):
        """
        Run agents IN PARALLEL for speed

        Instead of: Agent1 → Agent2 → Agent3 (slow)
        We do: Agent1, Agent2, Agent3 simultaneously (fast!)
        """

        tasks = []
        for agent in agents:
            tasks.append(run_agent_async(agent, query))

        # Wait for all agents to complete
        results = await asyncio.gather(*tasks)

    def synthesize_results(self, results):
        """
        Combine multiple agent outputs into ONE response

        Agent1: "Stock is undervalued"
        Agent2: "High risk due to volatility"
        Agent3: "Tax implications if you sell"

        → Combined: "The stock appears undervalued but carries
                     high risk. Consider tax implications before selling."
        """
```

---

## 7. FINANCIAL TOOLS: `agents/financial_tools.py`

```python
class FinancialTools:
    """
    Real calculations and data fetching
    These are the ACTUAL tools agents use
    """

    async def get_real_stock_data(self, symbol: str):
        """
        Fetches REAL data from Yahoo Finance

        ticker = yf.Ticker("AAPL")
        Returns:
        - current_price: $150.25
        - pe_ratio: 28.5
        - market_cap: $2.5T
        - ... and 20+ more metrics
        """

    async def calculate_portfolio_metrics(self, holdings, prices):
        """
        Professional portfolio analysis

        Calculates:
        - Sharpe Ratio: risk-adjusted returns
        - Volatility: how much prices swing
        - Max Drawdown: worst loss period
        - Beta: correlation with market
        """

        # This is REAL financial math, not placeholder!
        sharpe_ratio = (returns - risk_free_rate) / volatility

    async def calculate_position_size(self, account, risk_percent):
        """
        Risk management calculation

        If account = $10,000 and risk = 2%
        → Maximum risk per trade = $200

        If stop loss is $5 below entry:
        → Buy 40 shares maximum
        """
```

---

## 8. DATABASE: `models/database.py`

```python
class Message(Base):
    """
    Stores all conversations with embeddings
    """

    # Text content
    content = Column(Text)  # The actual message

    # Vector embedding for similarity search
    embedding = Column(Vector(1536))  # 1536-dimensional vector
    # This enables semantic search!
    # "How do I invest?" matches "investment strategies"

    # Multimodal support
    voice_data = Column(Text)  # Base64 audio
    image_data = Column(Text)  # Base64 image
```

---

## COMPLETE FLOW EXAMPLE

### User asks: "Should I buy Apple stock? Consider my risk tolerance and check current prices"

1. **Entry** (`main.py`)
   - Request arrives at FastAPI

2. **Router** (`chat.py`)
   - Receives query
   - Identifies as text input

3. **RAG** (`agentic_rag.py`)
   ```python
   # Classifies intent
   intent = PORTFOLIO_ADVICE  # Critical query!
   confidence = 0.95

   # Retrieves context
   - User's past Apple discussions
   - User's risk profile (moderate)
   - Educational content about Apple
   ```

4. **Orchestrator** (`orchestrator.py`)
   ```python
   # Assesses complexity
   complexity = COMPLEX  # Needs multiple agents

   # Selects agents
   agents = [MARKET_ANALYST, RISK_ASSESSOR, PORTFOLIO_MANAGER]
   ```

5. **Parallel Agent Execution**
   ```python
   # All agents work simultaneously:

   MARKET_ANALYST:
   - Fetches real Apple data: $150.25, PE: 28.5
   - Analyzes trend: Bullish, above 50-day MA

   RISK_ASSESSOR:
   - Evaluates volatility: Moderate (22% annual)
   - Checks user profile: Matches risk tolerance

   PORTFOLIO_MANAGER:
   - Calculates position size: 5% of portfolio
   - Checks diversification: Tech exposure OK
   ```

6. **Tools Used** (`financial_tools.py`)
   ```python
   - get_real_stock_data("AAPL")  # Real Yahoo Finance
   - calculate_position_size(10000, 2, 150, 145)  # Risk management
   - calculate_technical_indicators("AAPL")  # RSI, MA
   ```

7. **Synthesis** (`orchestrator.py`)
   ```python
   # Combines all agent outputs:
   "Based on analysis:
    - Apple trading at $150.25 (PE: 28.5)
    - Technical indicators positive
    - Matches your moderate risk profile
    - Suggested position: 65 shares (5% of portfolio)
    - Set stop loss at $145

    Note: This is educational, not financial advice."
   ```

8. **Storage** (`database.py`)
   - Query stored with embedding
   - Response stored with embedding
   - Available for future RAG retrieval

---

## KEY INSIGHTS

1. **One Endpoint, Many Agents**: `/chat` handles everything through intelligent routing

2. **Parallel Processing**: Multiple agents work simultaneously for speed

3. **Real Data**: Not placeholders - actual Yahoo Finance, real calculations

4. **Smart Context**: RAG understands intent, not just keywords

5. **Safety First**: Critical queries get extra verification

6. **Learning System**: Every conversation improves future responses through embeddings

The system is like having a team of financial experts, each specialized, working together, with perfect memory of all past conversations!