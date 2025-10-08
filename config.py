"""
Configuration file for Kite Trading Bot
Store your API credentials and trading parameters here
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for trading bot"""
    
    # Kite Connect API Credentials
    # Replace these with your actual credentials
    API_KEY = "dg1evjfyy5yikx3w"  # Your Kite Connect API Key
    API_SECRET = "vibdux7arbve6yix1qmgfqmminno82py"  # Your Kite Connect API Secret
    ACCESS_TOKEN = "6vOWMSWtzM7J1MpGqCk4kiZYFGz1lRBX"  # Your access token (obtained after login)
    
    # Trading Parameters
    MAX_POSITION_SIZE = 100000  # Maximum amount to invest in a single position (in INR)
    MAX_DAILY_LOSS = 5000  # Maximum daily loss limit (in INR)
    MAX_DAILY_TRADES = 10  # Maximum number of trades per day
    
    # Risk Management
    STOP_LOSS_PERCENTAGE = 2.0  # Stop loss percentage
    TAKE_PROFIT_PERCENTAGE = 3.0  # Take profit percentage
    MAX_PORTFOLIO_RISK = 0.02  # Maximum 2% of portfolio at risk per trade
    
    # Trading Hours (IST)
    MARKET_OPEN_TIME = "09:15"
    MARKET_CLOSE_TIME = "15:30"
    
    # Instruments to trade (NSE symbols) - Customized for your strategy
    WATCHLIST = [
        # Gold & Silver ETFs (50% allocation)
        "NSE:GOLDBEES",      # Nippon Goldbees
        "NSE:SILVERBEES",    # Nippon Silverbees
        
        # Equities for swing trading (50% allocation)
        "NSE:RELIANCE",
        "NSE:TCS", 
        "NSE:HDFCBANK",
        "NSE:INFY",
        "NSE:HINDUNILVR",
        "NSE:ITC",
        "NSE:KOTAKBANK",
        "NSE:LT",
        "NSE:SBIN",
        "NSE:BHARTIARTL"
    ]
    
    # Portfolio allocation strategy
    GOLD_SILVER_ALLOCATION = 0.50  # 50% in gold/silver ETFs
    EQUITY_ALLOCATION = 0.50       # 50% in equities
    
    # Swing trading parameters
    PROFIT_TARGET_PERCENTAGE = 8.5  # Target 8-9% profit
    MONTHLY_PROFIT_TARGET = 7.0     # Monthly goal 7%
    SWING_HOLDING_PERIOD_DAYS = 5   # Typical swing trade duration
    
    # Technical Analysis Parameters
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    MA_SHORT_PERIOD = 20
    MA_LONG_PERIOD = 50
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "trading_bot.log"
    
    @classmethod
    def get_kite_credentials(cls) -> Dict[str, str]:
        """Get Kite Connect credentials"""
        return {
            "api_key": cls.API_KEY,
            "api_secret": cls.API_SECRET,
            "access_token": cls.ACCESS_TOKEN
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration"""
        if not cls.API_KEY or cls.API_KEY == "your_api_key_here":
            print("⚠️  Please update your API_KEY in config.py")
            return False
        if not cls.API_SECRET or cls.API_SECRET == "your_api_secret_here":
            print("⚠️  Please update your API_SECRET in config.py")
            return False
        if not cls.ACCESS_TOKEN or cls.ACCESS_TOKEN == "your_access_token_here":
            print("⚠️  Please update your ACCESS_TOKEN in config.py")
            return False
        return True

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    LOG_LEVEL = "DEBUG"
    MAX_DAILY_TRADES = 5  # Reduced for testing

class ProductionConfig(Config):
    """Production environment configuration"""
    LOG_LEVEL = "INFO"
    MAX_DAILY_TRADES = 20

# Select configuration based on environment
config = DevelopmentConfig() if os.getenv('ENV') == 'development' else ProductionConfig()
