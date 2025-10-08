"""
Swing Trading Strategy - Customized for Gold/Silver ETFs + Equities
Designed for 8-9% profit targets with monthly 7% goal
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from kite_client import KiteTradingClient
from portfolio_manager import PortfolioManager
from config import config

class SwingTradingStrategy:
    """Swing trading strategy optimized for your requirements"""
    
    def __init__(self, kite_client: KiteTradingClient, portfolio_manager: PortfolioManager):
        self.kite_client = kite_client
        self.portfolio_manager = portfolio_manager
        self.logger = logging.getLogger(__name__)
        self.name = "Swing Trading Strategy"
        
        # Track positions and their entry details
        self.position_tracker = {}
        
    def is_gold_silver_etf(self, symbol: str) -> bool:
        """Check if symbol is a gold/silver ETF"""
        gold_silver_etfs = ["GOLDBEES", "SILVERBEES"]
        return any(etf in symbol.upper() for etf in gold_silver_etfs)
    
    def get_portfolio_allocation(self, total_value: float) -> Dict[str, float]:
        """Calculate portfolio allocation based on your strategy"""
        return {
            "gold_silver": total_value * config.GOLD_SILVER_ALLOCATION,
            "equities": total_value * config.EQUITY_ALLOCATION
        }
    
    def analyze_swing_opportunity(self, symbol: str) -> Dict:
        """Analyze swing trading opportunity for a symbol"""
        try:
            # Get current quote
            quote = self.kite_client.get_quote([symbol])
            if not quote or symbol not in quote:
                return {"error": "No quote data available"}
            
            current_price = float(quote[symbol]['last_price'])
            
            # Get historical data for analysis
            historical_data = self.get_historical_data_simple(symbol, days=30)
            if not historical_data:
                return {"error": "Insufficient historical data"}
            
            # Calculate technical indicators
            analysis = self.calculate_swing_indicators(historical_data, current_price)
            analysis['symbol'] = symbol
            analysis['current_price'] = current_price
            analysis['is_gold_silver'] = self.is_gold_silver_etf(symbol)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    def get_historical_data_simple(self, symbol: str, days: int = 30) -> Optional[List[Dict]]:
        """Get historical data with fallback to quote data"""
        try:
            # Try to get historical data
            historical_data = self.get_historical_data(symbol, days)
            if historical_data and len(historical_data) > 10:
                return historical_data
            
            # Fallback: Use current quote and simulate some historical data
            quote = self.kite_client.get_quote([symbol])
            if quote and symbol in quote:
                current_price = float(quote[symbol]['last_price'])
                # Create simple historical data for analysis
                return self.create_synthetic_historical_data(current_price, days)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> Optional[List[Dict]]:
        """Get historical data for symbol"""
        try:
            # Get instrument token
            instruments = self.kite_client.get_instruments("NSE")
            if not instruments:
                return None
            
            instrument_token = None
            for instrument in instruments:
                if instrument.get('tradingsymbol') == symbol.replace('NSE:', ''):
                    instrument_token = instrument.get('instrument_token')
                    break
            
            if not instrument_token:
                return None
            
            # Get historical data
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            return self.kite_client.get_historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval="day"
            )
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def create_synthetic_historical_data(self, current_price: float, days: int) -> List[Dict]:
        """Create synthetic historical data for analysis when real data is unavailable"""
        data = []
        base_price = current_price
        
        for i in range(days):
            # Create realistic price movement
            change_percent = np.random.normal(0, 0.02)  # 2% daily volatility
            price = base_price * (1 + change_percent)
            
            data.append({
                'date': (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d'),
                'open': price * 0.99,
                'high': price * 1.02,
                'low': price * 0.98,
                'close': price,
                'volume': np.random.randint(1000, 10000)
            })
            base_price = price
        
        return data
    
    def calculate_swing_indicators(self, historical_data: List[Dict], current_price: float) -> Dict:
        """Calculate swing trading indicators"""
        try:
            # Extract closing prices
            prices = [float(candle['close']) for candle in historical_data]
            
            # Calculate moving averages
            ma_5 = np.mean(prices[-5:]) if len(prices) >= 5 else current_price
            ma_10 = np.mean(prices[-10:]) if len(prices) >= 10 else current_price
            ma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else current_price
            
            # Calculate RSI
            rsi = self.calculate_rsi(prices)
            
            # Calculate price momentum
            price_momentum = (current_price - prices[-5]) / prices[-5] * 100 if len(prices) >= 5 else 0
            
            # Calculate volatility
            volatility = np.std(prices[-10:]) / np.mean(prices[-10:]) * 100 if len(prices) >= 10 else 0
            
            # Determine trend
            trend = "bullish" if current_price > ma_20 else "bearish" if current_price < ma_20 else "sideways"
            
            # Calculate support and resistance levels
            support = min(prices[-10:]) if len(prices) >= 10 else current_price * 0.95
            resistance = max(prices[-10:]) if len(prices) >= 10 else current_price * 1.05
            
            return {
                "ma_5": ma_5,
                "ma_10": ma_10,
                "ma_20": ma_20,
                "rsi": rsi,
                "price_momentum": price_momentum,
                "volatility": volatility,
                "trend": trend,
                "support": support,
                "resistance": resistance,
                "price_vs_ma20": (current_price - ma_20) / ma_20 * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def should_buy(self, analysis: Dict) -> bool:
        """Determine if we should buy based on swing trading criteria"""
        if "error" in analysis:
            return False
        
        symbol = analysis.get('symbol', '')
        current_price = analysis.get('current_price', 0)
        rsi = analysis.get('rsi', 50)
        trend = analysis.get('trend', 'sideways')
        price_vs_ma20 = analysis.get('price_vs_ma20', 0)
        price_momentum = analysis.get('price_momentum', 0)
        
        # Different criteria for Gold/Silver ETFs vs Equities
        if self.is_gold_silver_etf(symbol):
            # Gold/Silver ETF criteria (more conservative)
            return (
                rsi < 40 and  # Oversold
                trend in ['bullish', 'sideways'] and
                price_vs_ma20 > -2  # Not too far below MA20
            )
        else:
            # Equity criteria (swing trading)
            return (
                rsi < 35 and  # Oversold
                trend == 'bullish' and
                price_vs_ma20 > -3 and  # Not too far below MA20
                price_momentum > -2  # Not in strong downtrend
            )
    
    def should_sell(self, analysis: Dict, entry_price: float) -> bool:
        """Determine if we should sell based on profit target or stop loss"""
        if "error" in analysis:
            return False
        
        current_price = analysis.get('current_price', 0)
        rsi = analysis.get('rsi', 50)
        
        # Calculate profit/loss percentage
        profit_percent = (current_price - entry_price) / entry_price * 100
        
        # Profit target reached
        if profit_percent >= config.PROFIT_TARGET_PERCENTAGE:
            self.logger.info(f"Profit target reached: {profit_percent:.2f}%")
            return True
        
        # Stop loss
        if profit_percent <= -config.STOP_LOSS_PERCENTAGE:
            self.logger.info(f"Stop loss triggered: {profit_percent:.2f}%")
            return True
        
        # Overbought condition
        if rsi > 75:
            self.logger.info(f"Overbought condition: RSI {rsi:.2f}")
            return True
        
        return False
    
    def get_position_size(self, symbol: str, current_price: float, total_portfolio_value: float) -> int:
        """Calculate position size based on portfolio allocation"""
        try:
            allocation = self.get_portfolio_allocation(total_portfolio_value)
            
            if self.is_gold_silver_etf(symbol):
                # Allocate portion of gold/silver allocation
                available_amount = allocation["gold_silver"] / 2  # Split between gold and silver
            else:
                # Allocate portion of equity allocation
                available_amount = allocation["equities"] / len([s for s in config.WATCHLIST if not self.is_gold_silver_etf(s)])
            
            # Calculate number of shares
            position_size = int(available_amount / current_price)
            
            # Apply maximum position size limit
            max_position_value = config.MAX_POSITION_SIZE
            max_shares = int(max_position_value / current_price)
            position_size = min(position_size, max_shares)
            
            return max(0, position_size)
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0
    
    def get_entry_price(self, analysis: Dict) -> float:
        """Get suggested entry price"""
        return analysis.get('current_price', 0)
    
    def get_stop_loss(self, analysis: Dict, entry_price: float) -> float:
        """Get stop loss price"""
        return entry_price * (1 - config.STOP_LOSS_PERCENTAGE / 100)
    
    def get_take_profit(self, analysis: Dict, entry_price: float) -> float:
        """Get take profit price"""
        return entry_price * (1 + config.PROFIT_TARGET_PERCENTAGE / 100)
    
    def track_position(self, symbol: str, entry_price: float, quantity: int):
        """Track position for monitoring"""
        self.position_tracker[symbol] = {
            "entry_price": entry_price,
            "quantity": quantity,
            "entry_time": datetime.now(),
            "target_price": self.get_take_profit({}, entry_price),
            "stop_loss": self.get_stop_loss({}, entry_price)
        }
    
    def get_position_status(self, symbol: str) -> Optional[Dict]:
        """Get current position status"""
        return self.position_tracker.get(symbol)
    
    def remove_position(self, symbol: str):
        """Remove position from tracking"""
        if symbol in self.position_tracker:
            del self.position_tracker[symbol]
