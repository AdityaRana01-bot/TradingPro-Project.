# QUICK START GUIDE - 5 Minutes to First Prediction

## ⚡ Fastest Way to Get Started (NO API KEY NEEDED!)

### Step 1: Install Python (5 minutes)
Download from: https://www.python.org/downloads/
Choose Python 3.8 or higher

### Step 2: Install TA-Lib

**Windows:**
1. Download: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Pick the right file for your Python version
3. Run: `pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl`

**Mac:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux:**
```bash
sudo apt-get install ta-lib
pip install TA-Lib
```

### Step 3: Install Other Dependencies (2 minutes)
```bash
pip install pandas numpy requests scikit-learn yfinance
```

### Step 4: Run Your First Prediction! (1 minute)

```python
from realtime_trading_predictor import RealTimeTradingSystem

# Create system
system = RealTimeTradingSystem()

# Analyze Bitcoin - NO API KEY NEEDED!
system.analyze_and_predict(
    symbol='BTCUSDT',
    market_type='crypto',
    interval='5m'
)
```

### Step 5: Get Results!

You'll see:
- ✅ Current price
- ✅ BUY or SELL prediction
- ✅ Confidence percentage
- ✅ Candlestick patterns detected
- ✅ Technical indicators
- ✅ Risk management suggestions

## 🎯 That's It!

You now have a professional trading prediction system running for FREE!

### Next Steps:
1. Try different crypto symbols: ETHUSDT, BNBUSDT, SOLUSDT
2. Test different time intervals: 1m, 5m, 15m, 1h
3. Practice paper trading with predictions
4. Learn more in COMPREHENSIVE_GUIDE.md

## ⚠️ Important Reminders:
- Start with PAPER TRADING (virtual money)
- Never trade without stop-loss
- Only use regulated platforms (Zerodha, Upstox for India)
- AVOID Olymptrade - it's not SEBI regulated!

## 💰 Free Data Sources Used:
- ✅ Binance API (crypto) - Unlimited free
- ✅ Yahoo Finance - Free
- ✅ Alpha Vantage (stocks) - 25 calls/day free

Happy Trading! 🚀
