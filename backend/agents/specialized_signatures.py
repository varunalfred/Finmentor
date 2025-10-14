"""
Specialized DSPy Signatures for Multi-Agent Capabilities
Each signature represents a specialized agent's reasoning
"""

import dspy
from typing import Optional

# ============= Market Analysis Agent =============

class MarketTechnicalAnalysis(dspy.Signature):
    """Technical analysis of stocks and market trends"""
    symbol = dspy.InputField(desc="stock symbol or market index")
    timeframe = dspy.InputField(desc="analysis timeframe (1d, 1w, 1m, 3m, 1y)")
    price_data = dspy.InputField(desc="historical price data")

    trend = dspy.OutputField(desc="bullish/bearish/neutral")
    support_levels = dspy.OutputField(desc="key support price levels")
    resistance_levels = dspy.OutputField(desc="key resistance price levels")
    indicators = dspy.OutputField(desc="RSI, MACD, moving averages analysis")
    recommendation = dspy.OutputField(desc="buy/hold/sell recommendation")
    confidence = dspy.OutputField(desc="confidence score 0-100")

class MarketSentimentAnalysis(dspy.Signature):
    """Analyze market sentiment from news and social media"""
    topic = dspy.InputField(desc="company or market topic")
    news_data = dspy.InputField(desc="recent news articles")
    social_data = dspy.InputField(desc="social media mentions")

    sentiment = dspy.OutputField(desc="positive/negative/neutral")
    sentiment_score = dspy.OutputField(desc="sentiment score -1 to 1")
    key_themes = dspy.OutputField(desc="main themes in discussions")
    market_impact = dspy.OutputField(desc="expected impact on price")
    confidence = dspy.OutputField(desc="confidence score 0-100")

# ============= Portfolio Management Agent =============

class PortfolioOptimization(dspy.Signature):
    """Optimize portfolio allocation based on goals and risk"""
    current_portfolio = dspy.InputField(desc="current holdings and allocations")
    risk_tolerance = dspy.InputField(desc="low/moderate/high risk tolerance")
    investment_goals = dspy.InputField(desc="retirement/growth/income goals")
    time_horizon = dspy.InputField(desc="investment timeframe in years")

    recommended_allocation = dspy.OutputField(desc="optimal asset allocation")
    rebalancing_actions = dspy.OutputField(desc="specific buy/sell actions")
    expected_return = dspy.OutputField(desc="projected annual return")
    risk_score = dspy.OutputField(desc="portfolio risk score 1-10")
    diversification_score = dspy.OutputField(desc="diversification quality 1-10")

class DividendAnalysis(dspy.Signature):
    """Analyze dividend stocks and income strategies"""
    symbols = dspy.InputField(desc="stock symbols to analyze")
    income_target = dspy.InputField(desc="desired monthly/annual income")

    dividend_yield = dspy.OutputField(desc="current and historical yields")
    dividend_safety = dspy.OutputField(desc="sustainability assessment")
    growth_rate = dspy.OutputField(desc="dividend growth rate")
    recommended_stocks = dspy.OutputField(desc="top dividend stock picks")
    income_projection = dspy.OutputField(desc="projected income stream")

# ============= Tax Strategy Agent =============

class TaxImplications(dspy.Signature):
    """Analyze tax implications of investment decisions"""
    transaction_type = dspy.InputField(desc="buy/sell/dividend/rebalance")
    holding_period = dspy.InputField(desc="time held in days")
    gain_loss = dspy.InputField(desc="profit or loss amount")
    tax_bracket = dspy.InputField(desc="user's tax bracket")

    tax_treatment = dspy.OutputField(desc="short-term/long-term/qualified")
    estimated_tax = dspy.OutputField(desc="estimated tax liability")
    tax_strategy = dspy.OutputField(desc="tax optimization suggestions")
    harvesting_opportunities = dspy.OutputField(desc="tax loss harvesting options")

# ============= News & Events Agent =============

class EarningsAnalysis(dspy.Signature):
    """Analyze company earnings and forward guidance"""
    symbol = dspy.InputField(desc="company stock symbol")
    earnings_data = dspy.InputField(desc="recent earnings report")
    analyst_estimates = dspy.InputField(desc="analyst expectations")

    earnings_surprise = dspy.OutputField(desc="beat/miss/meet expectations")
    revenue_trend = dspy.OutputField(desc="revenue growth analysis")
    guidance_assessment = dspy.OutputField(desc="forward guidance analysis")
    analyst_sentiment = dspy.OutputField(desc="analyst recommendation changes")
    price_impact = dspy.OutputField(desc="expected stock price impact")

class EconomicIndicatorAnalysis(dspy.Signature):
    """Analyze economic indicators and their market impact"""
    indicator = dspy.InputField(desc="GDP/CPI/unemployment/interest rates")
    current_value = dspy.InputField(desc="latest indicator value")
    historical_data = dspy.InputField(desc="historical indicator values")

    trend_analysis = dspy.OutputField(desc="indicator trend interpretation")
    economic_outlook = dspy.OutputField(desc="economic growth forecast")
    sector_impact = dspy.OutputField(desc="impact on different sectors")
    investment_implications = dspy.OutputField(desc="portfolio adjustments needed")

# ============= Education Agent Enhancement =============

class PersonalizedLearning(dspy.Signature):
    """Create personalized learning paths"""
    user_level = dspy.InputField(desc="beginner/intermediate/advanced")
    learning_goals = dspy.InputField(desc="what user wants to learn")
    completed_topics = dspy.InputField(desc="topics already covered")
    learning_style = dspy.InputField(desc="visual/text/interactive preference")

    next_topic = dspy.OutputField(desc="recommended next topic")
    learning_path = dspy.OutputField(desc="structured learning sequence")
    resources = dspy.OutputField(desc="articles, videos, exercises")
    estimated_time = dspy.OutputField(desc="time to complete")
    skill_assessment = dspy.OutputField(desc="quiz or practice problems")

# ============= Behavioral Finance Agent =============

class BehavioralBiasDetection(dspy.Signature):
    """Detect and address behavioral biases in investment decisions"""
    user_action = dspy.InputField(desc="proposed investment action")
    market_context = dspy.InputField(desc="current market conditions")
    user_history = dspy.InputField(desc="past investment decisions")

    detected_biases = dspy.OutputField(desc="FOMO, loss aversion, anchoring, etc")
    bias_impact = dspy.OutputField(desc="how bias affects decision")
    debiasing_strategy = dspy.OutputField(desc="techniques to overcome bias")
    rational_alternative = dspy.OutputField(desc="emotion-free recommendation")

class PsychologicalProfiling(dspy.Signature):
    """Profile investor psychology and risk tolerance"""
    questionnaire_responses = dspy.InputField(desc="risk assessment answers")
    investment_history = dspy.InputField(desc="past investment behavior")
    reaction_to_volatility = dspy.InputField(desc="behavior during market swings")

    investor_type = dspy.OutputField(desc="conservative/moderate/aggressive")
    true_risk_tolerance = dspy.OutputField(desc="actual vs stated risk tolerance")
    behavioral_patterns = dspy.OutputField(desc="identified behavior patterns")
    coaching_recommendations = dspy.OutputField(desc="personalized coaching tips")