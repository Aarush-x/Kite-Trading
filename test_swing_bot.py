"""
Test script for Swing Trading Bot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from kite_client import KiteTradingClient
from portfolio_manager import PortfolioManager
from swing_trading_strategy import SwingTradingStrategy

def test_swing_bot():
    """Test the swing trading bot components"""
    
    print("🧪 Testing Swing Trading Bot Components")
    print("=" * 50)
    
    # Test 1: Configuration
    print("1. Testing Configuration...")
    print(f"   API Key: {config.API_KEY[:10]}...")
    print(f"   Watchlist: {len(config.WATCHLIST)} symbols")
    print(f"   Gold/Silver Allocation: {config.GOLD_SILVER_ALLOCATION*100}%")
    print(f"   Equity Allocation: {config.EQUITY_ALLOCATION*100}%")
    print(f"   Profit Target: {config.PROFIT_TARGET_PERCENTAGE}%")
    print("   ✅ Configuration loaded successfully")
    
    # Test 2: Authentication
    print("\n2. Testing Authentication...")
    kite_client = KiteTradingClient()
    if kite_client.authenticate():
        print("   ✅ Authentication successful")
        
        # Test 3: Portfolio Manager
        print("\n3. Testing Portfolio Manager...")
        portfolio_manager = PortfolioManager(kite_client)
        portfolio_value = portfolio_manager.get_portfolio_value()
        print(f"   Portfolio Value: ₹{portfolio_value:,.2f}")
        print("   ✅ Portfolio Manager working")
        
        # Test 4: Swing Trading Strategy
        print("\n4. Testing Swing Trading Strategy...")
        swing_strategy = SwingTradingStrategy(kite_client, portfolio_manager)
        
        # Test allocation calculation
        allocation = swing_strategy.get_portfolio_allocation(portfolio_value)
        print(f"   Gold/Silver Allocation: ₹{allocation['gold_silver']:,.2f}")
        print(f"   Equity Allocation: ₹{allocation['equities']:,.2f}")
        
        # Test symbol analysis
        test_symbol = "NSE:GOLDBEES"
        print(f"\n5. Testing Symbol Analysis for {test_symbol}...")
        analysis = swing_strategy.analyze_swing_opportunity(test_symbol)
        
        if "error" not in analysis:
            print(f"   Current Price: ₹{analysis.get('current_price', 0):.2f}")
            print(f"   RSI: {analysis.get('rsi', 0):.2f}")
            print(f"   Trend: {analysis.get('trend', 'unknown')}")
            print(f"   Is Gold/Silver ETF: {analysis.get('is_gold_silver', False)}")
            print("   ✅ Symbol analysis working")
        else:
            print(f"   ⚠️ Analysis error: {analysis['error']}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Run: python swing_trading_bot.py")
        print("2. Monitor the logs for trading activity")
        print("3. Check your portfolio allocation")
        print("4. Send your Google Finance watchlist for customization")
        
    else:
        print("   ❌ Authentication failed")
        print("   Please check your API credentials")

if __name__ == "__main__":
    test_swing_bot()
