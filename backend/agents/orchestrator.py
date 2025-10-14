"""
Multi-Agent Orchestrator
Manages agent selection, parallel execution, and result synthesis
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime
import json

from agents.hybrid_core import HybridFinMentorSystem
from services.agentic_rag import rag_service, QueryIntent
from services.data_sources import DataSourcesManager

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of specialized agents - each represents a domain expert"""
    MARKET_ANALYST = "market_analyst"      # Technical analysis, price trends
    PORTFOLIO_MANAGER = "portfolio_manager"  # Asset allocation, optimization
    RISK_ASSESSOR = "risk_assessor"        # Risk evaluation, mitigation
    TAX_ADVISOR = "tax_advisor"            # Tax implications, strategies
    EDUCATION = "education"                # Concept explanation, learning
    NEWS_ANALYST = "news_analyst"          # News sentiment, market impact
    BEHAVIORAL = "behavioral"              # Psychology, bias detection

class QueryComplexity(Enum):
    """Query complexity levels - determines how many agents to use"""
    SIMPLE = 1      # Single agent can handle (e.g., "What is P/E ratio?")
    MODERATE = 2    # 2-3 agents needed (e.g., "Compare AAPL and MSFT")
    COMPLEX = 3     # Multiple agents with synthesis (e.g., "Analyze my portfolio")
    CRITICAL = 4    # All relevant agents + verification (e.g., "Should I sell everything?")

class MultiAgentOrchestrator:
    """
    The CONDUCTOR of the multi-agent system
    Like a project manager, it decides:
    - Which agents to use
    - How to coordinate them
    - How to combine their outputs
    """

    def __init__(self, hybrid_system: HybridFinMentorSystem):
        # Reference to the main hybrid system with all agents
        self.hybrid_system = hybrid_system
        # Data manager for fetching market data, news, etc.
        self.data_manager = DataSourcesManager()

        # Maps each agent type to its DSPy signature capabilities
        # This tells us what each agent can do
        self.agent_capabilities = {
            AgentType.MARKET_ANALYST: ["technical", "sentiment", "earnings"],  # Market analysis tools
            AgentType.PORTFOLIO_MANAGER: ["optimize", "dividends"],  # Portfolio management
            AgentType.RISK_ASSESSOR: ["risk", "bias"],  # Risk and behavioral assessment
            AgentType.TAX_ADVISOR: ["tax"],  # Tax implications
            AgentType.EDUCATION: ["explain", "learning"],  # Educational content
            AgentType.NEWS_ANALYST: ["sentiment", "economic"],  # News and economic analysis
            AgentType.BEHAVIORAL: ["bias", "psychology"]  # Behavioral finance
        }

    def assess_complexity(self, query: str, intent: QueryIntent) -> QueryComplexity:
        """Assess query complexity to determine how many agents we need"""
        # Keywords that suggest we need comprehensive analysis
        complex_keywords = ["portfolio", "comprehensive", "analyze everything", "full assessment"]
        # Keywords that suggest comparison or multiple aspects
        moderate_keywords = ["compare", "and", "versus", "or"]

        query_lower = query.lower()  # Case-insensitive matching

        # Portfolio and risk questions are always treated seriously
        # These can affect user's money, so we use multiple agents for verification
        if intent in [QueryIntent.PORTFOLIO_ADVICE, QueryIntent.RISK_ASSESSMENT]:
            if any(keyword in query_lower for keyword in complex_keywords):
                return QueryComplexity.CRITICAL  # Maximum caution needed!
            return QueryComplexity.COMPLEX  # Still needs multiple agents

        # Check for multi-part questions that need multiple perspectives
        if any(keyword in query_lower for keyword in complex_keywords):
            return QueryComplexity.COMPLEX  # Needs comprehensive analysis
        elif any(keyword in query_lower for keyword in moderate_keywords):
            return QueryComplexity.MODERATE  # Needs 2-3 agents
        else:
            return QueryComplexity.SIMPLE  # One agent is enough

    def select_agents(self, query: str, intent: QueryIntent, complexity: QueryComplexity) -> List[AgentType]:
        """Select the right team of agents for this query"""
        selected_agents = []

        # Each intent type has preferred agents
        # This is like assigning the right experts to a project
        intent_to_agents = {
            QueryIntent.MARKET_ANALYSIS: [AgentType.MARKET_ANALYST, AgentType.NEWS_ANALYST],  # Market experts
            QueryIntent.PORTFOLIO_ADVICE: [AgentType.PORTFOLIO_MANAGER, AgentType.RISK_ASSESSOR],  # Investment team
            QueryIntent.RISK_ASSESSMENT: [AgentType.RISK_ASSESSOR, AgentType.BEHAVIORAL],  # Risk + psychology
            QueryIntent.EDUCATIONAL_QUERY: [AgentType.EDUCATION],  # Teacher agent
            QueryIntent.GENERAL_CHAT: [AgentType.EDUCATION]  # Default to education
        }

        # Start with primary agents based on intent
        selected_agents = intent_to_agents.get(intent, [AgentType.EDUCATION])

        # For complex queries, add more specialized agents
        if complexity >= QueryComplexity.COMPLEX:
            # Portfolio questions also need tax advice
            if AgentType.PORTFOLIO_MANAGER in selected_agents:
                selected_agents.append(AgentType.TAX_ADVISOR)  # Tax implications matter!
            # Market analysis benefits from behavioral insights
            if AgentType.MARKET_ANALYST in selected_agents:
                selected_agents.append(AgentType.BEHAVIORAL)

        if complexity == QueryComplexity.CRITICAL:
            # Add all relevant agents for critical queries
            selected_agents.extend([
                AgentType.RISK_ASSESSOR,
                AgentType.BEHAVIORAL,
                AgentType.TAX_ADVISOR
            ])

        # Remove duplicates while preserving order
        seen = set()
        return [x for x in selected_agents if not (x in seen or seen.add(x))]

    async def prepare_agent_context(self, agent_type: AgentType, query: str, base_context: Dict) -> Dict:
        """Prepare specific context for each agent"""
        context = base_context.copy()

        # Add agent-specific data
        if agent_type == AgentType.MARKET_ANALYST:
            # Get market data
            symbols = self._extract_symbols(query)
            if symbols:
                market_data = await self.data_manager.get_stock_data(symbols[0])
                context["price_data"] = json.dumps(market_data) if market_data else "{}"

        elif agent_type == AgentType.NEWS_ANALYST:
            # Get news data
            news = await self.data_manager.search_news(query)
            context["news_data"] = json.dumps(news[:5]) if news else "[]"

        elif agent_type == AgentType.TAX_ADVISOR:
            # Add tax-relevant context
            context["tax_bracket"] = base_context.get("user_profile", {}).get("tax_bracket", "25%")

        return context

    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query"""
        import re
        # Find uppercase symbols (basic extraction)
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        return [s for s in symbols if len(s) >= 2]  # Filter out single letters

    async def execute_agents(self, agents: List[AgentType], query: str, context: Dict) -> List[Dict]:
        """Execute selected agents in parallel"""
        tasks = []

        for agent_type in agents:
            # Get DSPy signatures for this agent
            capabilities = self.agent_capabilities[agent_type]

            # Prepare agent-specific context
            agent_context = await self.prepare_agent_context(agent_type, query, context)

            # Create tasks for each capability
            for capability in capabilities:
                task_context = {
                    "agent_type": agent_type.value,
                    "capability": capability,
                    "query": query,
                    "context": agent_context
                }

                tasks.append(self._execute_single_agent(capability, task_context))

        # Execute all agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and format results
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent execution failed: {result}")
                continue

            formatted_results.append(result)

        return formatted_results

    async def _execute_single_agent(self, capability: str, task_context: Dict) -> Dict:
        """Execute a single agent capability"""
        try:
            # Map context to DSPy signature inputs
            dspy_kwargs = self._map_to_dspy_inputs(capability, task_context)

            # Execute DSPy signature
            result = await asyncio.to_thread(
                self.hybrid_system.dspy_reasoner.forward,
                capability,
                **dspy_kwargs
            )

            return {
                "agent_type": task_context["agent_type"],
                "capability": capability,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent {capability} failed: {e}")
            raise

    def _map_to_dspy_inputs(self, capability: str, task_context: Dict) -> Dict:
        """Map task context to DSPy signature inputs"""
        # This is a simplified mapping - in production, this would be more sophisticated
        base_mapping = {
            "technical": {
                "symbol": task_context.get("query", ""),
                "timeframe": "1d",
                "price_data": task_context["context"].get("price_data", "{}")
            },
            "sentiment": {
                "topic": task_context.get("query", ""),
                "news_data": task_context["context"].get("news_data", "[]"),
                "social_data": "[]"  # Placeholder
            },
            "optimize": {
                "current_portfolio": task_context["context"].get("portfolio", "{}"),
                "risk_tolerance": task_context["context"].get("risk_tolerance", "moderate"),
                "investment_goals": task_context["context"].get("goals", "growth"),
                "time_horizon": "5"
            },
            "risk": {
                "investment": task_context.get("query", ""),
                "user_profile": json.dumps(task_context["context"].get("user_profile", {})),
                "market_conditions": task_context["context"].get("market_data", "{}")
            },
            "explain": {
                "concept": task_context.get("query", ""),
                "user_level": task_context["context"].get("education_level", "beginner"),
                "context": task_context.get("query", "")
            }
        }

        return base_mapping.get(capability, {
            "question": task_context.get("query", ""),
            "user_profile": "general",
            "market_context": "{}"
        })

    def synthesize_results(self, results: List[Dict], complexity: QueryComplexity) -> Dict:
        """Synthesize results from multiple agents into coherent response"""
        if not results:
            return {
                "response": "I couldn't process your request. Please try rephrasing.",
                "confidence": 0.0
            }

        # For simple queries, return the single result
        if complexity == QueryComplexity.SIMPLE and len(results) == 1:
            return self._format_single_result(results[0])

        # For complex queries, synthesize multiple results
        synthesized = {
            "primary_response": "",
            "supporting_insights": [],
            "recommendations": [],
            "warnings": [],
            "confidence": 0.0,
            "agents_consulted": []
        }

        # Aggregate results by type
        for result in results:
            agent_type = result.get("agent_type", "unknown")
            capability = result.get("capability", "")
            agent_result = result.get("result", {})

            synthesized["agents_consulted"].append(f"{agent_type}:{capability}")

            # Extract key information based on capability
            if capability in ["technical", "sentiment", "earnings"]:
                # Market analysis results
                if hasattr(agent_result, "recommendation"):
                    synthesized["recommendations"].append(agent_result.recommendation)
                if hasattr(agent_result, "trend"):
                    synthesized["supporting_insights"].append(f"Market trend: {agent_result.trend}")

            elif capability in ["risk", "bias"]:
                # Risk and behavioral results
                if hasattr(agent_result, "risk_factors"):
                    synthesized["warnings"].extend(agent_result.risk_factors.split(","))
                if hasattr(agent_result, "detected_biases"):
                    synthesized["warnings"].append(f"Behavioral bias detected: {agent_result.detected_biases}")

            elif capability in ["optimize", "tax"]:
                # Portfolio and tax results
                if hasattr(agent_result, "recommended_allocation"):
                    synthesized["recommendations"].append(f"Portfolio: {agent_result.recommended_allocation}")
                if hasattr(agent_result, "tax_strategy"):
                    synthesized["supporting_insights"].append(f"Tax consideration: {agent_result.tax_strategy}")

            # Update confidence (average)
            if hasattr(agent_result, "confidence"):
                try:
                    conf_value = float(agent_result.confidence)
                    synthesized["confidence"] = (synthesized["confidence"] + conf_value) / 2
                except:
                    pass

        # Create coherent response
        synthesized["primary_response"] = self._create_coherent_response(synthesized)

        return synthesized

    def _format_single_result(self, result: Dict) -> Dict:
        """Format a single agent result"""
        agent_result = result.get("result", {})

        response_parts = []

        # Build response from available fields
        if hasattr(agent_result, "analysis"):
            response_parts.append(agent_result.analysis)
        if hasattr(agent_result, "recommendation"):
            response_parts.append(f"Recommendation: {agent_result.recommendation}")
        if hasattr(agent_result, "explanation"):
            response_parts.append(agent_result.explanation)

        return {
            "response": " ".join(response_parts) if response_parts else "Analysis complete.",
            "confidence": getattr(agent_result, "confidence", 75.0),
            "agent": result.get("agent_type")
        }

    def _create_coherent_response(self, synthesized: Dict) -> str:
        """Create a coherent response from synthesized results"""
        response_parts = []

        # Start with primary insights
        if synthesized["supporting_insights"]:
            response_parts.append("Based on my analysis: " + "; ".join(synthesized["supporting_insights"][:3]))

        # Add recommendations
        if synthesized["recommendations"]:
            unique_recs = list(set(synthesized["recommendations"]))
            response_parts.append("\n\nRecommendations: " + "; ".join(unique_recs[:3]))

        # Add warnings if any
        if synthesized["warnings"]:
            unique_warnings = list(set(synthesized["warnings"]))
            response_parts.append("\n\nImportant considerations: " + "; ".join(unique_warnings[:2]))

        # Add disclaimer for financial advice
        if "PORTFOLIO_MANAGER" in str(synthesized["agents_consulted"]) or "TAX_ADVISOR" in str(synthesized["agents_consulted"]):
            response_parts.append("\n\nNote: This is for educational purposes only, not financial advice.")

        return "\n".join(response_parts) if response_parts else "Analysis complete."

    async def process_complex_query(self, query: str, user_profile: Dict) -> Dict:
        """Main entry point for complex multi-agent queries"""
        try:
            # Get intent and context from RAG
            user_id = user_profile.get("user_id", "default")
            rag_context = await rag_service.retrieve_and_generate_context(
                query=query,
                user_id=user_id,
                user_context=user_profile
            )

            # Determine intent and complexity
            intent = QueryIntent[rag_context["intent"].upper()]
            complexity = self.assess_complexity(query, intent)

            logger.info(f"Processing query with complexity: {complexity.name}, intent: {intent.value}")

            # Select agents
            agents = self.select_agents(query, intent, complexity)
            logger.info(f"Selected agents: {[a.value for a in agents]}")

            # Prepare base context
            base_context = {
                "user_profile": user_profile,
                "rag_context": rag_context["context"],
                "intent": intent.value,
                "education_level": user_profile.get("education_level", "beginner"),
                "risk_tolerance": user_profile.get("risk_tolerance", "moderate")
            }

            # Execute agents in parallel
            results = await self.execute_agents(agents, query, base_context)

            # Synthesize results
            final_response = self.synthesize_results(results, complexity)

            # Add metadata
            final_response["metadata"] = {
                "complexity": complexity.name,
                "intent": intent.value,
                "agents_used": len(agents),
                "processing_time": datetime.now().isoformat()
            }

            return final_response

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "response": "I encountered an error processing your request.",
                "error": str(e),
                "confidence": 0.0
            }