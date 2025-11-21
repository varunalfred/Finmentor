"""
Agent Dependency Graph
Defines which agents depend on outputs from other agents

This is critical because:
- Some agents need data from previous agents
- Running them in wrong order produces garbage results
- We want to parallelize when possible, but sequence when necessary

Example:
    Portfolio Optimizer needs Risk Assessment output
    Risk Assessment needs Market Analysis output
    So: Market Analysis → Risk Assessment → Portfolio Optimizer
"""

from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass


class AgentType(Enum):
    """Types of specialized agents"""
    # Market Analysis (no dependencies - can run first)
    MARKET_ANALYST = "market_analyst"
    TECHNICAL_ANALYSIS = "technical_analysis"
    NEWS_SENTIMENT = "news_sentiment"
    ECONOMIC_ANALYSIS = "economic_analysis"
    
    # Risk & Behavioral (depends on market analysis)
    RISK_ASSESSMENT = "risk_assessment"
    BEHAVIORAL_ANALYSIS = "behavioral"
    
    # Portfolio Management (depends on risk assessment)
    PORTFOLIO_OPTIMIZER = "portfolio_optimizer"
    
    # Financial Planning (depends on portfolio)
    TAX_ADVISOR = "tax_advisor"
    COST_ANALYZER = "cost_analyzer"
    
    # Education (no dependencies - can run anytime)
    EDUCATION = "education"
    PERSONALIZED_LEARNING = "learning"
    
    # Analysis Tools (depends on market data)
    DIVIDEND_ANALYSIS = "dividends"
    EARNINGS_ANALYSIS = "earnings"


@dataclass
class AgentDependency:
    """
    Represents dependencies for a single agent
    
    Fields:
        agent: The agent type
        depends_on: Set of agents that must complete first
        provides: List of data types this agent provides
        stage: Execution stage (0 = no dependencies, higher = more dependencies)
    """
    agent: AgentType
    depends_on: Set[AgentType]
    provides: List[str]
    stage: int


class DependencyGraph:
    """
    Manages agent dependencies and execution order
    
    Features:
    - Automatically calculates execution stages
    - Detects circular dependencies
    - Enables parallel execution within stages
    - Passes outputs between dependent agents
    """
    
    def __init__(self):
        """Initialize dependency graph with agent relationships"""
        
        # Define what each agent depends on
        self.dependencies: Dict[AgentType, Set[AgentType]] = {
            # ===== STAGE 0: No Dependencies (can run first, in parallel) =====
            AgentType.MARKET_ANALYST: set(),
            AgentType.TECHNICAL_ANALYSIS: set(),
            AgentType.NEWS_SENTIMENT: set(),
            AgentType.ECONOMIC_ANALYSIS: set(),
            AgentType.EDUCATION: set(),
            AgentType.PERSONALIZED_LEARNING: set(),
            
            # ===== STAGE 1: Depends on Market Analysis =====
            AgentType.RISK_ASSESSMENT: {
                AgentType.MARKET_ANALYST,
                AgentType.TECHNICAL_ANALYSIS,
                AgentType.ECONOMIC_ANALYSIS
            },
            AgentType.BEHAVIORAL_ANALYSIS: {
                AgentType.MARKET_ANALYST
            },
            AgentType.DIVIDEND_ANALYSIS: {
                AgentType.TECHNICAL_ANALYSIS
            },
            AgentType.EARNINGS_ANALYSIS: {
                AgentType.MARKET_ANALYST
            },
            
            # ===== STAGE 2: Depends on Risk Assessment =====
            AgentType.PORTFOLIO_OPTIMIZER: {
                AgentType.RISK_ASSESSMENT,
                AgentType.BEHAVIORAL_ANALYSIS  # Optional but recommended
            },
            
            # ===== STAGE 3: Depends on Portfolio Optimization =====
            AgentType.TAX_ADVISOR: {
                AgentType.PORTFOLIO_OPTIMIZER
            },
            AgentType.COST_ANALYZER: {
                AgentType.PORTFOLIO_OPTIMIZER
            }
        }
        
        # Define what data each agent provides (for context building)
        self.provides: Dict[AgentType, List[str]] = {
            AgentType.MARKET_ANALYST: ["market_trend", "price_analysis", "volume_analysis"],
            AgentType.TECHNICAL_ANALYSIS: ["technical_indicators", "support_resistance", "price_targets"],
            AgentType.NEWS_SENTIMENT: ["sentiment_score", "news_summary", "market_mood"],
            AgentType.ECONOMIC_ANALYSIS: ["economic_indicators", "macro_trends", "interest_rates"],
            
            AgentType.RISK_ASSESSMENT: ["risk_score", "risk_factors", "volatility_analysis"],
            AgentType.BEHAVIORAL_ANALYSIS: ["bias_detection", "investor_psychology", "emotional_state"],
            
            AgentType.PORTFOLIO_OPTIMIZER: ["recommended_allocation", "rebalancing_plan", "expected_returns"],
            
            AgentType.TAX_ADVISOR: ["tax_implications", "tax_strategy", "tax_loss_harvesting"],
            AgentType.COST_ANALYZER: ["cost_breakdown", "fee_analysis", "expense_ratio"],
            
            AgentType.EDUCATION: ["explanation", "examples", "learning_resources"],
            AgentType.DIVIDEND_ANALYSIS: ["dividend_yield", "payout_ratio", "dividend_growth"],
            AgentType.EARNINGS_ANALYSIS: ["earnings_summary", "eps_analysis", "revenue_growth"]
        }
    
    def get_execution_stages(self, agents: List[AgentType]) -> List[List[AgentType]]:
        """
        Build execution stages based on dependencies
        Agents in same stage can run in parallel
        
        Algorithm:
        1. Start with agents that have no dependencies
        2. Find agents whose dependencies are all satisfied
        3. Repeat until all agents are scheduled
        
        Args:
            agents: List of agents to execute
        
        Returns:
            List of stages, where each stage is a list of agents that can run in parallel
        
        Example:
            Input: [MARKET_ANALYST, RISK_ASSESSMENT, PORTFOLIO_OPTIMIZER]
            Output: [
                [MARKET_ANALYST],              # Stage 0: no dependencies
                [RISK_ASSESSMENT],             # Stage 1: needs MARKET_ANALYST
                [PORTFOLIO_OPTIMIZER]          # Stage 2: needs RISK_ASSESSMENT
            ]
        """
        stages = []
        remaining = set(agents)
        completed = set()
        
        max_iterations = len(agents) + 1  # Prevent infinite loop
        iteration = 0
        
        while remaining and iteration < max_iterations:
            # Find agents whose dependencies are all satisfied
            ready = {
                agent for agent in remaining
                if self.dependencies.get(agent, set()).issubset(completed)
            }
            
            if not ready:
                # No agents ready but still have remaining agents
                # This means circular dependency!
                raise ValueError(
                    f"Circular dependency detected! "
                    f"Remaining agents: {[a.value for a in remaining]} "
                    f"Completed agents: {[a.value for a in completed]}"
                )
            
            # Add this stage
            stages.append(list(ready))
            completed.update(ready)
            remaining -= ready
            
            iteration += 1
        
        return stages
    
    def get_dependencies(self, agent: AgentType) -> Set[AgentType]:
        """Get the set of agents that must complete before this agent"""
        return self.dependencies.get(agent, set())
    
    def get_dependents(self, agent: AgentType) -> Set[AgentType]:
        """Get the set of agents that depend on this agent"""
        return {
            dependent_agent 
            for dependent_agent, deps in self.dependencies.items()
            if agent in deps
        }
    
    def get_provided_data(self, agent: AgentType) -> List[str]:
        """Get the list of data types this agent provides"""
        return self.provides.get(agent, [])
    
    def validate_agent_selection(self, agents: List[AgentType]) -> tuple[bool, str]:
        """
        Validate that all dependencies are satisfied
        
        Returns:
            (is_valid, error_message)
        """
        agent_set = set(agents)
        
        for agent in agents:
            deps = self.get_dependencies(agent)
            missing = deps - agent_set
            
            if missing:
                return False, (
                    f"Agent {agent.value} requires {[a.value for a in missing]} "
                    f"but they are not in the selected agents list"
                )
        
        return True, ""
    
    def suggest_additional_agents(self, agents: List[AgentType]) -> Set[AgentType]:
        """
        Suggest additional agents that would benefit from the selected agents
        
        Example:
            If MARKET_ANALYST is selected, suggest RISK_ASSESSMENT
            (since it can use the market data)
        """
        agent_set = set(agents)
        suggestions = set()
        
        for agent in agents:
            # Find agents that depend on this one
            dependents = self.get_dependents(agent)
            
            for dependent in dependents:
                # Check if all dependencies of the dependent are satisfied
                if self.dependencies[dependent].issubset(agent_set):
                    suggestions.add(dependent)
        
        # Remove agents that are already selected
        return suggestions - agent_set
    
    def get_execution_plan(self, agents: List[AgentType]) -> Dict:
        """
        Get detailed execution plan with stages and dependencies
        
        Returns:
            Dictionary with execution plan details
        """
        # Validate selection
        is_valid, error = self.validate_agent_selection(agents)
        if not is_valid:
            return {
                "valid": False,
                "error": error,
                "stages": []
            }
        
        # Get execution stages
        stages = self.get_execution_stages(agents)
        
        # Build detailed plan
        plan = {
            "valid": True,
            "total_agents": len(agents),
            "total_stages": len(stages),
            "stages": [],
            "estimated_time_multiplier": len(stages)  # vs fully parallel
        }
        
        for stage_num, stage_agents in enumerate(stages):
            stage_info = {
                "stage": stage_num,
                "agents": [a.value for a in stage_agents],
                "parallelizable": len(stage_agents) > 1,
                "dependencies": {
                    a.value: [d.value for d in self.get_dependencies(a)]
                    for a in stage_agents
                },
                "provides": {
                    a.value: self.get_provided_data(a)
                    for a in stage_agents
                }
            }
            plan["stages"].append(stage_info)
        
        # Add suggestions
        suggestions = self.suggest_additional_agents(agents)
        if suggestions:
            plan["suggested_agents"] = [a.value for a in suggestions]
        
        return plan


# Create singleton instance
dependency_graph = DependencyGraph()
