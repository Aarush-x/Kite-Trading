# Kite Trading Bot

An automated trading and portfolio management system built for Zerodha Kite Connect API. This bot helps you automate your trading strategies while maintaining proper risk management and portfolio diversification.

## Features

- **Automated Trading**: Execute trades based on technical analysis strategies
- **Portfolio Management**: Monitor and manage your portfolio with risk controls
- **Multiple Strategies**: RSI, Moving Average Crossover, and Bollinger Bands strategies
- **Risk Management**: Built-in position sizing, stop-loss, and daily loss limits
- **Real-time Monitoring**: Live portfolio tracking and performance metrics
- **Scheduled Trading**: Automated trading cycles during market hours
- **Comprehensive Logging**: Detailed logs for all trading activities

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kite-trading-bot.git
   cd kite-trading-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API credentials**
   - Copy `env_example.txt` to `.env`
   - Update the configuration in `config.py` with your Kite Connect credentials:
     ```python
     API_KEY = "your_actual_api_key"
     API_SECRET = "your_actual_api_secret" 
     ACCESS_TOKEN = "your_actual_access_token"
     ```

##  Getting Your Kite Connect Credentials

1. **API Key & Secret**: Get these from your [Kite Connect app settings](https://kite.trade/apps/)
2. **Access Token**: 
   - Use the login flow to get your access token
   - Or use the `get_access_token.py` script (create this if needed)

##  Quick Start

1. **Update your credentials** in `config.py`
2. **Run the bot**:
   ```bash
   python main.py
   ```

The bot will:
- Authenticate with Kite Connect
- Start monitoring your watchlist
- Execute trades based on the selected strategy
- Log all activities to `trading_bot.log`

##  Trading Strategies

### 1. RSI Strategy
- **Buy Signal**: RSI < 30 (oversold) and price above 20-day MA
- **Sell Signal**: RSI > 70 (overbought)

### 2. Moving Average Crossover
- **Buy Signal**: 20-day MA crosses above 50-day MA (Golden Cross)
- **Sell Signal**: 20-day MA crosses below 50-day MA (Death Cross)

### 3. Bollinger Bands
- **Buy Signal**: Price touches lower band (oversold)
- **Sell Signal**: Price touches upper band (overbought)

## Configuration

Edit `config.py` to customize:

```python
# Risk Management
MAX_POSITION_SIZE = 100000  # Max amount per position (INR)
MAX_DAILY_LOSS = 5000       # Max daily loss limit (INR)
STOP_LOSS_PERCENTAGE = 2.0  # Stop loss percentage
TAKE_PROFIT_PERCENTAGE = 3.0 # Take profit percentage

# Watchlist
WATCHLIST = [
    "NSE:RELIANCE",
    "NSE:TCS",
    "NSE:HDFCBANK",
    # Add more symbols
]
```

## Portfolio Management

The bot includes comprehensive portfolio management features:

- **Position Sizing**: Automatic calculation based on risk parameters
- **Risk Limits**: Daily loss limits and position size limits
- **Rebalancing**: Suggestions for portfolio rebalancing
- **Performance Tracking**: Real-time P&L and performance metrics

## Risk Management

Built-in risk controls:

- ✅ Maximum position size limits
- ✅ Daily loss limits
- ✅ Stop-loss orders
- ✅ Take-profit targets
- ✅ Portfolio concentration limits
- ✅ Daily trade limits

##  Logging

All activities are logged to `trading_bot.log`:

```
2024-01-15 09:30:00 - INFO - Trading cycle started
2024-01-15 09:30:01 - INFO - Portfolio value: ₹1,25,000.00
2024-01-15 09:30:02 - INFO - Buy signal detected for NSE:RELIANCE
2024-01-15 09:30:03 - INFO - Order placed: BUY 10 RELIANCE @ ₹2,450
```

##  Advanced Usage

### Custom Strategies

Create your own trading strategy by extending the `TradingStrategy` class:

```python
class MyCustomStrategy(TradingStrategy):
    def analyze_symbol(self, symbol: str) -> Dict:
        # Your analysis logic
        pass
    
    def should_buy(self, analysis: Dict) -> bool:
        # Your buy conditions
        pass
    
    def should_sell(self, analysis: Dict) -> bool:
        # Your sell conditions
        pass
```

### Strategy Selection

Change the active strategy in `main.py`:

```python
# In the StrategyManager initialization
self.strategy_manager.set_active_strategy("ma_crossover")  # or "rsi", "bollinger"
```

## ⚠️ Important Notes

1. **Paper Trading First**: Test with small amounts before using real money
2. **Market Hours**: Bot only trades during market hours (9:15 AM - 3:30 PM IST)
3. **Risk Management**: Always set appropriate risk limits
4. **Monitoring**: Keep an eye on the bot's performance and logs
5. **API Limits**: Be aware of Kite Connect API rate limits

##  Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your API credentials in `config.py`
   - Ensure your access token is valid

2. **No Trades Executed**
   - Check if market is open
   - Verify your watchlist symbols
   - Check risk limits

3. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This software is for educational purposes only. Trading involves risk, and you should never trade with money you cannot afford to lose. The authors are not responsible for any financial losses.

## Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Happy Trading! 📈**
