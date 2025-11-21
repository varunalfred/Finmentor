"""
Hybrid DSPy + LangChain Multi-Agent System Core
DSPy for intelligent reasoning, LangChain for orchestration
"""

import dspy
from typing import Dict, Any, List, Optional

# LangChain imports - using latest versions only
from langchain.agents import create_react_agent, create_openai_tools_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
import logging
from datetime import datetime
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import specialized signatures
from agents.specialized_signatures import (
    MarketTechnicalAnalysis, MarketSentimentAnalysis,
    PortfolioOptimization, DividendAnalysis,
    TaxImplications, EarningsAnalysis,
    EconomicIndicatorAnalysis, PersonalizedLearning,
    BehavioralBiasDetection, PsychologicalProfiling
)
from agents.financial_tools import FinancialTools

logger = logging.getLogger(__name__)

# ============= DSPy Signatures for Financial Reasoning =============
# DSPy signatures define structured reasoning templates for agents
# Each signature is like a specialized expert with specific inputs/outputs

class FinancialAnalysis(dspy.Signature):
    """Analyze financial queries with knowledge base priority - Analysis Agent"""
    # INPUTS for financial analysis
    question = dspy.InputField(desc="financial question or scenario")
    user_profile = dspy.InputField(desc="user experience level and preferences")
    market_context = dspy.InputField(desc="current market conditions")
    knowledge_base_context = dspy.InputField(desc="retrieved relevant financial documents and data")
    
    # OUTPUTS after reasoning
    analysis = dspy.OutputField(desc="comprehensive financial analysis combining KB and market data")
    recommendation = dspy.OutputField(desc="actionable recommendation")
    risk_level = dspy.OutputField(desc="low/moderate/high")
    confidence = dspy.OutputField(desc="0-100 confidence score")
    sources_used = dspy.OutputField(desc="sources: 'knowledge_base', 'market_data', 'llm_knowledge', or combination")

class ConceptExplanation(dspy.Signature):
    """Explain financial concepts using knowledge base and additional sources - Education Agent"""
    # INPUTS for educational reasoning
    concept = dspy.InputField(desc="financial concept to explain")  # e.g., "P/E ratio"
    user_level = dspy.InputField(desc="beginner/intermediate/advanced")  # Determines complexity
    knowledge_base_context = dspy.InputField(desc="retrieved documents from financial glossary and knowledge base")  # RAG context
    kb_relevance_score = dspy.InputField(desc="how relevant the KB documents are (0-1)")  # Quality indicator
    
    # OUTPUTS after educational reasoning
    explanation = dspy.OutputField(desc="clear explanation combining KB and LLM knowledge, suited to user level")
    examples = dspy.OutputField(desc="practical examples from KB or generated")
    related_concepts = dspy.OutputField(desc="related topics to explore")
    sources_used = dspy.OutputField(desc="sources: 'knowledge_base', 'llm_knowledge', or 'both'")

class RiskAssessment(dspy.Signature):
    """Assess investment risk and user psychology - Risk Agent"""
    # INPUTS for risk analysis
    investment = dspy.InputField(desc="investment being considered")  # What user wants to buy
    user_profile = dspy.InputField(desc="user's risk tolerance and goals")  # User's risk capacity
    market_conditions = dspy.InputField(desc="current market state")  # Bull/bear market, volatility

    # OUTPUTS from risk reasoning
    risk_score = dspy.OutputField(desc="numerical risk score 1-10")  # Quantified risk level
    risk_factors = dspy.OutputField(desc="key risk factors identified")  # Specific risks found
    mitigation = dspy.OutputField(desc="risk mitigation strategies")  # How to reduce risk
    psychological_bias = dspy.OutputField(desc="detected behavioral biases")  # FOMO, loss aversion, etc.

# ============= DSPy Modules =============

class DSPyFinancialReasoner(dspy.Module):
    """Enhanced DSPy module with all specialized agent capabilities"""

    def __init__(self):
        super().__init__()
        # ChainOfThought makes agents show their reasoning step-by-step
        # This improves accuracy and explainability

        # Original core agents - these handle basic queries
        self.analyze = dspy.ChainOfThought(FinancialAnalysis)  # General financial analysis
        self.explain = dspy.ChainOfThought(ConceptExplanation)  # Educational explanations
        self.assess_risk = dspy.ChainOfThought(RiskAssessment)  # Risk evaluation

        # Market Analysis Agents - analyze market conditions and trends
        self.technical_analysis = dspy.ChainOfThought(MarketTechnicalAnalysis)  # Charts, indicators
        self.sentiment_analysis = dspy.ChainOfThought(MarketSentimentAnalysis)  # News sentiment

        # Portfolio Management Agents - optimize and manage investments
        self.optimize_portfolio = dspy.ChainOfThought(PortfolioOptimization)  # Asset allocation
        self.analyze_dividends = dspy.ChainOfThought(DividendAnalysis)  # Income strategies

        # Specialized Agents - specific domain expertise
        self.tax_implications = dspy.ChainOfThought(TaxImplications)  # Tax consequences
        self.earnings_analysis = dspy.ChainOfThought(EarningsAnalysis)  # Company earnings
        self.economic_analysis = dspy.ChainOfThought(EconomicIndicatorAnalysis)  # Macro analysis

        # Education & Behavioral Agents - understand and educate users
        self.personalized_learning = dspy.ChainOfThought(PersonalizedLearning)  # Custom learning paths
        self.detect_bias = dspy.ChainOfThought(BehavioralBiasDetection)  # Spot emotional decisions
        self.profile_psychology = dspy.ChainOfThought(PsychologicalProfiling)  # Understand investor type

    def forward(self, query_type: str, **kwargs):
        """Route to appropriate specialized agent based on query type"""
        # Map query types to their corresponding specialized agents
        # This is like a switchboard directing calls to the right expert
        agents_map = {
            "analyze": self.analyze,           # General financial questions
            "explain": self.explain,           # "What is...?" questions
            "risk": self.assess_risk,          # "Is this risky?" questions
            "technical": self.technical_analysis,  # Chart/indicator analysis
            "sentiment": self.sentiment_analysis,  # News/social sentiment
            "optimize": self.optimize_portfolio,   # Portfolio optimization
            "dividends": self.analyze_dividends,   # Income investing
            "tax": self.tax_implications,          # Tax consequences
            "earnings": self.earnings_analysis,    # Company earnings
            "economic": self.economic_analysis,    # Economic indicators
            "learning": self.personalized_learning,  # Educational paths
            "bias": self.detect_bias,              # Behavioral biases
            "psychology": self.profile_psychology  # Investor profiling
        }

        # Get the right agent for this query type
        agent = agents_map.get(query_type)
        if agent:
            # Execute the agent with provided arguments
            return agent(**kwargs)  # **kwargs unpacks the arguments
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    async def parallel_analysis(self, analyses: List[tuple]):
        """Run multiple agents in parallel for comprehensive analysis"""
        # Create a list to hold all async tasks
        tasks = []

        # For each analysis request, create an async task
        for query_type, kwargs in analyses:
            # asyncio.to_thread runs the synchronous DSPy forward() in a thread
            # This prevents blocking while maintaining parallelism
            tasks.append(asyncio.create_task(
                asyncio.to_thread(self.forward, query_type, **kwargs)
            ))

        # Wait for ALL agents to complete and collect results
        # This is the magic - all agents work simultaneously!
        results = await asyncio.gather(*tasks)
        return results

# ============= Hybrid System =============

class HybridFinMentorSystem:
    """
    The BRAIN of FinMentor AI - Combines multiple AI paradigms:
    DSPy: Handles complex reasoning and learning (the thinking)
    LangChain: Manages tools, memory, and workflow (the doing)
    Agentic RAG: Intelligent context retrieval (the remembering)
    """

    def __init__(self, config: Dict[str, Any], db_session=None):
        # Configuration for the system (model, temperature, etc.)
        self.config = config
        # Will store current user's profile for personalization
        self.user_profile = None
        # Database session for storing/retrieving data
        self.db_session = db_session

        # Step 1: Initialize DSPy with language model (Gemini/OpenAI/Claude)
        self._init_dspy()  # Sets up the reasoning engine

        # Step 2: Create the multi-agent reasoner with 13 specialized agents
        self.dspy_reasoner = DSPyFinancialReasoner()

        # Step 3: Initialize LangChain for tool management and orchestration
        self._init_langchain()  # Sets up tools and memory

        # Step 4: Connect to Agentic RAG singleton for smart retrieval
        from services.agentic_rag import rag_service
        self.agentic_rag = rag_service  # Singleton instance
        if db_session:
            self.agentic_rag.set_db_session(db_session)

        # Track performance metrics for monitoring and optimization
        self.metrics = {
            "total_queries": 0,      # Total queries processed
            "dspy_calls": 0,         # Times DSPy reasoning used
            "langchain_calls": 0,    # Times LangChain tools used
            "rag_calls": 0,          # Times RAG retrieval used
            "avg_confidence": 0      # Average confidence of responses
        }

    def _init_dspy(self):
        """Initialize DSPy configuration - supports multiple LLM providers"""
        import os

        # DSPy uses LiteLLM under the hood, so we use "provider/model" format
        # Check environment variables to determine which LLM to use
        # Priority order: Gemini > OpenAI > Claude
        if os.getenv("GEMINI_API_KEY"):
            # Preferred: Use Google's Gemini for best performance/cost ratio
            # Set the API key as environment variable for LiteLLM
            os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
            
            # Configure LiteLLM retry behavior with exponential backoff
            # This prevents "retry storms" that worsen rate limiting
            os.environ["LITELLM_NUM_RETRIES"] = "3"  # Max 3 retries
            os.environ["LITELLM_RETRY_DELAY"] = "2"  # Start with 2s delay (exponential: 2s, 4s, 8s)
            
            lm = dspy.LM(
                model="gemini/" + self.config.get("model", "gemini-2.5-flash"),  # LiteLLM format
                temperature=self.config.get("temperature", 0.7),  # 0.7 = balanced creativity
                max_tokens=self.config.get("max_tokens", 2500),   # Optimal for detailed responses (researched value)
                # Retry configuration for handling 503 errors (overloaded servers)
                num_retries=3,  # Retry up to 3 times with exponential backoff
                api_base=None  # Use default Gemini endpoint
            )
            logger.info(f"DSPy initialized with Gemini: {self.config.get('model', 'gemini-2.5-flash')} (3 retries with exponential backoff: 2s, 4s, 8s)")

        elif os.getenv("OPENAI_API_KEY"):
            # Alternative: OpenAI GPT models
            lm = dspy.LM(
                model="openai/" + self.config.get("model", "gpt-3.5-turbo"),  # LiteLLM format
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2500)  # Optimal for detailed responses
            )
            logger.info(f"DSPy initialized with OpenAI: {self.config.get('model', 'gpt-3.5-turbo')}")

        elif os.getenv("ANTHROPIC_API_KEY"):
            # Alternative: Anthropic Claude
            lm = dspy.LM(
                model="anthropic/" + self.config.get("model", "claude-3-haiku-20240307"),  # LiteLLM format
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2500)  # Optimal for detailed responses
            )
            logger.info(f"DSPy initialized with Claude: {self.config.get('model', 'claude-3-haiku-20240307')}")

        else:
            # No API key found - cannot proceed
            raise ValueError("No LLM API key found. Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")

        # Store LM instance instead of using global configure to avoid async issues
        # Each instance maintains its own DSPy context
        self.lm = lm

    def _init_langchain(self):
        """Initialize LangChain components"""
        import os

        # LLM for LangChain - support multiple providers
        if os.getenv("GEMINI_API_KEY"):
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.get("model", "gemini-2.5-flash"),
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0,
                max_retries=3  # Retry up to 3 times for 503 errors
            )
            logger.info(f"LangChain using Gemini: {self.config.get('model', 'gemini-2.5-flash')} (3 retries enabled)")
        elif os.getenv("OPENAI_API_KEY"):
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=self.config.get("model", "gpt-3.5-turbo"),
                temperature=0
            )
            logger.info("LangChain using OpenAI")
        elif os.getenv("ANTHROPIC_API_KEY"):
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model=self.config.get("model", "claude-3-haiku-20240307"),
                temperature=0
            )
            logger.info("LangChain using Claude")
        else:
            raise ValueError("No LLM API key found")

        # Memory for conversation
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Keep last 10 exchanges
        )

        # Create tools that leverage DSPy
        self.tools = self._create_tools()

        # Create agent prompt
        prompt = self._create_prompt()

        # DEBUG: Log before creating agent
        print("\n" + "="*70)
        print(f"DEBUG: Creating agent with {len(self.tools)} tools")
        print(f"DEBUG: LLM: {self.llm.__class__.__name__}")
        print(f"DEBUG: Model: {self.config.get('model', 'unknown')}")
        print("DEBUG: Tool names being passed to LangChain:")
        for i, tool in enumerate(self.tools):
            print(f"  {i+1}. '{tool.name}'")
        print("="*70 + "\n")
        
        logger.info(f"Creating agent with {len(self.tools)} tools and LLM: {self.llm.__class__.__name__}")
        logger.info(f"LLM model: {self.config.get('model', 'unknown')}")
        
        # EXPERIMENTAL: Try binding tools directly to Gemini LLM
        # The issue is that create_openai_tools_agent uses OpenAI format
        # which may not be compatible with Gemini's function calling API
        print("DEBUG: Attempting to bind tools to LLM using bind_tools()...")
        try:
            # Bind tools to the LLM - this is Gemini-compatible
            self.llm_with_tools = self.llm.bind_tools(self.tools)
            print("DEBUG: Tools bound successfully to LLM")
        except Exception as e:
            print(f"DEBUG: WARNING - Could not bind tools: {e}")
            print("DEBUG: Falling back to agent without tool binding")
            self.llm_with_tools = self.llm
        
        # Create agent - Try ReAct agent instead of OpenAI tools agent
        # ReAct uses a different format that may be more compatible with Gemini
        from langchain.agents import create_react_agent
        try:
            print("DEBUG: Trying ReAct agent (more compatible with Gemini)...")
            # ReAct agent uses a simpler format
            self.agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            print("DEBUG: ReAct agent created successfully\n")
            logger.info("ReAct agent created successfully")
        except Exception as e:
            print(f"DEBUG: ReAct agent failed, trying OpenAI tools agent: {e}")
            # Fallback to OpenAI tools agent
            try:
                self.agent = create_openai_tools_agent(
                    llm=self.llm,
                    tools=self.tools,
                    prompt=prompt
                )
                print("DEBUG: OpenAI tools agent created successfully\n")
                logger.info("OpenAI tools agent created successfully")
            except Exception as e2:
                print(f"DEBUG: Failed to create any agent: {e2}\n")
                logger.error(f"Failed to create agent: {e2}")
                raise

        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.config.get("verbose", False),
            max_iterations=5,
            handle_parsing_errors=True
        )

        logger.info("LangChain components initialized successfully")

    def _run_async_in_thread(self, coro):
        """
        Run async function in a separate thread with its own event loop.
        This isolates the async operation from the main event loop to avoid conflicts.
        """
        def run_in_new_loop():
            # Create a completely new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(coro)
                return result
            except Exception as e:
                logger.error(f"Error in async thread: {e}")
                return f"Error: {str(e)}"
            finally:
                # Clean up
                try:
                    # Cancel any pending tasks
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    # Run loop one last time to process cancellations
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
        
        # Run in thread pool to completely isolate from current event loop
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_in_new_loop)
            return future.result(timeout=60)  # 60 second timeout

    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools that use DSPy for reasoning and real financial tools"""

        # Initialize financial tools
        self.financial_tools = FinancialTools()

        logger.info("Creating LangChain tools...")
        
        tools = [
            # DSPy-based reasoning tools - wrap async functions to make them synchronous for LangChain
            Tool(
                name="analyze_financial_query",
                description="Analyze complex financial questions with market context. Input should be a query string.",
                func=lambda q: self._run_async_in_thread(self._tool_analyze_query(q))
            ),
            Tool(
                name="explain_concept",
                description="Explain financial concepts adapted to user level. Input should be a concept name.",
                func=lambda c: self._run_async_in_thread(self._tool_explain_concept(c))
            ),
            Tool(
                name="assess_risk",
                description="Assess investment risk and psychological factors. Input should be an investment description.",
                func=lambda i: self._run_async_in_thread(self._tool_assess_risk(i))
            ),

            # Real market data tools
            Tool(
                name="get_stock_data",
                description="Get real-time stock data including price, volume, PE ratio, etc. Input should be a stock symbol like AAPL or GOOGL.",
                func=lambda symbol: self._run_async_in_thread(self.financial_tools.get_real_stock_data(symbol))
            ),
            Tool(
                name="get_historical_prices",
                description="Get historical price data for a stock. Input should be a stock symbol.",
                func=lambda symbol: self._run_async_in_thread(
                    self.financial_tools.get_historical_prices(symbol, "1mo")
                )
            ),
            Tool(
                name="calculate_technical_indicators",
                description="Calculate RSI, moving averages, and other technical indicators. Input should be a stock symbol.",
                func=lambda symbol: self._run_async_in_thread(
                    self.financial_tools.calculate_technical_indicators(symbol)
                )
            ),

            # Financial calculation tools
            Tool(
                name="calculate_portfolio_metrics",
                description="Calculate portfolio Sharpe ratio, volatility, and other metrics. Input should be JSON with holdings and prices.",
                func=lambda data: self._run_async_in_thread(
                    self.financial_tools.calculate_portfolio_metrics(data.get('holdings', []), data.get('prices', {}))
                )
            ),
            Tool(
                name="calculate_position_size",
                description="Calculate optimal position size based on risk management. Input should be account_size.",
                func=lambda account_size: self._run_async_in_thread(
                    self.financial_tools.calculate_position_size(
                        account_size, 2, 100, 95  # defaults
                    )
                )
            ),
            Tool(
                name="calculate_compound_interest",
                description="Calculate compound interest and future value. Input should be principal amount.",
                func=lambda principal: self._run_async_in_thread(
                    self.financial_tools.calculate_compound_interest(
                        principal, 7, 10  # 7% for 10 years as default
                    )
                )
            ),
            Tool(
                name="calculate_loan_payment",
                description="Calculate loan/mortgage payments. Input should be principal amount.",
                func=lambda principal: self._run_async_in_thread(
                    self.financial_tools.calculate_loan_payment(principal, 5, 30)  # 5% for 30 years default
                )
            ),
            Tool(
                name="compare_stocks",
                description="Compare multiple stocks on various metrics. Input should be comma-separated stock symbols like 'AAPL,GOOGL,MSFT'.",
                func=lambda symbols: self._run_async_in_thread(
                    self.financial_tools.compare_stocks(symbols.split(',') if isinstance(symbols, str) else symbols)
                )
            )
        ]
        
        # DEBUG: Log all tool names and validate them
        logger.info(f"Created {len(tools)} tools:")
        for i, tool in enumerate(tools):
            tool_name = tool.name if hasattr(tool, 'name') else 'unknown'
            logger.info(f"  Tool {i+1}: '{tool_name}'")
            
            # Validate tool name
            if tool_name:
                is_valid = (
                    tool_name[0].isalpha() or tool_name[0] == '_'
                ) and all(c.isalnum() or c in '_.:-' for c in tool_name) and len(tool_name) <= 64
                
                if not is_valid:
                    logger.error(f"  ❌ INVALID tool name: '{tool_name}' - Does not meet Gemini requirements")
                else:
                    logger.info(f"  ✓ Valid tool name")
        
        return tools

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the main agent prompt - ReAct format"""
        from langchain.prompts import PromptTemplate
        
        # ReAct agent needs a template with {tools}, {tool_names}, {agent_scratchpad}, and {input}
        template = """You are FinMentor AI, a sophisticated financial advisor that combines
deep market knowledge with educational capabilities. You help users understand finance
and make informed decisions.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        return prompt

    async def _tool_analyze_query(self, query: str) -> str:
        """
        RAG-First Financial Analysis Tool:
        1. Query knowledge base for relevant financial information
        2. Get current market context
        3. Combine KB + market data + LLM reasoning
        4. Cite sources used
        """
        try:
            self.metrics["dspy_calls"] += 1
            kb_context = ""
            sources = []

            # STEP 1: Retrieve from knowledge base
            if self.agentic_rag and self.user_profile.get("user_id"):
                try:
                    logger.info(f"Querying knowledge base for analysis: {query}")
                    
                    # Create a new DB session for this event loop (in case we're in a different thread)
                    from services.database import db_service
                    async with db_service.AsyncSessionLocal() as new_session:
                        # Temporarily set the new session
                        old_session = self.agentic_rag.db
                        self.agentic_rag.set_db_session(new_session)
                        
                        try:
                            rag_result = await self.agentic_rag.retrieve_and_generate_context(
                                query=query,
                                user_id=self.user_profile.get("user_id"),
                                user_context=self.user_profile
                            )
                        finally:
                            # Restore original session
                            self.agentic_rag.db = old_session
                    
                    retrieved_docs = rag_result.get("context", [])
                    if retrieved_docs:
                        kb_context = "\n\n".join([
                            f"[KB Document {i+1}] {doc}" 
                            for i, doc in enumerate(retrieved_docs[:5])
                        ])
                        sources.append("Knowledge Base")
                        logger.info(f"Retrieved {len(retrieved_docs)} documents from KB")
                    else:
                        kb_context = "No relevant documents found in knowledge base."
                except Exception as e:
                    logger.error(f"Error retrieving from knowledge base: {e}")
                    kb_context = "Knowledge base unavailable."
            else:
                kb_context = "Knowledge base not configured."

            # STEP 2: Get market context
            market_context = await self._get_market_context()
            if market_context:
                sources.append("Market Data")

            # STEP 3: Use DSPy for reasoning with all available context
            # Use context manager to avoid async configuration issues
            with dspy.context(lm=self.lm):
                result = self.dspy_reasoner(
                    query_type="analyze",
                    question=query,
                    user_profile=self.user_profile.get("type", "beginner"),
                    market_context=market_context,
                    knowledge_base_context=kb_context
                )

            # Track sources
            if result.sources_used:
                if "llm" in result.sources_used.lower():
                    sources.append("LLM Analysis")
            source_text = " + ".join(sources) if sources else "LLM Analysis"

            # Update confidence metric
            confidence = float(result.confidence)
            self._update_avg_confidence(confidence)

            response = f"""
📊 Analysis: {result.analysis}

💡 Recommendation: {result.recommendation}

⚠️ Risk Level: {result.risk_level}

📈 Confidence: {result.confidence}%

📖 Sources: {source_text}
"""
            
            logger.info(f"Financial analysis completed using: {source_text}")
            return response

        except Exception as e:
            logger.error(f"Error in analyze query: {e}")
            return f"Error analyzing query: {str(e)}"

    async def _tool_explain_concept(self, concept: str) -> str:
        """
        RAG-First Educational Tool:
        1. Query knowledge base first (highest priority)
        2. Fall back to LLM knowledge if KB insufficient
        3. Combine and cite sources
        """
        try:
            self.metrics["dspy_calls"] += 1
            kb_context = ""
            kb_relevance = 0.0
            sources = []

            # STEP 1: Retrieve from knowledge base (PRIMARY SOURCE)
            if self.agentic_rag and self.user_profile.get("user_id"):
                try:
                    logger.info(f"Querying knowledge base for concept: {concept}")
                    
                    # Create a new DB session for this event loop (in case we're in a different thread)
                    from services.database import db_service
                    async with db_service.AsyncSessionLocal() as new_session:
                        # Temporarily set the new session
                        old_session = self.agentic_rag.db
                        self.agentic_rag.set_db_session(new_session)
                        
                        try:
                            rag_result = await self.agentic_rag.retrieve_and_generate_context(
                                query=concept,
                                user_id=self.user_profile.get("user_id"),
                                user_context=self.user_profile
                            )
                        finally:
                            # Restore original session
                            self.agentic_rag.db = old_session
                    
                    retrieved_docs = rag_result.get("context", [])
                    if retrieved_docs:
                        # Format retrieved documents
                        kb_context = "\n\n".join([
                            f"[KB Document {i+1}] {doc}" 
                            for i, doc in enumerate(retrieved_docs[:5])  # Top 5 docs
                        ])
                        # Calculate relevance based on number and quality of docs
                        kb_relevance = min(len(retrieved_docs) / 3.0, 1.0)  # 3+ docs = high relevance
                        sources.append("Knowledge Base")
                        logger.info(f"Retrieved {len(retrieved_docs)} documents from KB (relevance: {kb_relevance:.2f})")
                    else:
                        logger.info("No documents found in knowledge base")
                        kb_context = "No relevant documents found in knowledge base."
                except Exception as e:
                    logger.error(f"Error retrieving from knowledge base: {e}")
                    kb_context = "Knowledge base unavailable."
                    kb_relevance = 0.0
            else:
                kb_context = "Knowledge base not configured."
                kb_relevance = 0.0
            
            # STEP 2: Use DSPy with KB context (will use LLM knowledge if KB insufficient)
            # Note: Using __call__() instead of .forward() as recommended by DSPy
            # Use context manager to avoid async configuration issues
            with dspy.context(lm=self.lm):
                result = self.dspy_reasoner(
                    query_type="explain",
                    concept=concept,
                    user_level=self.user_profile.get("education_level", "beginner"),
                    knowledge_base_context=kb_context,
                    kb_relevance_score=str(kb_relevance)
                )

            # Track which sources were used
            if result.sources_used:
                if "llm" in result.sources_used.lower():
                    sources.append("LLM Knowledge")
                source_text = " + ".join(sources) if sources else "LLM Knowledge"
            else:
                source_text = "Knowledge Base" if kb_relevance > 0.3 else "LLM Knowledge"

            # STEP 3: Format response with source attribution
            response = f"""
📚 {concept}

{result.explanation}

💭 Examples:
{result.examples}

🔗 Related Concepts: {result.related_concepts}

📖 Sources: {source_text}
"""
            
            logger.info(f"Concept explanation completed using: {source_text}")
            return response

        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return f"Error explaining concept: {str(e)}"

    async def _tool_assess_risk(self, investment: str) -> str:
        """Use DSPy to assess investment risk"""
        try:
            self.metrics["dspy_calls"] += 1

            market_conditions = await self._get_market_conditions()

            # Use DSPy context manager to avoid async configuration issues
            with dspy.context(lm=self.lm):
                result = self.dspy_reasoner.forward(
                    query_type="risk",
                    investment=investment,
                    user_profile=json.dumps(self.user_profile),
                    market_conditions=market_conditions
                )

            return f"""
⚠️ Risk Assessment for {investment}

Risk Score: {result.risk_score}/10

🔴 Risk Factors:
{result.risk_factors}

🛡️ Mitigation Strategies:
{result.mitigation}

🧠 Behavioral Note:
{result.psychological_bias}
"""
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return f"Error assessing risk: {str(e)}"

    async def _tool_fetch_market_data(self, symbol: str) -> str:
        """Fetch real market data using financial tools"""
        data = await self.financial_tools.get_real_stock_data(symbol)
        if "error" in data:
            return f"Error: {data['error']}"

        return f"""
Stock: {data.get('name', symbol)} ({data.get('symbol')})
Price: ${data.get('current_price', 'N/A')}
Change: {data.get('change_percent', 'N/A')}
Volume: {data.get('volume', 'N/A'):,}
PE Ratio: {data.get('pe_ratio', 'N/A')}
Market Cap: ${data.get('market_cap', 0):,.0f}
52W Range: ${data.get('52_week_low', 'N/A')} - ${data.get('52_week_high', 'N/A')}
"""

    async def _tool_calculate_returns(self, params: str) -> str:
        """Calculate real investment returns"""
        try:
            # Parse params (expecting format: "principal:10000,rate:7,years:10")
            param_dict = dict(item.split(':') for item in params.split(','))
            principal = float(param_dict.get('principal', 10000))
            rate = float(param_dict.get('rate', 7))
            years = float(param_dict.get('years', 10))

            result = await self.financial_tools.calculate_compound_interest(
                principal, rate, years
            )

            return f"""
Investment Returns:
- Future Value: ${result['future_value']:,.2f}
- Total Interest: ${result['total_interest']:,.2f}
- Effective Annual Rate: {result['effective_annual_rate']}
- Years: {result['years']}
"""
        except Exception as e:
            return f"Error calculating returns: {str(e)}"

    async def _get_market_context(self) -> str:
        """Get current market context"""
        # Implement real market data fetching
        return "S&P500: +15% YTD, VIX: 18, Fed Rate: 5.5%"

    async def _get_market_conditions(self) -> str:
        """Get current market conditions"""
        return "Bull market, low volatility, rising interest rates"

    def _update_avg_confidence(self, confidence: float):
        """Update average confidence metric"""
        n = self.metrics["dspy_calls"]
        self.metrics["avg_confidence"] = (
            (self.metrics["avg_confidence"] * (n - 1) + confidence) / n
        )

    async def process_query(
        self,
        query: str,
        user_profile: Dict[str, Any],
        voice_input: bool = False,
        rag_context: Optional[Dict] = None,
        skip_orchestration: bool = False  # NEW: Prevent infinite recursion
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user queries
        Combines Agentic RAG + DSPy reasoning + LangChain orchestration
        Now with Multi-Agent Orchestration for complex queries
        
        Args:
            query: User's question
            user_profile: User information
            voice_input: Whether input is from voice
            rag_context: Pre-fetched RAG context (optional)
            skip_orchestration: If True, bypass multi-agent orchestration (prevents recursion)
        """
        start_time = datetime.now()
        self.user_profile = user_profile
        self.metrics["total_queries"] += 1

        try:
            # Step 1: Use Agentic RAG if not provided
            if not rag_context and self.agentic_rag and user_profile.get("user_id"):
                self.metrics["rag_calls"] += 1
                rag_context = await self.agentic_rag.retrieve_and_generate_context(
                    query=query,
                    user_id=user_profile["user_id"],
                    user_context=user_profile
                )
                logger.info(f"RAG retrieved {len(rag_context.get('context', []))} documents")

            # Check if this is a complex query requiring multi-agent orchestration
            # IMPORTANT: Only orchestrate if NOT already inside an orchestrator (prevents infinite recursion)
            from agents.smart_orchestrator import SmartMultiAgentOrchestrator, QueryComplexity
            from services.agentic_rag import QueryIntent

            if rag_context and not skip_orchestration:
                orchestrator = SmartMultiAgentOrchestrator(
                    hybrid_system=self,
                    rpm_limit=10,  # Gemini free tier
                    max_concurrent=2  # Safe batching
                )
                intent = QueryIntent[rag_context["intent"].upper()] if "intent" in rag_context else QueryIntent.GENERAL_CHAT
                complexity = orchestrator.assess_complexity(query, intent)

                # Use orchestrator for complex queries (compare enum values, not enums themselves)
                if complexity.value >= QueryComplexity.MODERATE.value:
                    logger.info(f"Using multi-agent orchestration for {complexity.name} query")
                    orchestrated_result = await orchestrator.process_complex_query(
                        query=query,
                        user_profile=user_profile
                    )
                    return orchestrated_result

            # Step 2: Prepare enhanced input with RAG context
            # ReAct agent only accepts 'input' key, so we merge all context into it
            enriched_query = query
            
            # Add RAG context if available
            if rag_context and rag_context.get("context"):
                # Format context for the prompt
                context_str = "\n\nRelevant Context from Knowledge Base:\n"
                for ctx in rag_context["context"][:3]:  # Top 3 most relevant
                    context_str += f"- {ctx.get('content', '')[:200]}...\n"
                enriched_query = context_str + "\n\nUser Query: " + query
            
            # Add user profile context
            user_level = user_profile.get("education_level", "beginner")
            enriched_query = f"[User Level: {user_level}]\n\n{enriched_query}"
            
            agent_input = {
                "input": enriched_query
            }

            # Step 3: Process with LangChain agent (which uses DSPy tools)
            self.metrics["langchain_calls"] += 1
            logger.info(f"Invoking LangChain agent with query: '{query[:50]}...'")
            logger.info(f"Agent input keys: {list(agent_input.keys())}")
            
            try:
                response = await self.agent_executor.ainvoke(agent_input)
                logger.info("✓ Agent executor completed successfully")
                logger.info(f"Response keys: {list(response.keys()) if response else 'None'}")
            except Exception as e:
                logger.error(f"❌ Agent executor failed: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                raise

            # Step 4: Self-reflection for critical queries
            if not response:
                raise ValueError("Agent executor returned None")
            
            final_response = response.get("output", "")
            if not final_response:
                logger.warning(f"No output in response. Response keys: {list(response.keys())}")
                final_response = str(response)
            
            reflection = None

            # Only do reflection if we have rag_context and it has reflection data
            if rag_context and isinstance(rag_context, dict):
                reflection_data = rag_context.get("reflection")
                if reflection_data and isinstance(reflection_data, dict) and reflection_data.get("needed"):
                    # Perform self-reflection
                    reflection = await self.agentic_rag.self_reflect(
                        query=query,
                        response=final_response,
                        context=rag_context.get("context", [])
                    )

                    # Add disclaimers if needed
                    if reflection and isinstance(reflection, dict) and reflection.get("needs_revision"):
                        if "disclaimer" in str(reflection.get("suggestions", [])):
                            final_response += "\n\n⚠️ Disclaimer: This is not personalized financial advice. Please consult with a qualified financial advisor."
                        if "risk" in str(reflection.get("suggestions", [])):
                            final_response += "\n\n⚠️ Risk Warning: All investments carry risk. Past performance does not guarantee future results."

            # Step 5: Store message with embedding for future retrieval
            if self.agentic_rag and user_profile.get("user_id"):
                # This would typically be done after saving the message to DB
                # For now, we'll just note it should be done
                pass

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "response": final_response,
                "rag_context": {
                    "intent": rag_context.get("intent") if rag_context else None,
                    "sources_used": rag_context.get("retrieval_plan", {}).get("sources", []) if rag_context else [],
                    "documents_retrieved": len(rag_context.get("context", [])) if rag_context else 0
                },
                "reflection": reflection,
                "metadata": {
                    "processing_time": processing_time,
                    "voice_input": voice_input,
                    "confidence": self.metrics["avg_confidence"],
                    "tools_used": [tool.name for tool in self.tools],
                    "user_level": user_profile.get("education_level", "unknown")
                },
                "metrics": self.metrics
            }

        except Exception as e:
            import traceback
            logger.error(f"Error processing query: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again."
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            **self.metrics,
            "dspy_efficiency": (
                self.metrics["dspy_calls"] / max(self.metrics["total_queries"], 1)
            ),
            "system_status": "operational"
        }

    async def train_on_examples(self, examples: List[dspy.Example]):
        """Train DSPy modules with financial examples"""
        from dspy.teleprompt import BootstrapFewShot

        # Configure optimizer
        optimizer = BootstrapFewShot(
            max_bootstrapped_demos=4,
            max_labeled_demos=4
        )

        # Compile optimized module
        self.dspy_reasoner = optimizer.compile(
            self.dspy_reasoner,
            trainset=examples
        )

        logger.info(f"Trained DSPy module with {len(examples)} examples")
        return True