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
    """Analyze financial queries with market context"""
    # INPUTS: What this agent needs to reason
    question = dspy.InputField(desc="user's financial question")  # The main query to analyze
    user_profile = dspy.InputField(desc="student/professional/beginner")  # Adapt response to user level
    market_context = dspy.InputField(desc="current market data and trends")  # Real market conditions

    # OUTPUTS: What this agent produces after reasoning
    analysis = dspy.OutputField(desc="detailed financial analysis")  # Main analysis result
    recommendation = dspy.OutputField(desc="actionable recommendation")  # What user should do
    risk_level = dspy.OutputField(desc="low/medium/high")  # Risk assessment
    confidence = dspy.OutputField(desc="confidence score 0-100")  # How sure the agent is

class ConceptExplanation(dspy.Signature):
    """Explain financial concepts adaptively - Education Agent"""
    # INPUTS for educational reasoning
    concept = dspy.InputField(desc="financial concept to explain")  # e.g., "P/E ratio"
    user_level = dspy.InputField(desc="beginner/intermediate/advanced")  # Determines complexity
    context = dspy.InputField(desc="why user is asking")  # Helps tailor explanation

    # OUTPUTS after educational reasoning
    explanation = dspy.OutputField(desc="clear explanation suited to user level")  # Adapted explanation
    examples = dspy.OutputField(desc="practical examples")  # Real-world examples
    related_concepts = dspy.OutputField(desc="related topics to explore")  # Learning path

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
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            # Preferred: Use Google's Gemini for best performance/cost ratio
            # Set the API key as environment variable for LiteLLM
            os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            
            lm = dspy.LM(
                model="gemini/" + self.config.get("model", "gemini-1.5-flash"),  # LiteLLM format
                temperature=self.config.get("temperature", 0.7),  # 0.7 = balanced creativity
                max_tokens=self.config.get("max_tokens", 1000)   # Response length limit
            )
            logger.info(f"DSPy initialized with Gemini: {self.config.get('model', 'gemini-1.5-flash')}")

        elif os.getenv("OPENAI_API_KEY"):
            # Alternative: OpenAI GPT models
            lm = dspy.LM(
                model="openai/" + self.config.get("model", "gpt-3.5-turbo"),  # LiteLLM format
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000)
            )
            logger.info(f"DSPy initialized with OpenAI: {self.config.get('model', 'gpt-3.5-turbo')}")

        elif os.getenv("ANTHROPIC_API_KEY"):
            # Alternative: Anthropic's Claude
            lm = dspy.LM(
                model="anthropic/" + self.config.get("model", "claude-3-haiku-20240307"),  # LiteLLM format
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000)
            )
            logger.info(f"DSPy initialized with Claude: {self.config.get('model', 'claude-3-haiku-20240307')}")

        else:
            # No API key found - cannot proceed
            raise ValueError("No LLM API key found. Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")

        # Configure DSPy to use the selected language model
        dspy.settings.configure(lm=lm)

    def _init_langchain(self):
        """Initialize LangChain components"""
        import os

        # LLM for LangChain - support multiple providers
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.get("model", "gemini-pro"),
                google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
                temperature=0
            )
            logger.info("LangChain using Gemini")
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

        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

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

    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools that use DSPy for reasoning and real financial tools"""

        # Initialize financial tools
        self.financial_tools = FinancialTools()

        tools = [
            # DSPy-based reasoning tools - using Tool instead of StructuredTool
            Tool(
                name="analyze_financial_query",
                description="Analyze complex financial questions with market context. Input should be a query string.",
                func=self._tool_analyze_query
            ),
            Tool(
                name="explain_concept",
                description="Explain financial concepts adapted to user level. Input should be a concept name.",
                func=self._tool_explain_concept
            ),
            Tool(
                name="assess_risk",
                description="Assess investment risk and psychological factors. Input should be an investment description.",
                func=self._tool_assess_risk
            ),

            # Real market data tools
            Tool(
                name="get_stock_data",
                description="Get real-time stock data including price, volume, PE ratio, etc. Input should be a stock symbol like AAPL or GOOGL.",
                func=lambda symbol: asyncio.run(self.financial_tools.get_real_stock_data(symbol))
            ),
            Tool(
                name="get_historical_prices",
                description="Get historical price data for a stock. Input should be a stock symbol.",
                func=lambda symbol: asyncio.run(
                    self.financial_tools.get_historical_prices(symbol, "1mo")
                )
            ),
            Tool(
                name="calculate_technical_indicators",
                description="Calculate RSI, moving averages, and other technical indicators. Input should be a stock symbol.",
                func=lambda symbol: asyncio.run(
                    self.financial_tools.calculate_technical_indicators(symbol)
                )
            ),

            # Financial calculation tools
            Tool(
                name="calculate_portfolio_metrics",
                description="Calculate portfolio Sharpe ratio, volatility, and other metrics. Input should be JSON with holdings and prices.",
                func=lambda data: asyncio.run(
                    self.financial_tools.calculate_portfolio_metrics(data.get('holdings', []), data.get('prices', {}))
                )
            ),
            Tool(
                name="calculate_position_size",
                description="Calculate optimal position size based on risk management. Input should be account_size.",
                func=lambda account_size: asyncio.run(
                    self.financial_tools.calculate_position_size(
                        account_size, 2, 100, 95  # defaults
                    )
                )
            ),
            Tool(
                name="calculate_compound_interest",
                description="Calculate compound interest and future value. Input should be principal amount.",
                func=lambda principal: asyncio.run(
                    self.financial_tools.calculate_compound_interest(
                        principal, 7, 10  # 7% for 10 years as default
                    )
                )
            ),
            Tool(
                name="calculate_loan_payment",
                description="Calculate loan/mortgage payments. Input should be principal amount.",
                func=lambda principal: asyncio.run(
                    self.financial_tools.calculate_loan_payment(principal, 5, 30)  # 5% for 30 years default
                )
            ),
            Tool(
                name="compare_stocks",
                description="Compare multiple stocks on various metrics. Input should be comma-separated stock symbols like 'AAPL,GOOGL,MSFT'.",
                func=lambda symbols: asyncio.run(
                    self.financial_tools.compare_stocks(symbols.split(',') if isinstance(symbols, str) else symbols)
                )
            )
        ]
        return tools

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the main agent prompt"""
        system_message = """You are FinMentor AI, a sophisticated financial advisor that combines
        deep market knowledge with educational capabilities. You help users understand finance
        and make informed decisions.

        Your approach:
        1. First understand what the user is asking
        2. Use appropriate tools to gather information and analyze
        3. Provide clear, actionable advice suited to their level
        4. Always consider risk and user psychology
        5. Educate while advising

        Current user profile: {user_profile}
        Current datetime: {current_time}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        return prompt

    async def _tool_analyze_query(self, query: str) -> str:
        """Use DSPy to analyze financial queries"""
        try:
            self.metrics["dspy_calls"] += 1

            # Get market context (mock for now, replace with real API)
            market_context = await self._get_market_context()

            # Use DSPy for reasoning
            result = self.dspy_reasoner.forward(
                query_type="analyze",
                question=query,
                user_profile=self.user_profile.get("type", "beginner"),
                market_context=market_context
            )

            # Update confidence metric
            confidence = float(result.confidence)
            self._update_avg_confidence(confidence)

            return f"""
📊 Analysis: {result.analysis}

💡 Recommendation: {result.recommendation}

⚠️ Risk Level: {result.risk_level}

📈 Confidence: {result.confidence}%
"""
        except Exception as e:
            logger.error(f"Error in analyze query: {e}")
            return f"Error analyzing query: {str(e)}"

    async def _tool_explain_concept(self, concept: str) -> str:
        """Use DSPy to explain financial concepts"""
        try:
            self.metrics["dspy_calls"] += 1

            result = self.dspy_reasoner.forward(
                query_type="explain",
                concept=concept,
                user_level=self.user_profile.get("education_level", "beginner"),
                context="User requested explanation"
            )

            return f"""
📚 {concept}

{result.explanation}

💭 Examples:
{result.examples}

🔗 Related Concepts: {result.related_concepts}
"""
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return f"Error explaining concept: {str(e)}"

    async def _tool_assess_risk(self, investment: str) -> str:
        """Use DSPy to assess investment risk"""
        try:
            self.metrics["dspy_calls"] += 1

            market_conditions = await self._get_market_conditions()

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
        rag_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user queries
        Combines Agentic RAG + DSPy reasoning + LangChain orchestration
        Now with Multi-Agent Orchestration for complex queries
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
            from agents.orchestrator import MultiAgentOrchestrator, QueryComplexity
            from services.agentic_rag import QueryIntent

            if rag_context:
                orchestrator = MultiAgentOrchestrator(self)
                intent = QueryIntent[rag_context["intent"].upper()] if "intent" in rag_context else QueryIntent.GENERAL_CHAT
                complexity = orchestrator.assess_complexity(query, intent)

                # Use orchestrator for complex queries
                if complexity >= QueryComplexity.MODERATE:
                    logger.info(f"Using multi-agent orchestration for {complexity.name} query")
                    orchestrated_result = await orchestrator.process_complex_query(
                        query=query,
                        user_profile=user_profile
                    )
                    return orchestrated_result

            # Step 2: Prepare enhanced input with RAG context
            agent_input = {
                "input": query,
                "user_profile": json.dumps(user_profile),
                "current_time": datetime.now().isoformat()
            }

            # Add RAG context if available
            if rag_context and rag_context.get("context"):
                # Format context for the prompt
                context_str = "\n\nRelevant Context:\n"
                for ctx in rag_context["context"][:3]:  # Top 3 most relevant
                    context_str += f"- {ctx.get('content', '')[:200]}...\n"

                agent_input["context"] = context_str
                agent_input["intent"] = rag_context.get("intent", "general")

            # Step 3: Process with LangChain agent (which uses DSPy tools)
            self.metrics["langchain_calls"] += 1
            response = await self.agent_executor.ainvoke(agent_input)

            # Step 4: Self-reflection for critical queries
            final_response = response["output"]
            reflection = None

            if rag_context and rag_context.get("reflection", {}).get("needed"):
                # Perform self-reflection
                reflection = await self.agentic_rag.self_reflect(
                    query=query,
                    response=final_response,
                    context=rag_context.get("context", [])
                )

                # Add disclaimers if needed
                if reflection.get("needs_revision"):
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
            logger.error(f"Error processing query: {e}")
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