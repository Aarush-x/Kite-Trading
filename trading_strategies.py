"""
Trading Strategies Module
Implements various automated trading strategies
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from kite_client import KiteTradingClient
from portfolio_manager import PortfolioManager
from config import config

class TechnicalIndicators:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        rsi_values = []
        for i in range(period, len(prices)):
            avg_gain = sum(gains[i-period:i]) / period
            avg_loss = sum(losses[i-period:i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    @staticmethod
    def calculate_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        ma_values = []
        for i in range(period - 1, len(prices)):
            ma = sum(prices[i-period+1:i+1]) / period
            ma_values.append(ma)
        
        return ma_values
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[List[float], List[float], List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return [], [], []
        
        ma = TechnicalIndicators.calculate_moving_average(prices, period)
        upper_band = []
        lower_band = []
        
        for i in range(period - 1, len(prices)):
            period_prices = prices[i-period+1:i+1]
            std = np.std(period_prices)
            upper = ma[i-period+1] + (std_dev * std)
            lower = ma[i-period+1] - (std_dev * std)
            upper_band.append(upper)
            lower_band.append(lower)
        
        return upper_band, ma, lower_band
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """Calculate MACD"""
        if len(prices) < slow_period:
            return [], [], []
        
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast_period)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow_period)
        
        # Align lengths
        min_length = min(len(ema_fast), len(ema_slow))
        ema_fast = ema_fast[-min_length:]
        ema_slow = ema_slow[-min_length:]
        
        macd_line = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal_period)
        
        # Align signal line with macd line
        signal_line = signal_line[-len(macd_line):]
        histogram = [macd - signal for macd, signal in zip(macd_line, signal_line)]
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = [prices[0]]  # First value is the first price
        
        for i in range(1, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, kite_client: KiteTradingClient, portfolio_manager: PortfolioManager):
        self.kite_client = kite_client
        self.portfolio_manager = portfolio_manager
        self.logger = logging.getLogger(__name__)
        self.name = "Base Strategy"
    
    def get_historical_data(self, symbol: str, days: int = 100) -> Optional[List[Dict]]:
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
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze symbol and return trading signals"""
        raise NotImplementedError("Subclasses must implement analyze_symbol method")
    
    def should_buy(self, analysis: Dict) -> bool:
        """Determine if we should buy based on analysis"""
        raise NotImplementedError("Subclasses must implement should_buy method")
    
    def should_sell(self, analysis: Dict) -> bool:
        """Determine if we should sell based on analysis"""
        raise NotImplementedError("Subclasses must implement should_sell method")
    
    def get_entry_price(self, analysis: Dict) -> float:
        """Get suggested entry price"""
        return analysis.get('current_price', 0)
    
    def get_stop_loss(self, analysis: Dict, entry_price: float) -> float:
        """Get stop loss price"""
        return entry_price * (1 - config.STOP_LOSS_PERCENTAGE / 100)
    
    def get_take_profit(self, analysis: Dict, entry_price: float) -> float:
        """Get take profit price"""
        return entry_price * (1 + config.TAKE_PROFIT_PERCENTAGE / 100)

class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy"""
    
    def __init__(self, kite_client: KiteTradingClient, portfolio_manager: PortfolioManager):
        super().__init__(kite_client, portfolio_manager)
        self.name = "RSI Strategy"
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze symbol using RSI"""
        try:
            historical_data = self.get_historical_data(symbol)
            if not historical_data or len(historical_data) < 20:
                return {"error": "Insufficient data"}
            
            # Extract closing prices
            prices = [float(candle['close']) for candle in historical_data]
            current_price = prices[-1]
            
            # Calculate RSI
            rsi_values = TechnicalIndicators.calculate_rsi(prices, 14)
            if not rsi_values:
                return {"error": "Could not calculate RSI"}
            
            current_rsi = rsi_values[-1]
            
            # Calculate moving averages
            ma_20 = TechnicalIndicators.calculate_moving_average(prices, 20)
            ma_50 = TechnicalIndicators.calculate_moving_average(prices, 50)
            
            analysis = {
                "symbol": symbol,
                "current_price": current_price,
                "rsi": current_rsi,
                "ma_20": ma_20[-1] if ma_20 else 0,
                "ma_50": ma_50[-1] if ma_50 else 0,
                "price_trend": "up" if current_price > ma_20[-1] else "down" if ma_20 else "neutral",
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    def should_buy(self, analysis: Dict) -> bool:
        """Buy when RSI is oversold and price is above MA"""
        if "error" in analysis:
            return False
        
        rsi = analysis.get("rsi", 50)
        price_trend = analysis.get("price_trend", "neutral")
        
        # Buy conditions: RSI oversold and price above MA20
        return (rsi < config.RSI_OVERSOLD and 
                price_trend == "up")
    
    def should_sell(self, analysis: Dict) -> bool:
        """Sell when RSI is overbought"""
        if "error" in analysis:
            return False
        
        rsi = analysis.get("rsi", 50)
        return rsi > config.RSI_OVERBOUGHT

class MovingAverageCrossoverStrategy(TradingStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, kite_client: KiteTradingClient, portfolio_manager: PortfolioManager):
        super().__init__(kite_client, portfolio_manager)
        self.name = "MA Crossover Strategy"
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze symbol using moving average crossover"""
        try:
            historical_data = self.get_historical_data(symbol)
            if not historical_data or len(historical_data) < 60:
                return {"error": "Insufficient data"}
            
            # Extract closing prices
            prices = [float(candle['close']) for candle in historical_data]
            current_price = prices[-1]
            
            # Calculate moving averages
            ma_short = TechnicalIndicators.calculate_moving_average(prices, config.MA_SHORT_PERIOD)
            ma_long = TechnicalIndicators.calculate_moving_average(prices, config.MA_LONG_PERIOD)
            
            if len(ma_short) < 2 or len(ma_long) < 2:
                return {"error": "Could not calculate moving averages"}
            
            # Check for crossover
            current_ma_short = ma_short[-1]
            current_ma_long = ma_long[-1]
            prev_ma_short = ma_short[-2]
            prev_ma_long = ma_long[-2]
            
            # Determine crossover type
            crossover = "none"
            if prev_ma_short <= prev_ma_long and current_ma_short > current_ma_long:
                crossover = "bullish"  # Golden cross
            elif prev_ma_short >= prev_ma_long and current_ma_short < current_ma_long:
                crossover = "bearish"  # Death cross
            
            analysis = {
                "symbol": symbol,
                "current_price": current_price,
                "ma_short": current_ma_short,
                "ma_long": current_ma_long,
                "crossover": crossover,
                "price_above_ma": current_price > current_ma_short,
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    def should_buy(self, analysis: Dict) -> bool:
        """Buy on bullish crossover"""
        if "error" in analysis:
            return False
        
        crossover = analysis.get("crossover", "none")
        price_above_ma = analysis.get("price_above_ma", False)
        
        return crossover == "bullish" and price_above_ma
    
    def should_sell(self, analysis: Dict) -> bool:
        """Sell on bearish crossover"""
        if "error" in analysis:
            return False
        
        crossover = analysis.get("crossover", "none")
        return crossover == "bearish"

class BollingerBandsStrategy(TradingStrategy):
    """Bollinger Bands Strategy"""
    
    def __init__(self, kite_client: KiteTradingClient, portfolio_manager: PortfolioManager):
        super().__init__(kite_client, portfolio_manager)
        self.name = "Bollinger Bands Strategy"
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze symbol using Bollinger Bands"""
        try:
            historical_data = self.get_historical_data(symbol)
            if not historical_data or len(historical_data) < 25:
                return {"error": "Insufficient data"}
            
            # Extract closing prices
            prices = [float(candle['close']) for candle in historical_data]
            current_price = prices[-1]
            
            # Calculate Bollinger Bands
            upper_band, middle_band, lower_band = TechnicalIndicators.calculate_bollinger_bands(prices, 20, 2)
            
            if not upper_band or not middle_band or not lower_band:
                return {"error": "Could not calculate Bollinger Bands"}
            
            current_upper = upper_band[-1]
            current_middle = middle_band[-1]
            current_lower = lower_band[-1]
            
            # Determine position relative to bands
            band_position = "middle"
            if current_price <= current_lower:
                band_position = "lower"
            elif current_price >= current_upper:
                band_position = "upper"
            
            # Calculate band width (volatility measure)
            band_width = (current_upper - current_lower) / current_middle * 100
            
            analysis = {
                "symbol": symbol,
                "current_price": current_price,
                "upper_band": current_upper,
                "middle_band": current_middle,
                "lower_band": current_lower,
                "band_position": band_position,
                "band_width": band_width,
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    def should_buy(self, analysis: Dict) -> bool:
        """Buy when price touches lower band (oversold)"""
        if "error" in analysis:
            return False
        
        band_position = analysis.get("band_position", "middle")
        band_width = analysis.get("band_width", 0)
        
        # Buy when price is at lower band and volatility is reasonable
        return band_position == "lower" and band_width > 2
    
    def should_sell(self, analysis: Dict) -> bool:
        """Sell when price touches upper band (overbought)"""
        if "error" in analysis:
            return False
        
        band_position = analysis.get("band_position", "middle")
        return band_position == "upper"

class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self, kite_client: KiteTradingClient, portfolio_manager: PortfolioManager):
        self.kite_client = kite_client
        self.portfolio_manager = portfolio_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize strategies
        self.strategies = {
            "rsi": RSIStrategy(kite_client, portfolio_manager),
            "ma_crossover": MovingAverageCrossoverStrategy(kite_client, portfolio_manager),
            "bollinger": BollingerBandsStrategy(kite_client, portfolio_manager)
        }
        
        self.active_strategy = "rsi"  # Default strategy
    
    def set_active_strategy(self, strategy_name: str):
        """Set the active trading strategy"""
        if strategy_name in self.strategies:
            self.active_strategy = strategy_name
            self.logger.info(f"Active strategy set to: {strategy_name}")
        else:
            self.logger.error(f"Strategy {strategy_name} not found")
    
    def get_trading_signals(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get trading signals for all symbols"""
        signals = {}
        strategy = self.strategies.get(self.active_strategy)
        
        if not strategy:
            self.logger.error("No active strategy found")
            return signals
        
        for symbol in symbols:
            try:
                analysis = strategy.analyze_symbol(symbol)
                if "error" not in analysis:
                    signals[symbol] = {
                        "analysis": analysis,
                        "should_buy": strategy.should_buy(analysis),
                        "should_sell": strategy.should_sell(analysis),
                        "entry_price": strategy.get_entry_price(analysis),
                        "stop_loss": strategy.get_stop_loss(analysis, analysis.get("current_price", 0)),
                        "take_profit": strategy.get_take_profit(analysis, analysis.get("current_price", 0))
                    }
                else:
                    self.logger.warning(f"Analysis failed for {symbol}: {analysis['error']}")
                    
            except Exception as e:
                self.logger.error(f"Error getting signal for {symbol}: {e}")
        
        return signals
    
    def get_strategy_performance(self) -> Dict:
        """Get performance metrics for all strategies"""
        # This would typically track historical performance
        # For now, return basic info
        return {
            "active_strategy": self.active_strategy,
            "available_strategies": list(self.strategies.keys()),
            "strategy_descriptions": {
                "rsi": "RSI-based mean reversion strategy",
                "ma_crossover": "Moving average crossover strategy",
                "bollinger": "Bollinger Bands mean reversion strategy"
            }
        }
