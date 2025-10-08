"""
Simplified Swing Trading Bot - Works with available API permissions
Focuses on portfolio management and basic trading signals
"""

import logging
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from kite_client import KiteTradingClient
from portfolio_manager import PortfolioManager

class SimpleSwingBot:
    """Simplified Swing Trading Bot for your strategy"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.kite_client = KiteTradingClient()
        self.portfolio_manager = PortfolioManager(self.kite_client)
        
        self.is_running = False
        self.daily_trades = 0
        self.monthly_profit = 0.0
        self.start_of_month = datetime.now().replace(day=1)
        
        self.logger.info("Simple Swing Trading Bot initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('simple_swing_bot.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def authenticate(self) -> bool:
        """Authenticate with Kite Connect"""
        self.logger.info("Authenticating with Kite Connect...")
        
        if not config.validate_config():
            self.logger.error("Configuration validation failed")
            return False
        
        success = self.kite_client.authenticate()
        if success:
            self.logger.info("Authentication successful")
            profile = self.kite_client.get_profile()
            if profile:
                self.logger.info(f"Logged in as: {profile.get('user_name', 'Unknown')}")
        else:
            self.logger.error("Authentication failed")
        
        return success
    
    def is_trading_time(self) -> bool:
        """Check if it's trading time (9:30 AM - 1:00 PM US time)"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Use IST market hours but limit to your availability
        if config.MARKET_OPEN_TIME <= current_time <= "13:00":  # 1:00 PM IST
            if now.weekday() < 5:  # Monday = 0, Sunday = 6
                return True
        return False
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        try:
            portfolio_analysis = self.portfolio_manager.get_portfolio_analysis()
            total_value = portfolio_analysis.get('total_value', 0)
            
            # Calculate allocation based on your strategy
            gold_silver_allocation = total_value * config.GOLD_SILVER_ALLOCATION
            equity_allocation = total_value * config.EQUITY_ALLOCATION
            
            summary = {
                "total_value": total_value,
                "day_pnl": portfolio_analysis.get('day_pnl', 0),
                "monthly_profit": self.monthly_profit,
                "gold_silver_allocation": gold_silver_allocation,
                "equity_allocation": equity_allocation,
                "positions": portfolio_analysis.get('positions', {}),
                "holdings": portfolio_analysis.get('holdings', []),
                "daily_trades": self.daily_trades
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def analyze_portfolio_allocation(self, portfolio_summary: Dict):
        """Analyze current portfolio allocation vs target"""
        try:
            total_value = portfolio_summary.get('total_value', 0)
            target_gold_silver = portfolio_summary.get('gold_silver_allocation', 0)
            target_equity = portfolio_summary.get('equity_allocation', 0)
            
            # Get current positions
            positions = portfolio_summary.get('positions', {})
            holdings = portfolio_summary.get('holdings', [])
            
            current_gold_silver_value = 0
            current_equity_value = 0
            
            # Calculate current allocation
            for position in positions.get('net', []):
                symbol = position.get('symbol', '')
                value = abs(position.get('quantity', 0) * position.get('current_price', 0))
                
                if 'GOLDBEES' in symbol or 'SILVERBEES' in symbol:
                    current_gold_silver_value += value
                else:
                    current_equity_value += value
            
            for holding in holdings:
                symbol = holding.get('symbol', '')
                value = abs(holding.get('quantity', 0) * holding.get('current_price', 0))
                
                if 'GOLDBEES' in symbol or 'SILVERBEES' in symbol:
                    current_gold_silver_value += value
                else:
                    current_equity_value += value
            
            # Calculate allocation percentages
            gold_silver_percent = (current_gold_silver_value / total_value * 100) if total_value > 0 else 0
            equity_percent = (current_equity_value / total_value * 100) if total_value > 0 else 0
            
            self.logger.info("📊 Portfolio Allocation Analysis:")
            self.logger.info(f"   Total Value: ₹{total_value:,.2f}")
            self.logger.info(f"   Gold/Silver: ₹{current_gold_silver_value:,.2f} ({gold_silver_percent:.1f}%) - Target: 50%")
            self.logger.info(f"   Equities: ₹{current_equity_value:,.2f} ({equity_percent:.1f}%) - Target: 50%")
            
            # Check if rebalancing is needed
            if abs(gold_silver_percent - 50) > 10:  # More than 10% deviation
                self.logger.info("⚠️ Portfolio rebalancing needed for Gold/Silver allocation")
            
            if abs(equity_percent - 50) > 10:  # More than 10% deviation
                self.logger.info("⚠️ Portfolio rebalancing needed for Equity allocation")
            
            return {
                "current_gold_silver": current_gold_silver_value,
                "current_equity": current_equity_value,
                "target_gold_silver": target_gold_silver,
                "target_equity": target_equity,
                "gold_silver_percent": gold_silver_percent,
                "equity_percent": equity_percent
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio allocation: {e}")
            return {}
    
    def check_profit_booking(self, portfolio_summary: Dict):
        """Check for profit booking opportunities"""
        try:
            positions = portfolio_summary.get('positions', {})
            
            for position in positions.get('net', []):
                symbol = position.get('symbol', '')
                pnl = position.get('pnl', 0)
                pnl_percent = position.get('pnl_percentage', 0)
                
                if pnl_percent >= config.PROFIT_TARGET_PERCENTAGE:
                    self.logger.info(f"🎯 Profit target reached for {symbol}: {pnl_percent:.2f}% (₹{pnl:,.2f})")
                    self.logger.info(f"   Consider booking profits for {symbol}")
                elif pnl_percent <= -config.STOP_LOSS_PERCENTAGE:
                    self.logger.info(f"🛑 Stop loss triggered for {symbol}: {pnl_percent:.2f}% (₹{pnl:,.2f})")
                    self.logger.info(f"   Consider cutting losses for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error checking profit booking: {e}")
    
    def execute_trading_cycle(self):
        """Execute one trading cycle"""
        try:
            self.logger.info("Starting trading cycle...")
            
            # Check if it's trading time
            if not self.is_trading_time():
                self.logger.info("Outside trading hours")
                return
            
            # Get portfolio summary
            portfolio_summary = self.get_portfolio_summary()
            total_value = portfolio_summary.get('total_value', 0)
            
            self.logger.info(f"Portfolio value: ₹{total_value:,.2f}")
            self.logger.info(f"Day PnL: ₹{portfolio_summary.get('day_pnl', 0):,.2f}")
            self.logger.info(f"Monthly profit: ₹{self.monthly_profit:,.2f}")
            
            # Analyze portfolio allocation
            allocation_analysis = self.analyze_portfolio_allocation(portfolio_summary)
            
            # Check for profit booking opportunities
            self.check_profit_booking(portfolio_summary)
            
            # Provide trading suggestions
            self.provide_trading_suggestions(portfolio_summary, allocation_analysis)
            
            self.logger.info("Trading cycle completed")
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
    
    def provide_trading_suggestions(self, portfolio_summary: Dict, allocation_analysis: Dict):
        """Provide trading suggestions based on current portfolio"""
        try:
            total_value = portfolio_summary.get('total_value', 0)
            gold_silver_percent = allocation_analysis.get('gold_silver_percent', 0)
            equity_percent = allocation_analysis.get('equity_percent', 0)
            
            self.logger.info("💡 Trading Suggestions:")
            
            # Gold/Silver allocation suggestions
            if gold_silver_percent < 40:
                self.logger.info(f"   📈 Consider buying more Gold/Silver ETFs (current: {gold_silver_percent:.1f}%)")
                self.logger.info(f"   Suggested: GOLDBEES, SILVERBEES")
            elif gold_silver_percent > 60:
                self.logger.info(f"   📉 Consider reducing Gold/Silver exposure (current: {gold_silver_percent:.1f}%)")
            
            # Equity allocation suggestions
            if equity_percent < 40:
                self.logger.info(f"   📈 Consider buying more equities (current: {equity_percent:.1f}%)")
                self.logger.info(f"   Suggested: RELIANCE, TCS, HDFCBANK, INFY")
            elif equity_percent > 60:
                self.logger.info(f"   📉 Consider reducing equity exposure (current: {equity_percent:.1f}%)")
            
            # Monthly goal tracking
            monthly_profit_percent = (self.monthly_profit / total_value * 100) if total_value > 0 else 0
            if monthly_profit_percent < config.MONTHLY_PROFIT_TARGET:
                remaining_percent = config.MONTHLY_PROFIT_TARGET - monthly_profit_percent
                self.logger.info(f"   🎯 Monthly goal: {monthly_profit_percent:.2f}% (Target: {config.MONTHLY_PROFIT_TARGET}%)")
                self.logger.info(f"   Need {remaining_percent:.2f}% more to reach monthly goal")
            
        except Exception as e:
            self.logger.error(f"Error providing trading suggestions: {e}")
    
    def daily_reset(self):
        """Daily reset routine"""
        self.logger.info("Performing daily reset...")
        self.daily_trades = 0
        self.portfolio_manager.reset_daily_stats()
        self.logger.info("Daily reset completed")
    
    def check_monthly_reset(self):
        """Check if monthly reset is needed"""
        current_month = datetime.now().replace(day=1)
        if current_month > self.start_of_month:
            self.monthly_reset()
    
    def monthly_reset(self):
        """Monthly reset routine"""
        self.logger.info("Performing monthly reset...")
        self.monthly_profit = 0.0
        self.start_of_month = datetime.now().replace(day=1)
        self.logger.info("Monthly reset completed")
    
    def start(self):
        """Start the simple swing trading bot"""
        self.logger.info("Starting Simple Swing Trading Bot...")
        
        # Authenticate
        if not self.authenticate():
            self.logger.error("Failed to authenticate. Exiting.")
            return
        
        self.is_running = True
        
        # Schedule trading cycles (every 30 minutes during trading hours)
        schedule.every(30).minutes.do(self.execute_trading_cycle)
        
        # Schedule daily reset at market open
        schedule.every().day.at("09:00").do(self.daily_reset)
        
        # Schedule monthly reset on 1st of each month at 9:00 AM
        schedule.every().day.at("09:00").do(self.check_monthly_reset)
        
        self.logger.info("Simple swing trading bot started. Press Ctrl+C to stop.")
        self.logger.info(f"Strategy: {config.GOLD_SILVER_ALLOCATION*100}% Gold/Silver, {config.EQUITY_ALLOCATION*100}% Equities")
        self.logger.info(f"Profit Target: {config.PROFIT_TARGET_PERCENTAGE}% per trade")
        self.logger.info(f"Monthly Goal: {config.MONTHLY_PROFIT_TARGET}%")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal. Stopping bot...")
            self.stop()
    
    def stop(self):
        """Stop the simple swing trading bot"""
        self.logger.info("Stopping simple swing trading bot...")
        self.is_running = False
        
        # Log final summary
        portfolio_summary = self.get_portfolio_summary()
        self.logger.info("Final Portfolio Summary:")
        self.logger.info(f"Total Value: ₹{portfolio_summary.get('total_value', 0):,.2f}")
        self.logger.info(f"Monthly Profit: ₹{self.monthly_profit:,.2f}")
        self.logger.info(f"Daily Trades: {self.daily_trades}")
        
        self.logger.info("Simple swing trading bot stopped")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        portfolio_summary = self.get_portfolio_summary()
        
        return {
            "is_running": self.is_running,
            "is_authenticated": self.kite_client.is_authenticated,
            "trading_time": self.is_trading_time(),
            "portfolio_value": portfolio_summary.get('total_value', 0),
            "monthly_profit": self.monthly_profit,
            "daily_trades": self.daily_trades,
            "last_update": datetime.now().isoformat()
        }

def main():
    """Main function"""
    print("🚀 Simple Swing Trading Bot - Gold/Silver + Equities")
    print("=" * 60)
    print(f"Strategy: {config.GOLD_SILVER_ALLOCATION*100}% Gold/Silver ETFs, {config.EQUITY_ALLOCATION*100}% Equities")
    print(f"Profit Target: {config.PROFIT_TARGET_PERCENTAGE}% per trade")
    print(f"Monthly Goal: {config.MONTHLY_PROFIT_TARGET}%")
    print("=" * 60)
    
    # Create and start bot
    bot = SimpleSwingBot()
    
    try:
        bot.start()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
