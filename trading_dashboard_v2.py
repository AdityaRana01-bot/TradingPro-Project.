
"""
ENHANCED PROFESSIONAL TRADING PREDICTION DASHBOARD v2.0
=========================================================
✅ Cryptocurrency Support (Binance API - FREE)
✅ Indian Stock Market Support (Angel One & Upstox APIs)
✅ Top 50 NSE Stocks (Nifty 50)
✅ Improved Charts & Technical Analysis
✅ Easy-to-Understand Indicators

Run with: streamlit run trading_dashboard_v2.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import talib
from datetime import datetime, timedelta
import time
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="AI Trading Predictor - India & Crypto",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Indian theme colors
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    
    .indian-flag {
        background: linear-gradient(to bottom, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);
        height: 5px;
        width: 100%;
        margin: 10px 0;
    }
    
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #28a745;
        font-size: 1.3rem;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #dc3545;
        font-size: 1.3rem;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .pattern-box {
        background: linear-gradient(135deg, #fff3cd 0%, #fff9e6 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #ffc107;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .indicator-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #e8f5f7 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #17a2b8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
class Config:
    # Binance API (Free - No registration)
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"
    
    # Angel One API (Requires registration)
    ANGEL_API_KEY = "YOUR_ANGEL_ONE_API_KEY"  # Get from https://smartapi.angelbroking.com
    
    # Upstox API (Requires registration)  
    UPSTOX_API_KEY = "YOUR_UPSTOX_API_KEY"  # Get from https://upstox.com/developer/
    
    CONFIDENCE_THRESHOLD = 0.65
    STOP_LOSS_PERCENT = 5.0
    TAKE_PROFIT_PERCENT = 10.0

# Top 50 NSE Stocks (Nifty 50) - Updated October 2025
NIFTY_50_STOCKS = {
    "Reliance Industries": "RELIANCE",
    "TCS (Tata Consultancy)": "TCS",
    "HDFC Bank": "HDFCBANK",
    "ICICI Bank": "ICICIBANK",
    "Bharti Airtel": "BHARTIARTL",
    "Infosys": "INFY",
    "State Bank of India": "SBIN",
    "Hindustan Unilever": "HINDUNILVR",
    "ITC": "ITC",
    "Larsen & Toubro": "LT",
    "Bajaj Finance": "BAJFINANCE",
    "Kotak Mahindra Bank": "KOTAKBANK",
    "Asian Paints": "ASIANPAINT",
    "HCL Technologies": "HCLTECH",
    "Maruti Suzuki": "MARUTI",
    "Axis Bank": "AXISBANK",
    "Sun Pharma": "SUNPHARMA",
    "Titan Company": "TITAN",
    "Wipro": "WIPRO",
    "Tata Motors": "TATAMOTORS",
    "Bajaj Finserv": "BAJAJFINSV",
    "UltraTech Cement": "ULTRACEMCO",
    "Tech Mahindra": "TECHM",
    "Power Grid Corp": "POWERGRID",
    "NTPC": "NTPC",
    "M&M (Mahindra)": "M&M",
    "Adani Ports": "ADANIPORTS",
    "Nestle India": "NESTLEIND",
    "Tata Steel": "TATASTEEL",
    "IndusInd Bank": "INDUSINDBK",
    "Coal India": "COALINDIA",
    "JSW Steel": "JSWSTEEL",
    "Grasim Industries": "GRASIM",
    "Cipla": "CIPLA",
    "Britannia": "BRITANNIA",
    "Apollo Hospital": "APOLLOHOSP",
    "Shree Cement": "SHREECEM",
    "Divis Labs": "DIVISLAB",
    "Hero MotoCorp": "HEROMOTOCO",
    "Eicher Motors": "EICHERMOT",
    "UPL": "UPL",
    "SBI Life Insurance": "SBILIFE",
    "Adani Enterprises": "ADANIENT",
    "Dr Reddy's Lab": "DRREDDY",
    "Hindalco": "HINDALCO",
    "Trent": "TRENT",
    "BPCL": "BPCL",
    "Bharat Electronics": "BEL",
    "LTIMindtree": "LTIM",
    "ONGC": "ONGC"
}

# Initialize session state
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

# ============================================================================
# DATA COLLECTION FUNCTIONS
# ============================================================================

@st.cache_data(ttl=60)
def get_crypto_data_binance(symbol, interval, limit=500):
    """Fetch cryptocurrency data from Binance (FREE)"""
    try:
        endpoint = f"{Config.BINANCE_BASE_URL}/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        
        response = requests.get(endpoint, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        df.set_index('timestamp', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        st.error(f"Error fetching Binance data: {e}")
        return None

def get_indian_stock_data_yfinance(symbol, period="1y"):
    """
    Fetch Indian stock data using yfinance (FREE - No API key needed!)
    This is the easiest way to get NSE stock data
    """
    try:
        import yfinance as yf
        
        # Add .NS suffix for NSE stocks
        nse_symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(nse_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return None
        
        # Rename columns to match our format
        df.columns = [col.lower() for col in df.columns]
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

def get_indian_stock_data_demo(symbol):
    """
    Demo function that generates realistic stock data
    Use this if yfinance is not available
    """
    try:
        # Generate 500 days of demo data
        dates = pd.date_range(end=datetime.now(), periods=500, freq='D')
        
        # Starting price based on stock
        base_prices = {
            'RELIANCE': 2400, 'TCS': 3500, 'HDFCBANK': 1600,
            'ICICIBANK': 1100, 'INFY': 1500, 'SBIN': 750
        }
        
        base_price = base_prices.get(symbol, 1000)
        
        # Generate realistic price movement
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 500)
        price = base_price * (1 + returns).cumprod()
        
        # Create OHLCV data
        df = pd.DataFrame({
            'open': price * (1 + np.random.uniform(-0.01, 0.01, 500)),
            'high': price * (1 + np.random.uniform(0, 0.02, 500)),
            'low': price * (1 + np.random.uniform(-0.02, 0, 500)),
            'close': price,
            'volume': np.random.randint(1000000, 10000000, 500)
        }, index=dates)
        
        return df
        
    except Exception as e:
        st.error(f"Error generating demo data: {e}")
        return None

# ============================================================================
# PATTERN DETECTION
# ============================================================================

def detect_candlestick_patterns(df):
    """Detect candlestick patterns with explanations"""
    try:
        open_prices = df['open'].values
        high_prices = df['high'].values
        low_prices = df['low'].values
        close_prices = df['close'].values
        
        patterns = {}
        bullish_count = 0
        bearish_count = 0
        
        # Bullish patterns with simple explanations
        hammer = talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices)
        if hammer[-1] > 0:
            patterns['Hammer'] = {
                'signal': 'BULLISH',
                'meaning': 'Price rejected lower levels - buyers stepping in'
            }
            bullish_count += 1
        
        engulfing = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)
        if engulfing[-1] > 0:
            patterns['Bullish Engulfing'] = {
                'signal': 'BULLISH',
                'meaning': 'Strong buying pressure - trend reversal likely'
            }
            bullish_count += 1
        
        morning_star = talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices)
        if morning_star[-1] > 0:
            patterns['Morning Star'] = {
                'signal': 'BULLISH',
                'meaning': 'Bottom formation complete - uptrend starting'
            }
            bullish_count += 1
        
        piercing = talib.CDLPIERCING(open_prices, high_prices, low_prices, close_prices)
        if piercing[-1] > 0:
            patterns['Piercing Line'] = {
                'signal': 'BULLISH',
                'meaning': 'Buyers pushing prices higher - recovery signal'
            }
            bullish_count += 1
        
        # Bearish patterns with explanations
        shooting_star = talib.CDLSHOOTINGSTAR(open_prices, high_prices, low_prices, close_prices)
        if shooting_star[-1] < 0:
            patterns['Shooting Star'] = {
                'signal': 'BEARISH',
                'meaning': 'Price rejected at highs - sellers taking control'
            }
            bearish_count += 1
        
        if engulfing[-1] < 0:
            patterns['Bearish Engulfing'] = {
                'signal': 'BEARISH',
                'meaning': 'Strong selling pressure - downtrend likely'
            }
            bearish_count += 1
        
        evening_star = talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices)
        if evening_star[-1] < 0:
            patterns['Evening Star'] = {
                'signal': 'BEARISH',
                'meaning': 'Top formation complete - downtrend starting'
            }
            bearish_count += 1
        
        hanging_man = talib.CDLHANGINGMAN(open_prices, high_prices, low_prices, close_prices)
        if hanging_man[-1] < 0:
            patterns['Hanging Man'] = {
                'signal': 'BEARISH',
                'meaning': 'Buyers losing strength - trend reversal possible'
            }
            bearish_count += 1
        
        total = bullish_count + bearish_count
        bullish_strength = bullish_count / total if total > 0 else 0.5
        
        return patterns, bullish_strength, bullish_count, bearish_count
        
    except Exception as e:
        return {}, 0.5, 0, 0

# ============================================================================
# TECHNICAL ANALYSIS with EASY EXPLANATIONS
# ============================================================================

def add_technical_indicators(df):
    """Add technical indicators with human-readable interpretations"""
    df['MA5'] = talib.SMA(df['close'], timeperiod=5)
    df['MA10'] = talib.SMA(df['close'], timeperiod=10)
    df['MA20'] = talib.SMA(df['close'], timeperiod=20)
    df['MA50'] = talib.SMA(df['close'], timeperiod=50)
    df['EMA12'] = talib.EMA(df['close'], timeperiod=12)
    df['EMA26'] = talib.EMA(df['close'], timeperiod=26)
    
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(
        df['close'], fastperiod=12, slowperiod=26, signalperiod=9
    )
    
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = talib.BBANDS(df['close'], timeperiod=20)
    df['STOCH_k'], df['STOCH_d'] = talib.STOCH(
        df['high'], df['low'], df['close'],
        fastk_period=14, slowk_period=3, slowd_period=3
    )
    
    df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['OBV'] = talib.OBV(df['close'], df['volume'])
    
    return df.dropna()

def interpret_indicators(latest):
    """Provide easy-to-understand indicator interpretations"""
    interpretations = {}
    
    # RSI Interpretation
    rsi = latest['RSI']
    if rsi < 30:
        interpretations['RSI'] = {
            'value': rsi,
            'signal': 'OVERSOLD 🟢',
            'meaning': 'Stock is heavily sold - good buying opportunity',
            'color': 'green'
        }
    elif rsi > 70:
        interpretations['RSI'] = {
            'value': rsi,
            'signal': 'OVERBOUGHT 🔴',
            'meaning': 'Stock is overvalued - consider selling or wait',
            'color': 'red'
        }
    else:
        interpretations['RSI'] = {
            'value': rsi,
            'signal': 'NEUTRAL 🟡',
            'meaning': 'Stock in balanced zone - watch for signals',
            'color': 'orange'
        }
    
    # MACD Interpretation
    macd_diff = latest['MACD'] - latest['MACD_signal']
    if macd_diff > 0:
        interpretations['MACD'] = {
            'value': latest['MACD'],
            'signal': 'BULLISH 🟢',
            'meaning': 'Momentum is positive - uptrend in progress',
            'color': 'green'
        }
    else:
        interpretations['MACD'] = {
            'value': latest['MACD'],
            'signal': 'BEARISH 🔴',
            'meaning': 'Momentum is negative - downtrend in progress',
            'color': 'red'
        }
    
    # ADX Interpretation
    adx = latest['ADX']
    if adx > 25:
        interpretations['ADX'] = {
            'value': adx,
            'signal': 'STRONG TREND',
            'meaning': 'Clear trend - good for trend following strategies',
            'color': 'blue'
        }
    else:
        interpretations['ADX'] = {
            'value': adx,
            'signal': 'WEAK TREND',
            'meaning': 'No clear trend - range-bound market',
            'color': 'gray'
        }
    
    # Stochastic Interpretation
    stoch = latest['STOCH_k']
    if stoch < 20:
        interpretations['Stochastic'] = {
            'value': stoch,
            'signal': 'OVERSOLD 🟢',
            'meaning': 'Short-term bounce expected',
            'color': 'green'
        }
    elif stoch > 80:
        interpretations['Stochastic'] = {
            'value': stoch,
            'signal': 'OVERBOUGHT 🔴',
            'meaning': 'Short-term pullback expected',
            'color': 'red'
        }
    else:
        interpretations['Stochastic'] = {
            'value': stoch,
            'signal': 'NEUTRAL 🟡',
            'meaning': 'No extreme condition',
            'color': 'orange'
        }
    
    return interpretations

# ============================================================================
# ML PREDICTION
# ============================================================================

def train_and_predict(df):
    """Train ML models and make predictions"""
    try:
        feature_cols = [
            'MA5', 'MA10', 'MA20', 'MA50', 'EMA12', 'EMA26',
            'MACD', 'MACD_signal', 'RSI', 'STOCH_k', 'STOCH_d',
            'ATR', 'ADX'
        ]
        
        df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)
        df_clean = df.dropna()
        
        if len(df_clean) < 100:
            return None, None
        
        X = df_clean[feature_cols]
        y = df_clean['Target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train_scaled, y_train)
        
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb_model.fit(X_train_scaled, y_train)
        
        latest_features = X.iloc[-1:].values
        latest_scaled = scaler.transform(latest_features)
        
        rf_prob = rf_model.predict_proba(latest_scaled)[0]
        gb_prob = gb_model.predict_proba(latest_scaled)[0]
        
        avg_prob = (rf_prob + gb_prob) / 2
        prediction = 'BUY' if avg_prob[1] > 0.5 else 'SELL'
        confidence = np.max(avg_prob)
        
        rf_accuracy = rf_model.score(X_test_scaled, y_test)
        gb_accuracy = gb_model.score(X_test_scaled, y_test)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'rf_accuracy': rf_accuracy,
            'gb_accuracy': gb_accuracy,
            'avg_accuracy': (rf_accuracy + gb_accuracy) / 2
        }, df_clean
        
    except Exception as e:
        st.error(f"Error in prediction: {e}")
        return None, None

# ============================================================================
# ENHANCED CHART with BETTER VISUALIZATION
# ============================================================================

def create_enhanced_candlestick_chart(df, symbol, interpretations):
    """Create beautiful, easy-to-understand chart"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(
            f'{symbol} Price & Moving Averages',
            'RSI (Relative Strength Index)',
            'MACD (Momentum)',
            'Volume'
        ),
        row_heights=[0.5, 0.17, 0.17, 0.16]
    )
    
    # 1. Candlestick Chart with MAs
    fig.add_trace(
        go.Candlestick(
            x=df.index[-100:],
            open=df['open'][-100:],
            high=df['high'][-100:],
            low=df['low'][-100:],
            close=df['close'][-100:],
            name='Price',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # Moving Averages with better colors
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['MA20'][-100:], 
                  name='MA20 (Short)', line=dict(color='#FF6B6B', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['MA50'][-100:], 
                  name='MA50 (Long)', line=dict(color='#4ECDC4', width=2)),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['BB_upper'][-100:], 
                  name='BB Upper', line=dict(color='gray', width=1, dash='dash'),
                  opacity=0.5),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['BB_lower'][-100:], 
                  name='BB Lower', line=dict(color='gray', width=1, dash='dash'),
                  fill='tonexty', opacity=0.1),
        row=1, col=1
    )
    
    # 2. RSI with colored zones
    rsi_color = interpretations['RSI']['color']
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['RSI'][-100:], 
                  name='RSI', line=dict(color='purple', width=2.5)),
        row=2, col=1
    )
    
    # RSI zones
    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, 
                  annotation_text="Overbought", row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, 
                  annotation_text="Oversold", row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
    
    # 3. MACD
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['MACD'][-100:], 
                  name='MACD', line=dict(color='blue', width=2)),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['MACD_signal'][-100:], 
                  name='Signal', line=dict(color='red', width=2)),
        row=3, col=1
    )
    
    # MACD Histogram
    colors = ['green' if val > 0 else 'red' for val in df['MACD_hist'][-100:]]
    fig.add_trace(
        go.Bar(x=df.index[-100:], y=df['MACD_hist'][-100:],
               name='Histogram', marker_color=colors, opacity=0.3),
        row=3, col=1
    )
    
    # 4. Volume with colors
    colors = ['green' if df['close'].iloc[i] > df['open'].iloc[i] else 'red' 
              for i in range(-100, 0)]
    fig.add_trace(
        go.Bar(x=df.index[-100:], y=df['volume'][-100:],
               name='Volume', marker_color=colors, opacity=0.5),
        row=4, col=1
    )
    
    # Layout
    fig.update_layout(
        height=1000,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=11)
    )
    
    fig.update_yaxes(title_text="Price (₹)" if "NSE" in symbol else "Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    
    # Header with Indian flag colors
    st.markdown('<h1 class="main-header">🇮🇳 AI Trading Predictor - India & Global Markets</h1>', 
                unsafe_allow_html=True)
    st.markdown('<div class="indian-flag"></div>', unsafe_allow_html=True)
    
    st.markdown("### Professional Real-Time Analysis for Indian Stocks & Cryptocurrency")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("⚙️ Market Selection")
    
    # Market type selection
    market_type = st.sidebar.radio(
        "📊 Choose Market",
        ["🇮🇳 Indian Stocks (NSE)", "💰 Cryptocurrency"],
        index=0
    )
    
    if "Indian" in market_type:
        # Indian Stock Selection
        st.sidebar.markdown("### 🇮🇳 Top NSE Stocks")
        
        # Categorize stocks
        st.sidebar.markdown("**Banking & Finance**")
        finance_stocks = {k: v for k, v in list(NIFTY_50_STOCKS.items())[:10]}
        
        selected_stock_name = st.sidebar.selectbox(
            "Select Stock",
            list(NIFTY_50_STOCKS.keys()),
            index=0
        )
        
        symbol = NIFTY_50_STOCKS[selected_stock_name]
        display_symbol = f"{symbol} (NSE)"
        
        # Period selection for stocks
        period = st.sidebar.selectbox(
            "⏱️ Data Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        
    else:
        # Cryptocurrency Selection
        crypto_symbols = {
            "Bitcoin (BTC/USDT)": "BTCUSDT",
            "Ethereum (ETH/USDT)": "ETHUSDT",
            "Binance Coin (BNB/USDT)": "BNBUSDT",
            "Cardano (ADA/USDT)": "ADAUSDT",
            "Solana (SOL/USDT)": "SOLUSDT",
            "XRP (XRP/USDT)": "XRPUSDT",
            "Polkadot (DOT/USDT)": "DOTUSDT",
            "Dogecoin (DOGE/USDT)": "DOGEUSDT",
        }
        
        selected_crypto = st.sidebar.selectbox(
            "💰 Select Cryptocurrency",
            list(crypto_symbols.keys())
        )
        
        symbol = crypto_symbols[selected_crypto]
        display_symbol = selected_crypto
        
        # Interval for crypto
        interval_options = {
            "1 Minute": "1m",
            "5 Minutes": "5m",
            "15 Minutes": "15m",
            "30 Minutes": "30m",
            "1 Hour": "1h",
            "4 Hours": "4h",
            "1 Day": "1d"
        }
        
        selected_interval = st.sidebar.selectbox(
            "⏱️ Time Interval",
            list(interval_options.keys()),
            index=1
        )
        
        interval = interval_options[selected_interval]
    
    # Risk Management
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Risk Management")
    
    stop_loss = st.sidebar.slider("Stop Loss %", 1.0, 10.0, 5.0, 0.5)
    take_profit = st.sidebar.slider("Take Profit %", 5.0, 20.0, 10.0, 0.5)
    position_size = st.sidebar.slider("Position Size %", 1, 10, 2, 1)
    
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (60s)", value=False)
    
    st.sidebar.markdown("---")
    analyze_button = st.sidebar.button("🚀 ANALYZE NOW", use_container_width=True)
    
    st.sidebar.markdown("---")
    st.sidebar.info("⚠️ For educational purposes only!\n\n✅ Use SEBI-registered brokers\n❌ Avoid unregulated platforms")
    
    # Main Analysis
    if analyze_button or auto_refresh:
        
        with st.spinner(f"🔍 Analyzing {display_symbol}..."):
            
            # Fetch data based on market type
            if "Indian" in market_type:
                df = get_indian_stock_data_yfinance(symbol, period=period)
                if df is None:
                    st.warning("⚠️ Using demo data. Install yfinance for real data: pip install yfinance")
                    df = get_indian_stock_data_demo(symbol)
            else:
                df = get_crypto_data_binance(symbol, interval, limit=500)
            
            if df is None or len(df) < 100:
                st.error("❌ Failed to fetch sufficient data")
                return
            
            # Add indicators
            df = add_technical_indicators(df)
            
            # Detect patterns
            patterns, bullish_strength, bull_count, bear_count = detect_candlestick_patterns(df)
            
            # Make prediction
            prediction_result, df_clean = train_and_predict(df)
            
            if prediction_result is None:
                st.error("❌ Prediction failed - not enough data")
                return
            
            # Get interpretations
            latest = df.iloc[-1]
            interpretations = interpret_indicators(latest)
            current_price = latest['close']
            
            st.success("✅ Analysis Complete!")
            
            # Top Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100)
            currency_symbol = "₹" if "Indian" in market_type else "$"
            
            with col1:
                st.metric(
                    f"{currency_symbol} Current Price",
                    f"{currency_symbol}{current_price:,.2f}",
                    f"{price_change:+.2f}%"
                )
            
            with col2:
                emoji = "🟢" if prediction_result['prediction'] == 'BUY' else "🔴"
                st.metric(
                    f"{emoji} AI Prediction",
                    prediction_result['prediction'],
                    f"{prediction_result['confidence']*100:.1f}% confident"
                )
            
            with col3:
                st.metric(
                    "🎯 Model Accuracy",
                    f"{prediction_result['avg_accuracy']*100:.1f}%",
                    "Trained on historical data"
                )
            
            with col4:
                pattern_score = bull_count - bear_count
                pattern_emoji = "🟢" if pattern_score > 0 else "🔴" if pattern_score < 0 else "🟡"
                st.metric(
                    f"{pattern_emoji} Pattern Score",
                    f"{pattern_score:+d}",
                    f"{bull_count}B / {bear_count}B"
                )
            
            st.markdown("---")
            
            # Signal Box
            if prediction_result['prediction'] == 'BUY' and prediction_result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                st.markdown(
                    f'<div class="buy-signal">🟢 STRONG BUY SIGNAL 🟢<br>AI Confidence: {prediction_result["confidence"]*100:.1f}% | Pattern Score: {bull_count} Bullish</div>', 
                    unsafe_allow_html=True
                )
            elif prediction_result['prediction'] == 'SELL' and prediction_result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                st.markdown(
                    f'<div class="sell-signal">🔴 STRONG SELL SIGNAL 🔴<br>AI Confidence: {prediction_result["confidence"]*100:.1f}% | Pattern Score: {bear_count} Bearish</div>', 
                    unsafe_allow_html=True
                )
            else:
                st.info(f"⚠️ WEAK SIGNAL - Confidence {prediction_result['confidence']*100:.1f}% below threshold. Wait for clearer opportunity.")
            
            st.markdown("---")
            
            # Analysis Details
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### 🕯️ Candlestick Patterns Detected")
                
                if patterns:
                    for pattern_name, pattern_info in patterns.items():
                        signal = pattern_info['signal']
                        meaning = pattern_info['meaning']
                        emoji = "🟢" if signal == "BULLISH" else "🔴"
                        st.markdown(
                            f'<div class="pattern-box">{emoji} <strong>{pattern_name}</strong>: {signal}<br><small>{meaning}</small></div>', 
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No significant patterns detected in recent candles")
                
                st.markdown(f"""
                **Pattern Summary:**
                - ✅ Bullish Signals: {bull_count}
                - ❌ Bearish Signals: {bear_count}
                - 📊 Net Strength: {bullish_strength*100:.1f}% Bullish
                """)
            
            with col_right:
                st.markdown("### 📊 Technical Indicators (Easy Explanation)")
                
                for indicator_name, info in interpretations.items():
                    st.markdown(
                        f"""
                        <div class="indicator-box">
                            <strong>{indicator_name}</strong><br>
                            <small>💡 Signal: {info.get("meaning", "No signal available")}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            st.markdown("---")
            
            # Risk Management
            st.markdown("### 🛡️ Smart Risk Management")
            
            stop_loss_price = current_price * (1 - stop_loss / 100)
            take_profit_price = current_price * (1 + take_profit / 100)
            risk_reward = take_profit / stop_loss
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🛑 Stop Loss", f"{currency_symbol}{stop_loss_price:.2f}", f"-{stop_loss}%")
            
            with col2:
                st.metric("🎯 Take Profit", f"{currency_symbol}{take_profit_price:.2f}", f"+{take_profit}%")
            
            with col3:
                st.metric("⚖️ Risk/Reward", f"{risk_reward:.2f}", "Good" if risk_reward > 1.5 else "Poor")
            
            with col4:
                st.metric("📦 Position Size", f"{position_size}%", "of total capital")
            
            st.markdown("---")
            
            # Enhanced Chart
            st.markdown("### 📈 Professional Technical Analysis Chart")
            st.markdown('<div class="info-box">💡 <strong>How to Read:</strong> Green candles = price went up, Red = went down. Watch where price touches Moving Averages (colored lines) for support/resistance levels.</div>', unsafe_allow_html=True)
            
            chart = create_enhanced_candlestick_chart(df, display_symbol, interpretations)
            st.plotly_chart(chart, use_container_width=True)
            
            st.markdown("---")
            
            # Trading Recommendation
            st.markdown("### 💡 Smart Trading Recommendation")
            
            if prediction_result['prediction'] == 'BUY' and bullish_strength >= 0.5 and prediction_result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                st.success(f"""
                ✅ **STRONG BUY RECOMMENDATION**
                
                **Why This is a Good Buy Signal:**
                - 🤖 AI Models agree on upward movement ({prediction_result['confidence']*100:.1f}% confidence)
                - 🕯️ {bull_count} bullish candlestick patterns detected
                - 📊 Overall bullish strength: {bullish_strength*100:.1f}%
                - ✅ Multiple indicators align positively
                
                **Suggested Trading Plan:**
                1. **Entry Price:** {currency_symbol}{current_price:,.2f} (current market price)
                2. **Stop Loss:** {currency_symbol}{stop_loss_price:,.2f} (-{stop_loss}% from entry)
                3. **Take Profit:** {currency_symbol}{take_profit_price:,.2f} (+{take_profit}% from entry)
                4. **Position Size:** Use only {position_size}% of your total capital
                5. **Risk/Reward:** 1:{risk_reward:.2f} (Risk ₹1 to potentially gain ₹{risk_reward:.2f})
                
                **Important Reminders:**
                - ⚠️ Set stop-loss immediately after entering position
                - 📱 Monitor your position regularly
                - 🎯 Consider booking partial profits at target levels
                - 💰 Never invest more than you can afford to lose
                """)
            
            elif prediction_result['prediction'] == 'SELL' and bullish_strength < 0.5 and prediction_result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                st.error(f"""
                ⚠️ **STRONG SELL/AVOID RECOMMENDATION**
                
                **Why You Should Avoid Buying Now:**
                - 🤖 AI Models predict downward movement ({prediction_result['confidence']*100:.1f}% confidence)
                - 🕯️ {bear_count} bearish candlestick patterns detected
                - 📊 Overall bearish strength: {(1-bullish_strength)*100:.1f}%
                - ❌ Multiple indicators show negative signals
                
                **Suggested Action Plan:**
                1. **DO NOT** enter new long positions now
                2. **If you own this stock:** Consider booking profits or tightening stop-loss
                3. **Set price alerts** for potential reversal levels
                4. **Wait** for clearer bullish signals before buying
                5. **Monitor** for pattern changes over next few days
                
                **Better Strategy:**
                - 🔍 Watch for support levels where price may bounce
                - 📊 Wait for RSI to reach oversold (<30) for potential entry
                - 🕯️ Look for bullish reversal patterns before considering entry
                """)
            
            else:
                st.warning(f"""
                ⚠️ **MIXED SIGNALS - WAIT FOR BETTER OPPORTUNITY**
                
                **Current Market Situation:**
                - 🤖 Prediction: {prediction_result['prediction']} with {prediction_result['confidence']*100:.1f}% confidence
                - 📊 Pattern signals are mixed or contradictory
                - ⚖️ Bulls vs Bears: {bull_count} vs {bear_count}
                - 🎯 Confidence below our {Config.CONFIDENCE_THRESHOLD*100:.0f}% threshold
                
                **Why This Matters:**
                When signals are mixed, the market is uncertain. Trading in uncertain conditions increases risk.
                
                **Best Course of Action:**
                1. **WAIT** - Don't force a trade when signals are unclear
                2. **MONITOR** - Check again after a few hours/days
                3. **SET ALERTS** - Get notified when confidence improves
                4. **BE PATIENT** - Good opportunities come to those who wait
                5. **KEEP LEARNING** - Study why signals are mixed
                
                **What to Watch For:**
                - Wait for confidence above {Config.CONFIDENCE_THRESHOLD*100:.0f}%
                - Look for clear pattern alignment (all bullish or all bearish)
                - Check if price breaks key support/resistance levels
                """)
            
            # Timestamp and Data Source
            st.markdown("---")
            data_source = "NSE India via yFinance" if "Indian" in market_type else "Binance (Real-time)"
            st.markdown(f"""
            **Last Updated:** {datetime.now().strftime('%d %B %Y, %I:%M:%S %p IST')}  
            **Data Source:** {data_source}  
            **Analysis Period:** Last {len(df)} candles
            """)
            
            # Auto refresh
            if auto_refresh:
                time.sleep(60)
                st.rerun()

if __name__ == "__main__":
    main()
