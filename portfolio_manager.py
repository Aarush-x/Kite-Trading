"""
Portfolio Management Module
Handles portfolio analysis, risk management, and position sizing
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from kite_client import KiteTradingClient
from config import config

class PortfolioManager:
    """Portfolio management and analysis"""
    
    def __init__(self, kite_client: KiteTradingClient):
        self.kite_client = kite_client
        self.logger = logging.getLogger(__name__)
        self.daily_pnl = 0.0
        self.daily_trades = 0
        
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        try:
            positions = self.kite_client.get_positions()
            holdings = self.kite_client.get_holdings()
            margins = self.kite_client.get_margins()
            
            if not all([positions, holdings, margins]):
                return 0.0
            
            # Calculate from holdings (long-term positions)
            holdings_value = 0
            if isinstance(holdings, list):
                holdings_value = sum(
                    float(holding.get('average_price', 0)) * int(holding.get('quantity', 0))
                    for holding in holdings
                )
            elif isinstance(holdings, dict) and 'day' in holdings:
                holdings_value = sum(
                    float(holding.get('average_price', 0)) * int(holding.get('quantity', 0))
                    for holding in holdings.get('day', [])
                )
            
            # Calculate from day positions
            day_positions_value = 0
            if isinstance(positions, dict) and 'day' in positions:
                day_positions_value = sum(
                    float(pos.get('average_price', 0)) * int(pos.get('quantity', 0))
                    for pos in positions.get('day', [])
                )
            
            # Add available cash
            available_cash = float(margins.get('equity', {}).get('available', {}).get('cash', 0))
            
            total_value = holdings_value + day_positions_value + available_cash
            return total_value
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio value: {e}")
            return 0.0
    
    def get_portfolio_analysis(self) -> Dict:
        """Get comprehensive portfolio analysis"""
        try:
            positions = self.kite_client.get_positions()
            holdings = self.kite_client.get_holdings()
            margins = self.kite_client.get_margins()
            
            if not all([positions, holdings, margins]):
                return {}
            
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "total_value": self.get_portfolio_value(),
                "available_cash": float(margins.get('equity', {}).get('available', {}).get('cash', 0)),
                "used_margin": float(margins.get('equity', {}).get('used', {}).get('total', 0)),
                "day_pnl": 0.0,
                "total_pnl": 0.0,
                "positions": {
                    "day": [],
                    "net": []
                },
                "holdings": [],
                "risk_metrics": {}
            }
            
            # Process day positions
            day_positions = positions.get('day', [])
            for pos in day_positions:
                position_data = {
                    "symbol": pos.get('tradingsymbol'),
                    "quantity": int(pos.get('quantity', 0)),
                    "average_price": float(pos.get('average_price', 0)),
                    "current_price": float(pos.get('last_price', 0)),
                    "pnl": float(pos.get('pnl', 0)),
                    "pnl_percentage": float(pos.get('pnl_percentage', 0))
                }
                analysis["positions"]["day"].append(position_data)
                analysis["day_pnl"] += position_data["pnl"]
            
            # Process net positions
            net_positions = positions.get('net', [])
            for pos in net_positions:
                position_data = {
                    "symbol": pos.get('tradingsymbol'),
                    "quantity": int(pos.get('quantity', 0)),
                    "average_price": float(pos.get('average_price', 0)),
                    "current_price": float(pos.get('last_price', 0)),
                    "pnl": float(pos.get('pnl', 0)),
                    "pnl_percentage": float(pos.get('pnl_percentage', 0))
                }
                analysis["positions"]["net"].append(position_data)
                analysis["total_pnl"] += position_data["pnl"]
            
            # Process holdings
            for holding in holdings:
                holding_data = {
                    "symbol": holding.get('tradingsymbol'),
                    "quantity": int(holding.get('quantity', 0)),
                    "average_price": float(holding.get('average_price', 0)),
                    "current_price": float(holding.get('last_price', 0)),
                    "pnl": float(holding.get('pnl', 0)),
                    "pnl_percentage": float(holding.get('pnl_percentage', 0))
                }
                analysis["holdings"].append(holding_data)
            
            # Calculate risk metrics
            analysis["risk_metrics"] = self.calculate_risk_metrics(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in portfolio analysis: {e}")
            return {}
    
    def calculate_risk_metrics(self, portfolio_data: Dict) -> Dict:
        """Calculate portfolio risk metrics"""
        try:
            total_value = portfolio_data.get("total_value", 0)
            day_pnl = portfolio_data.get("day_pnl", 0)
            total_pnl = portfolio_data.get("total_pnl", 0)
            
            # Calculate position sizes and concentration
            positions = portfolio_data.get("positions", {}).get("net", [])
            position_values = []
            
            for pos in positions:
                position_value = abs(pos.get("quantity", 0) * pos.get("current_price", 0))
                position_values.append(position_value)
            
            # Risk metrics
            risk_metrics = {
                "day_pnl_percentage": (day_pnl / total_value * 100) if total_value > 0 else 0,
                "total_pnl_percentage": (total_pnl / total_value * 100) if total_value > 0 else 0,
                "max_position_size": max(position_values) if position_values else 0,
                "max_position_percentage": (max(position_values) / total_value * 100) if total_value > 0 and position_values else 0,
                "position_count": len(positions),
                "concentration_risk": self.calculate_concentration_risk(position_values, total_value)
            }
            
            return risk_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def calculate_concentration_risk(self, position_values: List[float], total_value: float) -> float:
        """Calculate portfolio concentration risk (Herfindahl index)"""
        if not position_values or total_value <= 0:
            return 0.0
        
        # Calculate weights
        weights = [pv / total_value for pv in position_values]
        
        # Calculate Herfindahl index
        herfindahl = sum(w**2 for w in weights)
        
        # Normalize to 0-100 scale
        concentration_risk = herfindahl * 100
        return concentration_risk
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss_price: float, risk_per_trade: float = None) -> int:
        """Calculate optimal position size based on risk management"""
        try:
            if risk_per_trade is None:
                risk_per_trade = config.MAX_PORTFOLIO_RISK
            
            portfolio_value = self.get_portfolio_value()
            if portfolio_value <= 0:
                return 0
            
            # Calculate risk amount
            risk_amount = portfolio_value * risk_per_trade
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss_price)
            if risk_per_share <= 0:
                return 0
            
            # Calculate position size
            position_size = int(risk_amount / risk_per_share)
            
            # Apply maximum position size limit
            max_position_value = config.MAX_POSITION_SIZE
            max_shares = int(max_position_value / entry_price)
            position_size = min(position_size, max_shares)
            
            self.logger.info(f"Calculated position size for {symbol}: {position_size} shares")
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0
    
    def check_risk_limits(self) -> Dict[str, bool]:
        """Check if portfolio is within risk limits"""
        try:
            portfolio_data = self.get_portfolio_analysis()
            risk_metrics = portfolio_data.get("risk_metrics", {})
            
            limits = {
                "daily_loss_limit": True,
                "daily_trade_limit": True,
                "position_size_limit": True,
                "concentration_limit": True
            }
            
            # Check daily loss limit
            day_pnl = portfolio_data.get("day_pnl", 0)
            if day_pnl < -config.MAX_DAILY_LOSS:
                limits["daily_loss_limit"] = False
                self.logger.warning(f"Daily loss limit exceeded: {day_pnl}")
            
            # Check daily trade limit
            if self.daily_trades >= config.MAX_DAILY_TRADES:
                limits["daily_trade_limit"] = False
                self.logger.warning(f"Daily trade limit reached: {self.daily_trades}")
            
            # Check position size limit
            max_position_percentage = risk_metrics.get("max_position_percentage", 0)
            if max_position_percentage > 20:  # Max 20% in single position
                limits["position_size_limit"] = False
                self.logger.warning(f"Position size limit exceeded: {max_position_percentage}%")
            
            # Check concentration risk
            concentration_risk = risk_metrics.get("concentration_risk", 0)
            if concentration_risk > 30:  # Max 30% concentration risk
                limits["concentration_limit"] = False
                self.logger.warning(f"Concentration risk too high: {concentration_risk}%")
            
            return limits
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return {"error": True}
    
    def get_rebalancing_suggestions(self) -> List[Dict]:
        """Get portfolio rebalancing suggestions"""
        try:
            portfolio_data = self.get_portfolio_analysis()
            positions = portfolio_data.get("positions", {}).get("net", [])
            total_value = portfolio_data.get("total_value", 0)
            
            suggestions = []
            
            # Check for over-concentrated positions
            for pos in positions:
                position_value = abs(pos.get("quantity", 0) * pos.get("current_price", 0))
                position_percentage = (position_value / total_value * 100) if total_value > 0 else 0
                
                if position_percentage > 15:  # More than 15% in single position
                    suggestions.append({
                        "type": "reduce_position",
                        "symbol": pos.get("symbol"),
                        "current_percentage": position_percentage,
                        "suggested_percentage": 10,
                        "reason": "Position too concentrated"
                    })
            
            # Check for under-diversification
            if len(positions) < 5:
                suggestions.append({
                    "type": "diversify",
                    "current_positions": len(positions),
                    "suggested_positions": 8,
                    "reason": "Portfolio under-diversified"
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting rebalancing suggestions: {e}")
            return []
    
    def update_daily_stats(self, trade_pnl: float):
        """Update daily trading statistics"""
        self.daily_pnl += trade_pnl
        self.daily_trades += 1
        
        self.logger.info(f"Daily stats updated - PnL: {self.daily_pnl}, Trades: {self.daily_trades}")
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at start of new trading day)"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.logger.info("Daily statistics reset")
