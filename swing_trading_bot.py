"""
Swing Trading Bot - Customized for your Gold/Silver + Equity strategy
Optimized for US timezone trading (9:30 AM - 1:00 PM)
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
from swing_trading_strategy import SwingTradingStrategy

class SwingTradingBot:
    """Swing Trading Bot for Gold/Silver ETFs + Equities"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.kite_client = KiteTradingClient()
        self.portfolio_manager = PortfolioManager(self.kite_client)
        self.swing_strategy = SwingTradingStrategy(self.kite_client, self.portfolio_manager)
        
        self.is_running = False
        self.daily_trades = 0
        self.monthly_profit = 0.0
        self.start_of_month = datetime.now().replace(day=1)
        
        self.logger.info("Swing Trading Bot initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('swing_trading_bot.log'),
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
        
        # Convert to IST (add 10.5 hours to US time)
        # For simplicity, we'll use IST market hours but adjust for your availability
        if config.MARKET_OPEN_TIME <= current_time <= "13:00":  # 1:00 PM IST
            if now.weekday() < 5:  # Monday = 0, Sunday = 6
                return True
        return False
    
    def check_risk_limits(self) -> bool:
        """Check if we're within risk limits"""
        risk_limits = self.portfolio_manager.check_risk_limits()
        
        for limit_name, is_ok in risk_limits.items():
            if not is_ok:
                self.logger.warning(f"Risk limit exceeded: {limit_name}")
                return False
        
        return True
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        try:
            portfolio_analysis = self.portfolio_manager.get_portfolio_analysis()
            total_value = portfolio_analysis.get('total_value', 0)
            
            # Calculate allocation
            allocation = self.swing_strategy.get_portfolio_allocation(total_value)
            
            summary = {
                "total_value": total_value,
                "day_pnl": portfolio_analysis.get('day_pnl', 0),
                "monthly_profit": self.monthly_profit,
                "allocation": allocation,
                "positions": portfolio_analysis.get('positions', {}),
                "holdings": portfolio_analysis.get('holdings', []),
                "daily_trades": self.daily_trades
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def execute_swing_trading_cycle(self):
        """Execute one swing trading cycle"""
        try:
            self.logger.info("Starting swing trading cycle...")
            
            # Check if it's trading time
            if not self.is_trading_time():
                self.logger.info("Outside trading hours")
                return
            
            # Check risk limits
            if not self.check_risk_limits():
                self.logger.warning("Risk limits exceeded, skipping trading cycle")
                return
            
            # Get portfolio summary
            portfolio_summary = self.get_portfolio_summary()
            total_value = portfolio_summary.get('total_value', 0)
            
            self.logger.info(f"Portfolio value: ₹{total_value:,.2f}")
            self.logger.info(f"Day PnL: ₹{portfolio_summary.get('day_pnl', 0):,.2f}")
            self.logger.info(f"Monthly profit: ₹{self.monthly_profit:,.2f}")
            
            # Process each symbol in watchlist
            for symbol in config.WATCHLIST:
                try:
                    self.process_symbol(symbol, total_value)
                except Exception as e:
                    self.logger.error(f"Error processing {symbol}: {e}")
            
            # Check for profit booking opportunities
            self.check_profit_booking()
            
            self.logger.info("Swing trading cycle completed")
            
        except Exception as e:
            self.logger.error(f"Error in swing trading cycle: {e}")
    
    def process_symbol(self, symbol: str, total_portfolio_value: float):
        """Process a single symbol for swing trading"""
        try:
            # Analyze the symbol
            analysis = self.swing_strategy.analyze_swing_opportunity(symbol)
            if "error" in analysis:
                self.logger.warning(f"Analysis failed for {symbol}: {analysis['error']}")
                return
            
            current_price = analysis.get('current_price', 0)
            is_gold_silver = self.swing_strategy.is_gold_silver_etf(symbol)
            
            # Check if we already have a position
            existing_position = self.get_existing_position(symbol)
            
            if existing_position:
                # Check if we should sell
                if self.swing_strategy.should_sell(analysis, existing_position['average_price']):
                    self.execute_sell_order(symbol, existing_position)
            else:
                # Check if we should buy
                if self.swing_strategy.should_buy(analysis):
                    self.execute_buy_order(symbol, analysis, total_portfolio_value)
            
        except Exception as e:
            self.logger.error(f"Error processing symbol {symbol}: {e}")
    
    def get_existing_position(self, symbol: str) -> Optional[Dict]:
        """Get existing position for a symbol"""
        try:
            positions = self.kite_client.get_positions()
            if not positions or not positions.get('day'):
                return None
            
            for position in positions['day']:
                if position.get('tradingsymbol') == symbol.replace('NSE:', ''):
                    return {
                        'quantity': int(position.get('quantity', 0)),
                        'average_price': float(position.get('average_price', 0)),
                        'current_price': float(position.get('last_price', 0)),
                        'pnl': float(position.get('pnl', 0))
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting existing position for {symbol}: {e}")
            return None
    
    def execute_buy_order(self, symbol: str, analysis: Dict, total_portfolio_value: float):
        """Execute buy order"""
        try:
            current_price = analysis.get('current_price', 0)
            
            # Calculate position size
            position_size = self.swing_strategy.get_position_size(
                symbol, current_price, total_portfolio_value
            )
            
            if position_size <= 0:
                self.logger.info(f"Position size too small for {symbol}")
                return
            
            # Place buy order
            self.logger.info(f"Placing buy order for {symbol}: {position_size} shares at ₹{current_price}")
            
            order_id = self.kite_client.place_order(
                variety="regular",
                exchange="NSE",
                tradingsymbol=symbol.replace('NSE:', ''),
                transaction_type="BUY",
                quantity=position_size,
                product="CNC",  # Cash and Carry
                order_type="MARKET"
            )
            
            if order_id:
                self.logger.info(f"Buy order placed successfully: {order_id}")
                self.swing_strategy.track_position(symbol, current_price, position_size)
                self.daily_trades += 1
                
                # Log strategy details
                if self.swing_strategy.is_gold_silver_etf(symbol):
                    self.logger.info(f"Gold/Silver ETF position opened: {symbol}")
                else:
                    self.logger.info(f"Equity swing position opened: {symbol}")
            else:
                self.logger.error(f"Failed to place buy order for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error executing buy order for {symbol}: {e}")
    
    def execute_sell_order(self, symbol: str, position: Dict):
        """Execute sell order"""
        try:
            quantity = position['quantity']
            current_price = position['current_price']
            pnl = position['pnl']
            
            # Place sell order
            self.logger.info(f"Placing sell order for {symbol}: {quantity} shares at ₹{current_price}")
            self.logger.info(f"Expected PnL: ₹{pnl:,.2f}")
            
            order_id = self.kite_client.place_order(
                variety="regular",
                exchange="NSE",
                tradingsymbol=symbol.replace('NSE:', ''),
                transaction_type="SELL",
                quantity=quantity,
                product="CNC",
                order_type="MARKET"
            )
            
            if order_id:
                self.logger.info(f"Sell order placed successfully: {order_id}")
                self.swing_strategy.remove_position(symbol)
                self.daily_trades += 1
                self.monthly_profit += pnl
                
                # Log profit booking
                if pnl > 0:
                    profit_percent = (pnl / (position['average_price'] * quantity)) * 100
                    self.logger.info(f"✅ Profit booked: {profit_percent:.2f}% (₹{pnl:,.2f})")
                else:
                    self.logger.info(f"❌ Loss booked: ₹{pnl:,.2f}")
            else:
                self.logger.error(f"Failed to place sell order for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error executing sell order for {symbol}: {e}")
    
    def check_profit_booking(self):
        """Check for profit booking opportunities"""
        try:
            positions = self.kite_client.get_positions()
            if not positions or not positions.get('day'):
                return
            
            for position in positions['day']:
                symbol = f"NSE:{position.get('tradingsymbol')}"
                quantity = int(position.get('quantity', 0))
                average_price = float(position.get('average_price', 0))
                current_price = float(position.get('last_price', 0))
                pnl = float(position.get('pnl', 0))
                
                if quantity <= 0:
                    continue
                
                # Calculate profit percentage
                profit_percent = (current_price - average_price) / average_price * 100
                
                # Check if profit target is reached
                if profit_percent >= config.PROFIT_TARGET_PERCENTAGE:
                    self.logger.info(f"🎯 Profit target reached for {symbol}: {profit_percent:.2f}%")
                    self.execute_sell_order(symbol, {
                        'quantity': quantity,
                        'average_price': average_price,
                        'current_price': current_price,
                        'pnl': pnl
                    })
                
        except Exception as e:
            self.logger.error(f"Error checking profit booking: {e}")
    
    def daily_reset(self):
        """Daily reset routine"""
        self.logger.info("Performing daily reset...")
        self.daily_trades = 0
        self.portfolio_manager.reset_daily_stats()
        self.logger.info("Daily reset completed")
    
    def monthly_reset(self):
        """Monthly reset routine"""
        self.logger.info("Performing monthly reset...")
        self.monthly_profit = 0.0
        self.start_of_month = datetime.now().replace(day=1)
        self.logger.info("Monthly reset completed")
    
    def start(self):
        """Start the swing trading bot"""
        self.logger.info("Starting Swing Trading Bot...")
        
        # Authenticate
        if not self.authenticate():
            self.logger.error("Failed to authenticate. Exiting.")
            return
        
        self.is_running = True
        
        # Schedule trading cycles (every 15 minutes during trading hours)
        schedule.every(15).minutes.do(self.execute_swing_trading_cycle)
        
        # Schedule daily reset at market open
        schedule.every().day.at("09:00").do(self.daily_reset)
        
        # Schedule monthly reset on 1st of each month
        schedule.every().month.do(self.monthly_reset)
        
        self.logger.info("Swing trading bot started. Press Ctrl+C to stop.")
        self.logger.info(f"Trading strategy: {config.GOLD_SILVER_ALLOCATION*100}% Gold/Silver, {config.EQUITY_ALLOCATION*100}% Equities")
        self.logger.info(f"Profit target: {config.PROFIT_TARGET_PERCENTAGE}% per trade")
        self.logger.info(f"Monthly goal: {config.MONTHLY_PROFIT_TARGET}%")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal. Stopping bot...")
            self.stop()
    
    def stop(self):
        """Stop the swing trading bot"""
        self.logger.info("Stopping swing trading bot...")
        self.is_running = False
        
        # Log final summary
        portfolio_summary = self.get_portfolio_summary()
        self.logger.info("Final Portfolio Summary:")
        self.logger.info(f"Total Value: ₹{portfolio_summary.get('total_value', 0):,.2f}")
        self.logger.info(f"Monthly Profit: ₹{self.monthly_profit:,.2f}")
        self.logger.info(f"Daily Trades: {self.daily_trades}")
        
        self.logger.info("Swing trading bot stopped")
    
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
            "allocation": portfolio_summary.get('allocation', {}),
            "last_update": datetime.now().isoformat()
        }

def main():
    """Main function"""
    print("🚀 Swing Trading Bot - Gold/Silver + Equities")
    print("=" * 60)
    print(f"Strategy: {config.GOLD_SILVER_ALLOCATION*100}% Gold/Silver ETFs, {config.EQUITY_ALLOCATION*100}% Equities")
    print(f"Profit Target: {config.PROFIT_TARGET_PERCENTAGE}% per trade")
    print(f"Monthly Goal: {config.MONTHLY_PROFIT_TARGET}%")
    print("=" * 60)
    
    # Create and start bot
    bot = SwingTradingBot()
    
    try:
        bot.start()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()

