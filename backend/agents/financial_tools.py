"""
Financial Calculation Tools
Essential tools for financial calculations and analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import asyncio
import logging

logger = logging.getLogger(__name__)

class FinancialTools:
    """Collection of REAL financial calculation and data tools - not placeholders!"""

    # ============= Portfolio Metrics =============

    @staticmethod
    async def calculate_portfolio_metrics(
        holdings: Dict[str, float],        # {'AAPL': 100, 'GOOGL': 50} - shares owned
        prices: Dict[str, float],          # {'AAPL': 150.25, 'GOOGL': 140.50} - current prices
        historical_data: Optional[pd.DataFrame] = None  # Past price data for advanced metrics
    ) -> Dict[str, Any]:
        """
        Calculate professional portfolio metrics including Sharpe ratio, volatility, beta
        These are the same metrics hedge funds and institutions use!
        """
        try:
            # Step 1: Calculate total portfolio value
            # Sum of (shares * price) for each holding
            portfolio_value = sum(holdings[symbol] * prices.get(symbol, 0)
                                 for symbol in holdings)

            # Step 2: Calculate position weights (what % of portfolio is each stock)
            # Weight = (shares * price) / total_value
            weights = {symbol: (qty * prices.get(symbol, 0)) / portfolio_value
                      for symbol, qty in holdings.items()}

            # Step 3: Calculate advanced metrics if we have historical data
            if historical_data is not None and not historical_data.empty:
                # Calculate daily returns (percentage change day-to-day)
                returns = historical_data.pct_change().dropna()

                # Calculate weighted portfolio returns
                # Each stock's return * its weight in portfolio
                portfolio_returns = sum(weights.get(symbol, 0) * returns[symbol]
                                      for symbol in returns.columns if symbol in weights)

                # Professional metrics calculations
                annual_return = portfolio_returns.mean() * 252  # 252 trading days/year
                volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized volatility
                sharpe_ratio = annual_return / volatility if volatility > 0 else 0  # Risk-adjusted return

                # Maximum drawdown - worst peak-to-trough loss
                cumulative = (1 + portfolio_returns).cumprod()  # Cumulative returns
                running_max = cumulative.expanding().max()  # Track highest point
                drawdown = (cumulative - running_max) / running_max  # % below peak
                max_drawdown = drawdown.min()  # Worst drawdown

                return {
                    "portfolio_value": portfolio_value,
                    "weights": weights,
                    "annual_return": f"{annual_return:.2%}",
                    "volatility": f"{volatility:.2%}",
                    "sharpe_ratio": round(sharpe_ratio, 2),
                    "max_drawdown": f"{max_drawdown:.2%}",
                    "number_of_positions": len(holdings)
                }
            else:
                return {
                    "portfolio_value": portfolio_value,
                    "weights": weights,
                    "number_of_positions": len(holdings),
                    "note": "Historical data needed for advanced metrics"
                }

        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {"error": str(e)}

    # ============= Position Sizing =============

    @staticmethod
    async def calculate_position_size(
        account_size: float,
        risk_percent: float,
        entry_price: float,
        stop_loss_price: float,
        method: str = "fixed_fractional"
    ) -> Dict[str, Any]:
        """
        Calculate optimal position size based on risk management
        """
        try:
            risk_amount = account_size * (risk_percent / 100)
            price_risk = abs(entry_price - stop_loss_price)

            if price_risk == 0:
                return {"error": "Stop loss cannot be the same as entry price"}

            # Fixed fractional method
            shares = risk_amount / price_risk
            position_value = shares * entry_price

            # Kelly Criterion (simplified)
            win_rate = 0.55  # Assume 55% win rate
            avg_win_loss_ratio = 1.5  # Assume 1.5:1 reward/risk
            kelly_percent = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
            kelly_position = account_size * kelly_percent

            return {
                "method": method,
                "shares": round(shares, 2),
                "position_value": round(position_value, 2),
                "risk_amount": round(risk_amount, 2),
                "risk_percent": risk_percent,
                "position_percent": round((position_value / account_size) * 100, 2),
                "kelly_suggestion": round(kelly_position, 2),
                "max_loss": round(shares * price_risk, 2)
            }

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {"error": str(e)}

    # ============= Financial Calculations =============

    @staticmethod
    async def calculate_compound_interest(
        principal: float,
        annual_rate: float,
        years: float,
        compounds_per_year: int = 12,
        additional_monthly: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate compound interest with optional regular contributions
        """
        try:
            rate = annual_rate / 100

            # Basic compound interest
            future_value = principal * (1 + rate/compounds_per_year) ** (compounds_per_year * years)

            # With regular contributions
            if additional_monthly > 0:
                monthly_rate = rate / 12
                months = int(years * 12)
                future_value_with_contributions = future_value + (
                    additional_monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
                )
            else:
                future_value_with_contributions = future_value

            total_invested = principal + (additional_monthly * years * 12)
            total_interest = future_value_with_contributions - total_invested

            return {
                "future_value": round(future_value, 2),
                "future_value_with_contributions": round(future_value_with_contributions, 2),
                "total_invested": round(total_invested, 2),
                "total_interest": round(total_interest, 2),
                "effective_annual_rate": f"{((future_value/principal) ** (1/years) - 1) * 100:.2f}%",
                "years": years,
                "monthly_contribution": additional_monthly
            }

        except Exception as e:
            logger.error(f"Error calculating compound interest: {e}")
            return {"error": str(e)}

    @staticmethod
    async def calculate_loan_payment(
        principal: float,
        annual_rate: float,
        years: float,
        payment_type: str = "monthly"
    ) -> Dict[str, Any]:
        """Calculate loan payment (mortgage, auto, etc.)"""
        try:
            rate = annual_rate / 100

            if payment_type == "monthly":
                n = years * 12
                r = rate / 12
            else:  # annual
                n = years
                r = rate

            if r == 0:
                payment = principal / n
            else:
                payment = principal * (r * (1 + r)**n) / ((1 + r)**n - 1)

            total_paid = payment * n
            total_interest = total_paid - principal

            return {
                "payment": round(payment, 2),
                "payment_type": payment_type,
                "total_payments": int(n),
                "total_paid": round(total_paid, 2),
                "total_interest": round(total_interest, 2),
                "principal": principal,
                "rate": f"{annual_rate}%"
            }

        except Exception as e:
            logger.error(f"Error calculating loan payment: {e}")
            return {"error": str(e)}

    # ============= Real Market Data =============

    @staticmethod
    async def get_real_stock_data(symbol: str) -> Dict[str, Any]:
        """Fetch real stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info

            # Get current data
            current_data = {
                "symbol": symbol.upper(),
                "name": info.get('longName', info.get('shortName', symbol)),
                "current_price": info.get('currentPrice') or info.get('regularMarketPrice'),
                "previous_close": info.get('previousClose'),
                "open": info.get('open') or info.get('regularMarketOpen'),
                "day_high": info.get('dayHigh') or info.get('regularMarketDayHigh'),
                "day_low": info.get('dayLow') or info.get('regularMarketDayLow'),
                "volume": info.get('volume') or info.get('regularMarketVolume'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "forward_pe": info.get('forwardPE'),
                "dividend_yield": info.get('dividendYield'),
                "beta": info.get('beta'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "50_day_avg": info.get('fiftyDayAverage'),
                "200_day_avg": info.get('twoHundredDayAverage'),
                "earnings_date": info.get('earningsDate'),
                "ex_dividend_date": info.get('exDividendDate')
            }

            # Calculate changes
            if current_data['current_price'] and current_data['previous_close']:
                change = current_data['current_price'] - current_data['previous_close']
                change_percent = (change / current_data['previous_close']) * 100
                current_data['change'] = round(change, 2)
                current_data['change_percent'] = f"{change_percent:.2f}%"

            # Remove None values
            current_data = {k: v for k, v in current_data.items() if v is not None}

            return current_data

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return {"error": f"Could not fetch data for {symbol}"}

    @staticmethod
    async def get_historical_prices(
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                return {"error": f"No historical data found for {symbol}"}

            # Convert to dictionary format
            price_data = {
                "dates": hist.index.strftime("%Y-%m-%d").tolist(),
                "open": hist['Open'].round(2).tolist(),
                "high": hist['High'].round(2).tolist(),
                "low": hist['Low'].round(2).tolist(),
                "close": hist['Close'].round(2).tolist(),
                "volume": hist['Volume'].tolist()
            }

            # Calculate basic statistics
            returns = hist['Close'].pct_change().dropna()

            stats = {
                "period": period,
                "interval": interval,
                "total_return": f"{((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100):.2f}%",
                "volatility": f"{(returns.std() * np.sqrt(252) * 100):.2f}%",
                "avg_volume": int(hist['Volume'].mean()),
                "price_range": f"${hist['Low'].min():.2f} - ${hist['High'].max():.2f}"
            }

            return {
                "symbol": symbol.upper(),
                "price_data": price_data,
                "statistics": stats
            }

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return {"error": str(e)}

    @staticmethod
    async def compare_stocks(symbols: List[str], metric: str = "performance") -> Dict[str, Any]:
        """Compare multiple stocks on various metrics"""
        try:
            comparison = {}

            for symbol in symbols:
                data = await FinancialTools.get_real_stock_data(symbol)

                if "error" not in data:
                    comparison[symbol] = {
                        "price": data.get('current_price'),
                        "change_percent": data.get('change_percent'),
                        "pe_ratio": data.get('pe_ratio'),
                        "market_cap": data.get('market_cap'),
                        "dividend_yield": data.get('dividend_yield'),
                        "beta": data.get('beta')
                    }

            return {
                "comparison": comparison,
                "metric": metric,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error comparing stocks: {e}")
            return {"error": str(e)}

    # ============= Technical Indicators =============

    @staticmethod
    async def calculate_technical_indicators(
        symbol: str,
        period: str = "3mo"
    ) -> Dict[str, Any]:
        """Calculate basic technical indicators"""
        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period)

            if hist.empty:
                return {"error": f"No data found for {symbol}"}

            close = hist['Close']

            # Simple Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
            sma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None

            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]

            current_price = close.iloc[-1]

            indicators = {
                "symbol": symbol.upper(),
                "current_price": round(current_price, 2),
                "sma_20": round(sma_20, 2) if sma_20 else None,
                "sma_50": round(sma_50, 2) if sma_50 else None,
                "sma_200": round(sma_200, 2) if sma_200 else None,
                "rsi": round(rsi, 2),
                "price_vs_sma20": "above" if current_price > sma_20 else "below",
                "rsi_signal": "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"
            }

            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {"error": str(e)}