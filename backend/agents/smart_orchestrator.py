"""
Smart Multi-Agent Orchestrator with Rate Limiting and Dependency Awareness

Key Features:
1. Rate-limited execution (respects Gemini's 10 RPM free tier)
2. Dependency-aware agent scheduling (agents run in correct order)
3. Parallel execution within stages (agents without dependencies run together)
4. Automatic context passing between dependent agents

Author: Roshan Varghese
Date: 2025
"""

import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
import logging
import json

from agents.hybrid_core import HybridFinMentorSystem
from agents.dependency_graph import dependency_graph, AgentType
from utils.rate_limiter import SmartRateLimitedOrchestrator
from services.agentic_rag import rag_service, QueryIntent
from services.data_sources import DataSourcesManager

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels - determines how many agents to use"""
    SIMPLE = 1      # Single agent can handle (e.g., "What is P/E ratio?")
    MODERATE = 2    # 2-3 agents needed (e.g., "Compare AAPL and MSFT")
    COMPLEX = 3     # Multiple agents with synthesis (e.g., "Analyze my portfolio")
    CRITICAL = 4    # All relevant agents + verification (e.g., "Should I sell everything?")


class SmartMultiAgentOrchestrator:
    """
    Intelligent orchestrator that:
    - Respects API rate limits (10 RPM for Gemini free tier)
    - Executes agents in correct order based on dependencies
    - Runs agents in parallel when possible
    - Passes outputs between dependent agents
    """
    
    def __init__(
        self, 
        hybrid_system: HybridFinMentorSystem,
        rpm_limit: int = 10,
        max_concurrent: int = 2
    ):
        """
        Args:
            hybrid_system: The hybrid DSPy system with all agents
            rpm_limit: Requests per minute limit (10 for Gemini free tier)
            max_concurrent: Max parallel agents (2 for safe free tier usage)
        """
        self.hybrid_system = hybrid_system
        self.dependency_graph = dependency_graph
        
        # Data manager for fetching market data, news, etc.
        self.data_manager = DataSourcesManager()
        
        # Rate limiting orchestrator
        self.rate_limited_orchestrator = SmartRateLimitedOrchestrator(
            rpm_limit=rpm_limit,
            max_concurrent=max_concurrent
        )
        
        logger.info(
            f"🎯 Smart Orchestrator initialized: "
            f"{rpm_limit} RPM limit, {max_concurrent} max concurrent"
        )
    
    def assess_complexity(self, query: str, intent: QueryIntent) -> QueryComplexity:
        """
        Assess query complexity to determine how many agents we need
        (Ported from old orchestrator for backward compatibility)
        """
        # Keywords that suggest we need comprehensive analysis
        complex_keywords = ["portfolio", "comprehensive", "analyze everything", "full assessment"]
        # Keywords that suggest comparison or multiple aspects
        moderate_keywords = ["compare", "and", "versus", "or"]

        query_lower = query.lower()

        # Portfolio and risk questions are always treated seriously
        if intent in [QueryIntent.PORTFOLIO_ADVICE, QueryIntent.RISK_ASSESSMENT]:
            if any(keyword in query_lower for keyword in complex_keywords):
                return QueryComplexity.CRITICAL
            return QueryComplexity.COMPLEX

        # Check for multi-part questions
        if any(keyword in query_lower for keyword in complex_keywords):
            return QueryComplexity.COMPLEX
        elif any(keyword in query_lower for keyword in moderate_keywords):
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def select_agents(self, query: str, intent: QueryIntent, complexity: QueryComplexity) -> List[AgentType]:
        """
        Select the right team of agents for this query
        (Ported from old orchestrator for backward compatibility)
        """
        # Map intents to primary agents
        intent_to_agents = {
            QueryIntent.MARKET_ANALYSIS: [AgentType.MARKET_ANALYST, AgentType.NEWS_SENTIMENT],
            QueryIntent.PORTFOLIO_ADVICE: [AgentType.PORTFOLIO_OPTIMIZER, AgentType.RISK_ASSESSMENT],
            QueryIntent.RISK_ASSESSMENT: [AgentType.RISK_ASSESSMENT, AgentType.BEHAVIORAL_ANALYSIS],
            QueryIntent.EDUCATIONAL_QUERY: [AgentType.EDUCATION],
            QueryIntent.GENERAL_CHAT: [AgentType.EDUCATION]
        }

        # Start with primary agents
        selected_agents = list(intent_to_agents.get(intent, [AgentType.EDUCATION]))

        # Add more agents for complex queries
        if complexity.value >= QueryComplexity.COMPLEX.value:
            if AgentType.PORTFOLIO_OPTIMIZER in selected_agents:
                selected_agents.append(AgentType.TAX_ADVISOR)
            if AgentType.MARKET_ANALYST in selected_agents:
                selected_agents.append(AgentType.BEHAVIORAL_ANALYSIS)

        if complexity == QueryComplexity.CRITICAL:
            selected_agents.extend([
                AgentType.RISK_ASSESSMENT,
                AgentType.BEHAVIORAL_ANALYSIS,
                AgentType.TAX_ADVISOR
            ])

        # Remove duplicates while preserving order
        seen = set()
        agents_list = [x for x in selected_agents if not (x in seen or seen.add(x))]
        
        # Auto-include dependencies
        agents_with_deps = self._expand_with_dependencies(agents_list)
        
        return agents_with_deps
    
    def _expand_with_dependencies(self, agents: List[AgentType]) -> List[AgentType]:
        """
        Automatically include all required dependencies for selected agents
        
        This prevents "Invalid agent selection" errors by ensuring all
        dependencies are satisfied.
        
        Args:
            agents: List of desired agents
        
        Returns:
            Expanded list including all dependencies
        """
        agent_set = set(agents)
        expanded = set(agents)
        
        # Keep adding dependencies until no new ones are found
        changed = True
        while changed:
            changed = False
            for agent in list(expanded):
                deps = self.dependency_graph.get_dependencies(agent)
                new_deps = deps - expanded
                if new_deps:
                    expanded.update(new_deps)
                    changed = True
        
        # Convert back to list, preserving dependency order
        # (dependencies should come before dependents)
        execution_plan = self.dependency_graph.get_execution_plan(list(expanded))
        ordered_agents = []
        for stage_info in execution_plan["stages"]:
            ordered_agents.extend([AgentType(name) for name in stage_info["agents"]])
        
        return ordered_agents
    
    async def process_complex_query(self, query: str, user_profile: Dict) -> Dict:
        """
        Main entry point for complex multi-agent queries
        (Ported from old orchestrator for backward compatibility)
        
        This method:
        1. Gets RAG context and intent
        2. Assesses complexity
        3. Selects appropriate agents
        4. Processes with rate limiting and dependencies
        """
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

            # Select agents automatically
            agents = self.select_agents(query, intent, complexity)
            logger.info(f"Selected agents: {[a.value for a in agents]}")

            # Process with the new rate-limited system
            result = await self.process_query(
                query=query,
                required_agents=agents,
                user_profile=user_profile
            )

            # Add metadata
            result["metadata"]["complexity"] = complexity.name
            result["metadata"]["intent"] = intent.value

            return result

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "success": False,
                "response": "I encountered an error processing your request.",
                "error": str(e),
                "confidence": 0.0
            }
    
    async def process_query(
        self, 
        query: str, 
        required_agents: List[AgentType],
        user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process query with dependency-aware, rate-limited execution
        
        Flow:
        1. Validate agent dependencies
        2. Build execution stages
        3. Execute each stage with rate limiting
        4. Pass outputs between stages
        5. Synthesize final response
        
        Args:
            query: User's query
            required_agents: List of agents to use
            user_profile: Optional user profile for personalization
        
        Returns:
            Dictionary with response and metadata
        """
        start_time = datetime.now()
        
        logger.info(f"🚀 Processing query: {query[:100]}...")
        logger.info(f"📋 Required agents: {[a.value for a in required_agents]}")
        
        # Step 1: Validate dependencies
        is_valid, error = self.dependency_graph.validate_agent_selection(required_agents)
        if not is_valid:
            logger.error(f"❌ Invalid agent selection: {error}")
            return {
                "success": False,
                "error": f"Invalid agent selection: {error}",
                "response": "I couldn't process your request due to agent dependency issues."
            }
        
        # Step 2: Get execution plan
        execution_plan = self.dependency_graph.get_execution_plan(required_agents)
        stages = execution_plan["stages"]
        
        logger.info(f"📊 Execution plan: {len(stages)} stages")
        for stage_info in stages:
            logger.info(
                f"  Stage {stage_info['stage']}: "
                f"{stage_info['agents']} "
                f"({'parallel' if stage_info['parallelizable'] else 'sequential'})"
            )
        
        # Step 3: Execute stages
        all_results = {}
        
        for stage_num, stage_info in enumerate(stages):
            stage_agents = [AgentType(name) for name in stage_info["agents"]]
            
            logger.info(f"⚡ Executing Stage {stage_num + 1}/{len(stages)}...")
            
            # Execute this stage with rate limiting
            stage_results = await self._execute_stage(
                stage_agents=stage_agents,
                query=query,
                previous_results=all_results,
                user_profile=user_profile or {}
            )
            
            # Store results for next stage
            all_results.update(stage_results)
            
            logger.info(
                f"✅ Stage {stage_num + 1} complete: "
                f"{[a.value for a in stage_results.keys()]}"
            )
        
        # Step 4: Synthesize results
        final_response = self._synthesize_results(all_results, execution_plan)
        
        # Step 5: Add metadata
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        final_response["metadata"] = {
            "total_agents": len(required_agents),
            "total_stages": len(stages),
            "processing_time_seconds": processing_time,
            "execution_plan": execution_plan,
            "timestamp": end_time.isoformat()
        }
        
        logger.info(f"✅ Query processed in {processing_time:.2f}s")
        
        return final_response
    
    async def _execute_stage(
        self,
        stage_agents: List[AgentType],
        query: str,
        previous_results: Dict[AgentType, Any],
        user_profile: Dict
    ) -> Dict[AgentType, Any]:
        """
        Execute all agents in a single stage with rate limiting
        
        Args:
            stage_agents: Agents to execute in this stage
            query: Original user query
            previous_results: Results from previous stages
            user_profile: User profile data
        
        Returns:
            Dictionary mapping agent type to result
        """
        # Create tasks for all agents in this stage
        tasks = []
        for agent in stage_agents:
            task_func = self._create_agent_task(
                agent_type=agent,
                query=query,
                previous_results=previous_results,
                user_profile=user_profile
            )
            tasks.append(task_func)
        
        # Execute with rate limiting
        results = await self.rate_limited_orchestrator.execute_with_rate_limit(tasks)
        
        # Map results back to agent types
        stage_results = {}
        for agent, result in zip(stage_agents, results):
            if isinstance(result, Exception):
                logger.error(f"❌ Agent {agent.value} failed: {result}")
                stage_results[agent] = {
                    "error": str(result),
                    "success": False
                }
            else:
                stage_results[agent] = result
        
        return stage_results
    
    def _create_agent_task(
        self,
        agent_type: AgentType,
        query: str,
        previous_results: Dict[AgentType, Any],
        user_profile: Dict
    ):
        """
        Create an async task for a single agent
        
        Returns:
            Async callable that executes the agent
        """
        async def execute_agent():
            # Build context from dependencies
            dependencies = self.dependency_graph.get_dependencies(agent_type)
            context = self._build_context_from_dependencies(
                dependencies=dependencies,
                previous_results=previous_results,
                user_profile=user_profile
            )
            
            # Build enriched query with context
            enriched_query = self._build_enriched_query(query, context)
            
            logger.debug(f"▶️ Executing {agent_type.value}")
            
            # Execute agent via hybrid system
            try:
                result = await self._execute_agent(
                    agent_type=agent_type,
                    query=enriched_query,
                    context=context
                )
                
                logger.debug(f"✅ {agent_type.value} completed")
                
                return {
                    "agent": agent_type.value,
                    "result": result,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ {agent_type.value} failed: {e}")
                raise
        
        return execute_agent
    
    def _build_context_from_dependencies(
        self,
        dependencies: Set[AgentType],
        previous_results: Dict[AgentType, Any],
        user_profile: Dict
    ) -> Dict[str, Any]:
        """
        Build context dictionary from dependent agent outputs
        
        Args:
            dependencies: Set of agents this agent depends on
            previous_results: Results from all previous agents
            user_profile: User profile data
        
        Returns:
            Context dictionary with relevant data
        """
        context = {
            "user_profile": user_profile,
            "previous_analyses": {}
        }
        
        # Add outputs from dependent agents
        for dep_agent in dependencies:
            if dep_agent in previous_results:
                dep_result = previous_results[dep_agent]
                
                # Extract key data provided by this agent
                provided_data = self.dependency_graph.get_provided_data(dep_agent)
                
                context["previous_analyses"][dep_agent.value] = {
                    "agent": dep_agent.value,
                    "data_types": provided_data,
                    "result": dep_result.get("result", {})
                }
        
        return context
    
    def _build_enriched_query(self, query: str, context: Dict) -> str:
        """
        Build enriched query with context from previous agents
        
        This is CRITICAL for dependent agents:
        - Portfolio Optimizer needs Risk Assessment data
        - Risk Assessment needs Market Analysis data
        - We inject this data into the query/prompt
        """
        if not context.get("previous_analyses"):
            return query
        
        # Build context summary
        context_parts = []
        for agent_name, agent_data in context["previous_analyses"].items():
            context_parts.append(
                f"**{agent_name.replace('_', ' ').title()}:**"
            )
            
            # Extract result text
            result = agent_data.get("result", {})
            if isinstance(result, dict):
                # DSPy Signature result
                if "analysis" in result:
                    context_parts.append(f"  {result['analysis']}")
                elif "recommendation" in result:
                    context_parts.append(f"  {result['recommendation']}")
                elif "explanation" in result:
                    context_parts.append(f"  {result['explanation']}")
            elif isinstance(result, str):
                context_parts.append(f"  {result[:200]}")
        
        context_str = "\n".join(context_parts)
        
        # Build enriched query
        enriched_query = f"""
{query}

**Context from previous analysis:**
{context_str}

**Your task:**
Based on the above context and your specialized knowledge, provide your analysis.
"""
        
        return enriched_query
    
    async def _execute_agent(
        self,
        agent_type: AgentType,
        query: str,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Execute a single agent via the hybrid system
        
        This is where we actually call the DSPy signatures
        """
        # Map agent type to query type (for your existing system)
        agent_to_query_type = {
            AgentType.MARKET_ANALYST: "analyze",
            AgentType.TECHNICAL_ANALYSIS: "technical",
            AgentType.NEWS_SENTIMENT: "sentiment",
            AgentType.ECONOMIC_ANALYSIS: "economic",
            AgentType.RISK_ASSESSMENT: "risk_assessment",
            AgentType.BEHAVIORAL_ANALYSIS: "bias_detection",
            AgentType.PORTFOLIO_OPTIMIZER: "portfolio_optimization",
            AgentType.TAX_ADVISOR: "tax_implications",
            AgentType.COST_ANALYZER: "analyze",
            AgentType.EDUCATION: "explain",
            AgentType.PERSONALIZED_LEARNING: "personalized_learning",
            AgentType.DIVIDEND_ANALYSIS: "dividend_analysis",
            AgentType.EARNINGS_ANALYSIS: "earnings_analysis"
        }
        
        query_type = agent_to_query_type.get(agent_type, "explain")
        
        # Execute via hybrid system
        # Note: process_query doesn't accept query_type parameter
        # The routing is done internally based on query content
        # IMPORTANT: Skip orchestration to prevent infinite recursion!
        user_profile = context.get("user_profile", {
            "user_id": "orchestrator-user",
            "type": "intermediate",
            "education_level": "intermediate"
        })
        
        result = await self.hybrid_system.process_query(
            query=query,
            user_profile=user_profile,
            skip_orchestration=True  # ← CRITICAL: Prevent recursion!
        )
        
        return result
    
    def _synthesize_results(
        self,
        all_results: Dict[AgentType, Any],
        execution_plan: Dict
    ) -> Dict[str, Any]:
        """
        Synthesize results from all agents into coherent response
        
        Strategy:
        - Primary response from final stage (most dependent agents)
        - Supporting insights from earlier stages
        - Recommendations and warnings from all agents
        """
        if not all_results:
            return {
                "success": False,
                "response": "No agents were executed successfully.",
                "confidence": 0.0
            }
        
        # Get stages in reverse order (final stage = most important)
        stages = execution_plan["stages"]
        
        synthesized = {
            "success": True,
            "primary_response": "",
            "supporting_insights": [],
            "recommendations": [],
            "warnings": [],
            "confidence": 0.0,
            "agents_consulted": []
        }
        
        # Process results by stage (reverse order for primary response)
        for stage_info in reversed(stages):
            stage_agents = [AgentType(name) for name in stage_info["agents"]]
            
            for agent_type in stage_agents:
                if agent_type not in all_results:
                    continue
                
                agent_result = all_results[agent_type]
                
                if not agent_result.get("success", False):
                    continue
                
                synthesized["agents_consulted"].append(agent_type.value)
                
                # Extract result content
                result_content = agent_result.get("result", {})
                
                # Primary response from final stage
                if not synthesized["primary_response"] and isinstance(result_content, dict):
                    if "analysis" in result_content:
                        synthesized["primary_response"] = result_content["analysis"]
                    elif "explanation" in result_content:
                        synthesized["primary_response"] = result_content["explanation"]
                    elif "recommendation" in result_content:
                        synthesized["primary_response"] = result_content["recommendation"]
                
                # Extract recommendations
                if isinstance(result_content, dict):
                    if "recommendation" in result_content:
                        synthesized["recommendations"].append(
                            f"{agent_type.value}: {result_content['recommendation']}"
                        )
                    
                    # Extract warnings/risks
                    if "risk_factors" in result_content:
                        synthesized["warnings"].extend(
                            result_content["risk_factors"].split(",")
                        )
                    
                    # Extract confidence
                    if "confidence" in result_content:
                        try:
                            conf = float(result_content["confidence"])
                            synthesized["confidence"] = (
                                synthesized["confidence"] + conf
                            ) / 2 if synthesized["confidence"] > 0 else conf
                        except:
                            pass
        
        # Build final response
        response_parts = []
        
        if synthesized["primary_response"]:
            response_parts.append(synthesized["primary_response"])
        
        if synthesized["recommendations"]:
            response_parts.append("\n\n**Recommendations:**")
            for rec in synthesized["recommendations"][:3]:
                response_parts.append(f"  • {rec}")
        
        if synthesized["warnings"]:
            response_parts.append("\n\n**Important Considerations:**")
            for warning in list(set(synthesized["warnings"]))[:3]:
                response_parts.append(f"  ⚠️ {warning.strip()}")
        
        synthesized["response"] = "\n".join(response_parts) if response_parts else "Analysis complete."
        
        # Add disclaimer for financial advice
        if any(
            agent in ["portfolio_optimizer", "tax_advisor", "risk_assessment"]
            for agent in synthesized["agents_consulted"]
        ):
            synthesized["response"] += (
                "\n\n*Note: This is for educational purposes only, "
                "not professional financial advice.*"
            )
        
        return synthesized


# Example usage
async def test_smart_orchestrator():
    """Test the smart orchestrator with dependency-aware execution"""
    from agents.hybrid_core import HybridFinMentorSystem
    from services.database import db_service
    
    # Initialize system
    config = {"model": "gemini-2.5-flash"}
    
    async with db_service.AsyncSessionLocal() as session:
        hybrid_system = HybridFinMentorSystem(config, db_session=session)
        orchestrator = SmartMultiAgentOrchestrator(
            hybrid_system=hybrid_system,
            rpm_limit=10,  # Free tier
            max_concurrent=2  # Safe for free tier
        )
        
        # Complex portfolio query
        query = "I want to invest $10,000 in tech stocks. What should I do?"
        
        # Select agents (orchestrator will handle dependencies)
        required_agents = [
            AgentType.MARKET_ANALYST,
            AgentType.RISK_ASSESSMENT,
            AgentType.PORTFOLIO_OPTIMIZER,
            AgentType.TAX_ADVISOR
        ]
        
        # Process query
        result = await orchestrator.process_query(
            query=query,
            required_agents=required_agents,
            user_profile={"risk_tolerance": "moderate"}
        )
        
        print("\n" + "="*80)
        print("SMART ORCHESTRATOR TEST RESULT")
        print("="*80)
        print(f"Success: {result['success']}")
        print(f"Response:\n{result['response']}")
        print(f"\nMetadata:")
        print(f"  Total agents: {result['metadata']['total_agents']}")
        print(f"  Total stages: {result['metadata']['total_stages']}")
        print(f"  Processing time: {result['metadata']['processing_time_seconds']:.2f}s")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_smart_orchestrator())
