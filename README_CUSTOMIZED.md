# Your Customized Swing Trading Bot

##  **Setup Complete!**

Your trading bot is now fully configured with your specific strategy:

### **Your Trading Strategy:**
- **50% Gold/Silver ETFs**: Nippon Goldbees & Silverbees
- **50% Equities**: Swing trading for 8-9% profit targets
- **Monthly Goal**: 7% profit
- **Trading Window**: 9:30 AM - 1:00 PM (US time)
- **Strategy**: Swing trading with profit booking

### **Current Portfolio:**
- **Total Value**: ₹12,346.20
- **Gold/Silver Allocation**: ₹6,173.10 (50%)
- **Equity Allocation**: ₹6,173.10 (50%)

##  **How to Use Your Bot:**

### **1. Run the Simple Swing Bot:**
```bash
cd /Users/aarushmuralinathan/Documents/GitHub/Kite-Trading
source venv/bin/activate
python simple_swing_bot.py
```

### **2. What the Bot Does:**
- **Monitors your portfolio** every 30 minutes during trading hours
- **Analyzes allocation** between Gold/Silver ETFs and Equities
- **Tracks profit targets** (8.5% per trade)
- **Provides trading suggestions** based on your strategy
- **Monitors monthly goals** (7% monthly profit target)
- **Logs all activities** to `simple_swing_bot.log`

### **3. Key Features:**
- ✅ **Portfolio Allocation Tracking**: Ensures 50/50 split
- ✅ **Profit Target Monitoring**: Alerts when 8.5% profit is reached
- ✅ **Monthly Goal Tracking**: Tracks progress toward 7% monthly goal
- ✅ **Trading Suggestions**: Provides buy/sell recommendations
- ✅ **Risk Management**: Built-in stop-loss and position sizing
- ✅ **US Timezone Compatible**: Works with your 9:30 AM - 1:00 PM schedule

##  **Current Watchlist:**

### **Gold/Silver ETFs (50% allocation):**
- `NSE:GOLDBEES` - Nippon Goldbees
- `NSE:SILVERBEES` - Nippon Silverbees

### **Equities (50% allocation):**
- `NSE:RELIANCE`
- `NSE:TCS`
- `NSE:HDFCBANK`
- `NSE:INFY`
- `NSE:HINDUNILVR`
- `NSE:ITC`
- `NSE:KOTAKBANK`
- `NSE:LT`
- `NSE:SBIN`
- `NSE:BHARTIARTL`

##  **Customization Options:**

### **Update Your Watchlist:**
When you send your Google Finance watchlist, I can update the `WATCHLIST` in `config.py` with your preferred stocks.

### **Adjust Parameters:**
Edit `config.py` to modify:
```python
PROFIT_TARGET_PERCENTAGE = 8.5  # Your 8-9% target
MONTHLY_PROFIT_TARGET = 7.0     # Your monthly goal
GOLD_SILVER_ALLOCATION = 0.50   # 50% allocation
EQUITY_ALLOCATION = 0.50        # 50% allocation
```

##  **Bot Output Example:**

```
 Simple Swing Trading Bot - Gold/Silver + Equities
============================================================
Strategy: 50.0% Gold/Silver ETFs, 50.0% Equities
Profit Target: 8.5% per trade
Monthly Goal: 7.0%
============================================================

 Portfolio Allocation Analysis:
   Total Value: ₹12,346.20
   Gold/Silver: ₹6,173.10 (50.0%) - Target: 50%
   Equities: ₹6,173.10 (50.0%) - Target: 50%

 Trading Suggestions:
   📈 Consider buying more Gold/Silver ETFs (current: 45.0%)
   Suggested: GOLDBEES, SILVERBEES

 Monthly goal: 2.5% (Target: 7.0%)
   Need 4.5% more to reach monthly goal
```

##  **Risk Management:**

- **Maximum Position Size**: ₹100,000 per position
- **Daily Loss Limit**: ₹5,000
- **Stop Loss**: 2% per trade
- **Take Profit**: 8.5% per trade
- **Daily Trade Limit**: 10 trades

##  **Logs and Monitoring:**

- **Main Log**: `simple_swing_bot.log`
- **Trading Activity**: All trades and suggestions logged
- **Portfolio Tracking**: Real-time allocation monitoring
- **Performance Metrics**: Monthly and daily profit tracking

##  **Next Steps:**

1. **Run the bot** and monitor the logs
2. **Send your Google Finance watchlist** for customization
3. **Adjust parameters** in `config.py` as needed
4. **Monitor performance** and adjust strategy

## ⚠️ **Important Notes:**

- **Paper Trading First**: Test with small amounts
- **Monitor Regularly**: Check logs and portfolio
- **Market Hours**: Bot only runs during market hours
- **API Limits**: Respects Kite Connect rate limits

##  **Support:**

The bot is designed to work with your US schedule and will:
- Run automatically during Indian market hours
- Provide suggestions when you're available
- Track your monthly 7% profit goal
- Maintain your 50/50 Gold/Silver + Equity allocation

**Your trading bot is ready! **
