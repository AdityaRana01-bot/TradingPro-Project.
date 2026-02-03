
# Create the professional Streamlit UI - Fixed version

streamlit_ui_code = r'''
"""
PROFESSIONAL TRADING PREDICTION DASHBOARD
==========================================
Beautiful, Simple, and Easy-to-Use Web Interface
Built with Streamlit for Real-Time Trading Predictions

Run with: streamlit run trading_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import talib
from datetime import datetime
import time
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Page Configuration
st.set_page_config(
    page_title="AI Trading Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
    }
    
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
    }
    
    .pattern-box {
        background-color: #fff3cd;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ffc107;
    }
    
    .indicator-box {
        background-color: #d1ecf1;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
class Config:
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"
    CONFIDENCE_THRESHOLD = 0.65

@st.cache_data(ttl=60)
def get_crypto_data_binance(symbol, interval, limit=500):
    """Fetch cryptocurrency data from Binance"""
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
        st.error(f"Error fetching data: {e}")
        return None

def detect_candlestick_patterns(df):
    """Detect candlestick patterns"""
    try:
        open_prices = df['open'].values
        high_prices = df['high'].values
        low_prices = df['low'].values
        close_prices = df['close'].values
        
        patterns = {}
        bullish_count = 0
        bearish_count = 0
        
        # Bullish patterns
        hammer = talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices)
        if hammer[-1] > 0:
            patterns['Hammer'] = 'BULLISH'
            bullish_count += 1
        
        engulfing = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)
        if engulfing[-1] > 0:
            patterns['Bullish Engulfing'] = 'BULLISH'
            bullish_count += 1
        
        morning_star = talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices)
        if morning_star[-1] > 0:
            patterns['Morning Star'] = 'BULLISH'
            bullish_count += 1
        
        # Bearish patterns
        shooting_star = talib.CDLSHOOTINGSTAR(open_prices, high_prices, low_prices, close_prices)
        if shooting_star[-1] < 0:
            patterns['Shooting Star'] = 'BEARISH'
            bearish_count += 1
        
        if engulfing[-1] < 0:
            patterns['Bearish Engulfing'] = 'BEARISH'
            bearish_count += 1
        
        evening_star = talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices)
        if evening_star[-1] < 0:
            patterns['Evening Star'] = 'BEARISH'
            bearish_count += 1
        
        total = bullish_count + bearish_count
        bullish_strength = bullish_count / total if total > 0 else 0.5
        
        return patterns, bullish_strength, bullish_count, bearish_count
        
    except Exception as e:
        return {}, 0.5, 0, 0

def add_technical_indicators(df):
    """Add technical indicators"""
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
    
    return df.dropna()

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

def create_candlestick_chart(df, symbol):
    """Create interactive candlestick chart"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Price Chart', 'RSI', 'MACD'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    fig.add_trace(
        go.Candlestick(
            x=df.index[-100:],
            open=df['open'][-100:],
            high=df['high'][-100:],
            low=df['low'][-100:],
            close=df['close'][-100:],
            name='Price'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['MA20'][-100:], 
                  name='MA20', line=dict(color='orange', width=1)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['MA50'][-100:], 
                  name='MA50', line=dict(color='blue', width=1)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index[-100:], y=df['RSI'][-100:], 
                  name='RSI', line=dict(color='purple', width=2)),
        row=2, col=1
    )
    
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
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
    
    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    return fig

def main():
    st.markdown('<h1 class="main-header">🎯 AI Trading Prediction Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("### Professional Real-Time Trading Analysis with AI & Machine Learning")
    st.markdown("---")
    
    st.sidebar.title("⚙️ Settings")
    
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
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Risk Management")
    
    stop_loss = st.sidebar.slider("Stop Loss %", 1.0, 10.0, 5.0, 0.5)
    take_profit = st.sidebar.slider("Take Profit %", 5.0, 20.0, 10.0, 0.5)
    position_size = st.sidebar.slider("Position Size %", 1, 10, 2, 1)
    
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (5s)", value=False)
    
    st.sidebar.markdown("---")
    analyze_button = st.sidebar.button("🚀 ANALYZE NOW", use_container_width=True)
    
    st.sidebar.markdown("---")
    st.sidebar.warning("⚠️ Educational purposes only!")
    
    if analyze_button or auto_refresh:
        
        with st.spinner(f"🔍 Analyzing {selected_crypto}..."):
            
            df = get_crypto_data_binance(symbol, interval, limit=500)
            
            if df is None or len(df) < 100:
                st.error("❌ Failed to fetch data")
                return
            
            df = add_technical_indicators(df)
            patterns, bullish_strength, bull_count, bear_count = detect_candlestick_patterns(df)
            prediction_result, df_clean = train_and_predict(df)
            
            if prediction_result is None:
                st.error("❌ Prediction failed")
                return
            
            latest = df.iloc[-1]
            current_price = latest['close']
            
            st.success("✅ Analysis Complete!")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💵 Current Price",
                    f"${current_price:,.2f}",
                    f"{((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100):.2f}%"
                )
            
            with col2:
                emoji = "🟢" if prediction_result['prediction'] == 'BUY' else "🔴"
                st.metric(
                    f"{emoji} Prediction",
                    prediction_result['prediction'],
                    f"{prediction_result['confidence']*100:.1f}%"
                )
            
            with col3:
                st.metric(
                    "🎯 Model Accuracy",
                    f"{prediction_result['avg_accuracy']*100:.1f}%"
                )
            
            with col4:
                pattern_score = bull_count - bear_count
                st.metric(
                    "📊 Pattern Score",
                    f"{pattern_score:+d}",
                    f"{bull_count}B/{bear_count}B"
                )
            
            st.markdown("---")
            
            if prediction_result['prediction'] == 'BUY' and prediction_result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                st.markdown(
                    f'<div class="buy-signal">🟢 STRONG BUY SIGNAL 🟢<br>Confidence: {prediction_result["confidence"]*100:.1f}%</div>', 
                    unsafe_allow_html=True
                )
            elif prediction_result['prediction'] == 'SELL' and prediction_result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                st.markdown(
                    f'<div class="sell-signal">🔴 STRONG SELL SIGNAL 🔴<br>Confidence: {prediction_result["confidence"]*100:.1f}%</div>', 
                    unsafe_allow_html=True
                )
            else:
                st.info(f"⚠️ WEAK SIGNAL - {prediction_result['confidence']*100:.1f}% confidence")
            
            st.markdown("---")
            
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### 🕯️ Candlestick Patterns")
                
                if patterns:
                    for pattern, signal in patterns.items():
                        emoji = "🟢" if signal == "BULLISH" else "🔴"
                        st.markdown(
                            f'<div class="pattern-box">{emoji} <strong>{pattern}</strong>: {signal}</div>', 
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No patterns detected")
                
                st.markdown(f"**Summary:** {bull_count} Bullish | {bear_count} Bearish")
            
            with col_right:
                st.markdown("### 📊 Technical Indicators")
                
                rsi_signal = "Oversold 🟢" if latest['RSI'] < 30 else "Overbought 🔴" if latest['RSI'] > 70 else "Neutral 🟡"
                st.markdown(
                    f'<div class="indicator-box"><strong>RSI:</strong> {latest["RSI"]:.2f} - {rsi_signal}</div>', 
                    unsafe_allow_html=True
                )
                
                macd_signal = "Bullish 🟢" if latest['MACD'] > latest['MACD_signal'] else "Bearish 🔴"
                st.markdown(
                    f'<div class="indicator-box"><strong>MACD:</strong> {latest["MACD"]:.4f} - {macd_signal}</div>', 
                    unsafe_allow_html=True
                )
                
                adx_strength = "Strong" if latest['ADX'] > 25 else "Weak"
                st.markdown(
                    f'<div class="indicator-box"><strong>ADX:</strong> {latest["ADX"]:.2f} - {adx_strength} Trend</div>', 
                    unsafe_allow_html=True
                )
            
            st.markdown("---")
            
            st.markdown("### 🛡️ Risk Management")
            
            stop_loss_price = current_price * (1 - stop_loss/100)
            take_profit_price = current_price * (1 + take_profit/100)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🛑 Stop Loss", f"${stop_loss_price:,.2f}", f"-{stop_loss}%")
            
            with col2:
                st.metric("🎯 Take Profit", f"${take_profit_price:,.2f}", f"+{take_profit}%")
            
            with col3:
                st.metric("💰 Position Size", f"{position_size}%")
            
            st.markdown("---")
            
            st.markdown("### 📈 Interactive Chart")
            
            chart = create_candlestick_chart(df, symbol)
            st.plotly_chart(chart, use_container_width=True)
            
            st.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if auto_refresh:
                time.sleep(5)
                st.rerun()

if __name__ == "__main__":
    main()
'''

# Save the corrected UI code
with open('trading_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(streamlit_ui_code)

print("✅ Professional Trading Dashboard UI Created Successfully!")
print("=" * 70)
print("\nFile: trading_dashboard.py")
print("\nTo run the dashboard:")
print("  streamlit run trading_dashboard.py")
print("=" * 70)
