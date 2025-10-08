"""
Kite Trading Bot - Main Application
Automated trading and portfolio management system
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
from trading_strategies import StrategyManager

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.kite_client = KiteTradingClient()
        self.portfolio_manager = PortfolioManager(self.kite_client)
        self.strategy_manager = StrategyManager(self.kite_client, self.portfolio_manager)
        
        self.is_running = False
        self.last_trade_time = None
        
        self.logger.info("Trading Bot initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
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
            # Get and log user profile
            profile = self.kite_client.get_profile()
            if profile:
                self.logger.info(f"Logged in as: {profile.get('user_name', 'Unknown')}")
        else:
            self.logger.error("Authentication failed")
        
        return success
    
    def check_market_hours(self) -> bool:
        """Check if market is open"""
        if not self.kite_client.is_market_open():
            self.logger.info("Market is closed")
            return False
        return True
    
    def check_risk_limits(self) -> bool:
        """Check if we're within risk limits"""
        risk_limits = self.portfolio_manager.check_risk_limits()
        
        for limit_name, is_ok in risk_limits.items():
            if not is_ok:
                self.logger.warning(f"Risk limit exceeded: {limit_name}")
                return False
        
        return True
    
    def execute_trading_cycle(self):
        """Execute one trading cycle"""
        try:
            self.logger.info("Starting trading cycle...")
            
            # Check if market is open
            if not self.check_market_hours():
                return
            
            # Check risk limits
            if not self.check_risk_limits():
                self.logger.warning("Risk limits exceeded, skipping trading cycle")
                return
            
            # Get current portfolio analysis
            portfolio_analysis = self.portfolio_manager.get_portfolio_analysis()
            self.logger.info(f"Portfolio value: ₹{portfolio_analysis.get('total_value', 0):,.2f}")
            self.logger.info(f"Day PnL: ₹{portfolio_analysis.get('day_pnl', 0):,.2f}")
            
            # Get trading signals
            signals = self.strategy_manager.get_trading_signals(config.WATCHLIST)
            
            # Process buy signals
            self.process_buy_signals(signals)
            
            # Process sell signals
            self.process_sell_signals(signals)
            
            # Check for rebalancing opportunities
            self.check_rebalancing()
            
            self.logger.info("Trading cycle completed")
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
    
    def process_buy_signals(self, signals: Dict):
        """Process buy signals"""
        for symbol, signal_data in signals.items():
            if not signal_data.get('should_buy', False):
                continue
            
            try:
                analysis = signal_data['analysis']
                entry_price = signal_data['entry_price']
                stop_loss = signal_data['stop_loss']
                
                # Calculate position size
                position_size = self.portfolio_manager.calculate_position_size(
                    symbol, entry_price, stop_loss
                )
                
                if position_size <= 0:
                    self.logger.info(f"Position size too small for {symbol}")
                    continue
                
                # Check if we already have a position
                positions = self.kite_client.get_positions()
                existing_position = None
                
                if positions and positions.get('day'):
                    for pos in positions['day']:
                        if pos.get('tradingsymbol') == symbol.replace('NSE:', ''):
                            existing_position = pos
                            break
                
                if existing_position:
                    self.logger.info(f"Already have position in {symbol}")
                    continue
                
                # Place buy order
                self.logger.info(f"Placing buy order for {symbol}: {position_size} shares at ₹{entry_price}")
                
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
                    self.portfolio_manager.update_daily_stats(0)  # Update trade count
                else:
                    self.logger.error(f"Failed to place buy order for {symbol}")
                
            except Exception as e:
                self.logger.error(f"Error processing buy signal for {symbol}: {e}")
    
    def process_sell_signals(self, signals: Dict):
        """Process sell signals"""
        try:
            positions = self.kite_client.get_positions()
            if not positions or not positions.get('day'):
                return
            
            for position in positions['day']:
                symbol = f"NSE:{position.get('tradingsymbol')}"
                quantity = int(position.get('quantity', 0))
                
                if quantity <= 0:
                    continue
                
                # Check if we have a sell signal for this position
                if symbol not in signals:
                    continue
                
                signal_data = signals[symbol]
                if not signal_data.get('should_sell', False):
                    continue
                
                # Place sell order
                self.logger.info(f"Placing sell order for {symbol}: {quantity} shares")
                
                order_id = self.kite_client.place_order(
                    variety="regular",
                    exchange="NSE",
                    tradingsymbol=position.get('tradingsymbol'),
                    transaction_type="SELL",
                    quantity=quantity,
                    product="CNC",
                    order_type="MARKET"
                )
                
                if order_id:
                    self.logger.info(f"Sell order placed successfully: {order_id}")
                    self.portfolio_manager.update_daily_stats(0)  # Update trade count
                else:
                    self.logger.error(f"Failed to place sell order for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error processing sell signals: {e}")
    
    def check_rebalancing(self):
        """Check for portfolio rebalancing opportunities"""
        try:
            suggestions = self.portfolio_manager.get_rebalancing_suggestions()
            
            if suggestions:
                self.logger.info("Portfolio rebalancing suggestions:")
                for suggestion in suggestions:
                    self.logger.info(f"  - {suggestion}")
            
        except Exception as e:
            self.logger.error(f"Error checking rebalancing: {e}")
    
    def daily_reset(self):
        """Daily reset routine"""
        self.logger.info("Performing daily reset...")
        self.portfolio_manager.reset_daily_stats()
        self.logger.info("Daily reset completed")
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("Starting Kite Trading Bot...")
        
        # Authenticate
        if not self.authenticate():
            self.logger.error("Failed to authenticate. Exiting.")
            return
        
        self.is_running = True
        
        # Schedule trading cycles
        schedule.every(5).minutes.do(self.execute_trading_cycle)
        
        # Schedule daily reset at market open
        schedule.every().day.at("09:00").do(self.daily_reset)
        
        self.logger.info("Trading bot started. Press Ctrl+C to stop.")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal. Stopping bot...")
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Cancel any pending orders (optional)
        try:
            orders = self.kite_client.get_orders()
            if orders:
                for order in orders:
                    if order.get('status') in ['OPEN', 'TRIGGER PENDING']:
                        self.logger.info(f"Cancelling order: {order.get('order_id')}")
                        self.kite_client.cancel_order(order.get('order_id'))
        except Exception as e:
            self.logger.error(f"Error cancelling orders: {e}")
        
        self.logger.info("Trading bot stopped")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        portfolio_analysis = self.portfolio_manager.get_portfolio_analysis()
        strategy_performance = self.strategy_manager.get_strategy_performance()
        
        return {
            "is_running": self.is_running,
            "is_authenticated": self.kite_client.is_authenticated,
            "market_open": self.kite_client.is_market_open(),
            "portfolio_value": portfolio_analysis.get('total_value', 0),
            "day_pnl": portfolio_analysis.get('day_pnl', 0),
            "active_strategy": strategy_performance.get('active_strategy'),
            "last_update": datetime.now().isoformat()
        }

def main():
    """Main function"""
    print("🚀 Kite Trading Bot")
    print("=" * 50)
    
    # Create and start bot
    bot = TradingBot()
    
    try:
        bot.start()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
