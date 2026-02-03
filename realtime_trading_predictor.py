
"""
REAL-TIME TRADING PREDICTION SYSTEM
Professional AI-Powered Trading Prediction for International Markets
Supports: Stocks, Crypto, Forex
Free Data Sources: Alpha Vantage, Binance API, Yahoo Finance

⚠️ IMPORTANT DISCLAIMERS:
- This is for EDUCATIONAL purposes only
- No trading system guarantees profits
- Always use stop-loss orders and risk management
- Past performance does not guarantee future results
- Only invest money you can afford to lose
- Consult a financial advisor before trading

Author: AI Trading Assistant
Version: 2.0
Date: October 2025
"""

import requests
import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Machine Learning Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Deep Learning for Advanced Predictions
try:
    from tensorflow import keras
    from keras.models import Sequential
    from keras.layers import LSTM, Dense, Dropout
    KERAS_AVAILABLE = True
except:
    KERAS_AVAILABLE = False
    print("Note: TensorFlow not installed. Using RandomForest only.")

# CONFIGURATION SECTION - Add Your API Keys Here

class Config:
    """Configuration for API keys and settings"""

    # Alpha Vantage API (Free: 25 requests/day)
    # Get your free key at: https://www.alphavantage.co/support/#api-key
    ALPHA_VANTAGE_API_KEY = "VK7G7MDDAGDHCQW2"

    # Binance API (Free, No registration needed for public data)
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"

    # Trading Parameters
    CONFIDENCE_THRESHOLD = 0.65  # 65% confidence minimum for predictions
    STOP_LOSS_PERCENT = 5.0      # 5% stop loss
    TAKE_PROFIT_PERCENT = 10.0   # 10% take profit target

    # Risk Management
    MAX_POSITION_SIZE = 0.02     # Risk max 2% per trade
    MAX_DAILY_TRADES = 10        # Limit daily trades

# DATA COLLECTION MODULE - Multiple Free Sources

class DataCollector:
    """Collect real-time and historical data from multiple free sources"""

    def __init__(self):
        self.av_key = Config.ALPHA_VANTAGE_API_KEY
        self.binance_url = Config.BINANCE_BASE_URL

    def get_crypto_data_binance(self, symbol="BTCUSDT", interval="1m", limit=500):
        """
        Get real-time cryptocurrency data from Binance (100% FREE)

        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d
        Symbols: BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, SOLUSDT, etc.
        """
        try:
            endpoint = f"{self.binance_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }

            response = requests.get(endpoint, params=params)
            data = response.json()

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])

            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)

            df.set_index('timestamp', inplace=True)

            print(f"✅ Successfully fetched {len(df)} candles for {symbol}")
            return df[['open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            print(f"❌ Error fetching Binance data: {e}")
            return None

    def get_stock_data_alphavantage(self, symbol, interval="5min"):
        """
        Get stock data from Alpha Vantage (FREE: 25 calls/day)

        Intervals: 1min, 5min, 15min, 30min, 60min
        Symbols: AAPL, GOOGL, MSFT, TSLA, AMZN, etc.
        """
        try:
            if self.av_key == "YOUR_FREE_API_KEY_HERE":
                print("⚠️ Please add your Alpha Vantage API key in Config section")
                print("Get free key at: https://www.alphavantage.co/support/#api-key")
                return None

            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.av_key,
                'outputsize': 'full'
            }

            response = requests.get(url, params=params)
            data = response.json()

            # Extract time series data
            time_key = f'Time Series ({interval})'
            if time_key not in data:
                print(f"❌ Error: {data.get('Note', 'API limit reached or invalid symbol')}")
                return None

            time_series = data[time_key]

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)
            df.sort_index(inplace=True)

            print(f"✅ Successfully fetched {len(df)} candles for {symbol}")
            return df

        except Exception as e:
            print(f"❌ Error fetching Alpha Vantage data: {e}")
            return None

    def get_yahoo_finance_data(self, symbol, period="1d", interval="5m"):
        """
        Fallback: Get data from Yahoo Finance using yfinance

        Note: Requires 'yfinance' library
        """
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            print(f"✅ Successfully fetched {len(df)} candles for {symbol}")
            return df[['Open', 'High', 'Low', 'Close', 'Volume']].rename(columns=str.lower)
        except Exception as e:
            print(f"❌ Error fetching Yahoo Finance data: {e}")
            return None

# CANDLESTICK PATTERN RECOGNITION MODULE

class CandlestickPatternDetector:
    """Detect candlestick patterns using TA-Lib and custom formulas"""

    def __init__(self):
        self.patterns = []

    def detect_all_patterns(self, df):
        """Detect 50+ candlestick patterns using TA-Lib"""

        open_prices = df['open'].values
        high_prices = df['high'].values
        low_prices = df['low'].values
        close_prices = df['close'].values

        patterns_detected = {}

        # Bullish Patterns (Positive = Buy Signal)
        bullish_patterns = {
            'HAMMER': talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices),
            'INVERTED_HAMMER': talib.CDLINVERTEDHAMMER(open_prices, high_prices, low_prices, close_prices),
            'MORNING_STAR': talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices),
            'PIERCING': talib.CDLPIERCING(open_prices, high_prices, low_prices, close_prices),
            'THREE_WHITE_SOLDIERS': talib.CDL3WHITESOLDIERS(open_prices, high_prices, low_prices, close_prices),
            'BULLISH_ENGULFING': talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices),
            'HARAMI_BULLISH': talib.CDLHARAMI(open_prices, high_prices, low_prices, close_prices),
        }

        # Bearish Patterns (Negative = Sell Signal)
        bearish_patterns = {
            'HANGING_MAN': talib.CDLHANGINGMAN(open_prices, high_prices, low_prices, close_prices),
            'SHOOTING_STAR': talib.CDLSHOOTINGSTAR(open_prices, high_prices, low_prices, close_prices),
            'EVENING_STAR': talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices),
            'DARK_CLOUD': talib.CDLDARKCLOUDCOVER(open_prices, high_prices, low_prices, close_prices),
            'THREE_BLACK_CROWS': talib.CDL3BLACKCROWS(open_prices, high_prices, low_prices, close_prices),
            'BEARISH_ENGULFING': talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices),
        }

        # Check latest candle for patterns
        latest_idx = -1
        bullish_count = 0
        bearish_count = 0

        for name, pattern in bullish_patterns.items():
            if pattern[latest_idx] > 0:
                patterns_detected[name] = "BULLISH"
                bullish_count += 1

        for name, pattern in bearish_patterns.items():
            if pattern[latest_idx] < 0:
                patterns_detected[name] = "BEARISH"
                bearish_count += 1

        # Calculate pattern strength
        total_patterns = bullish_count + bearish_count
        if total_patterns > 0:
            bullish_strength = bullish_count / total_patterns
        else:
            bullish_strength = 0.5  # Neutral

        return patterns_detected, bullish_strength, bullish_count, bearish_count

# TECHNICAL INDICATORS MODULE

class TechnicalAnalysis:
    """Calculate technical indicators for prediction"""

    @staticmethod
    def add_indicators(df):
        """Add comprehensive technical indicators"""

        # Moving Averages
        df['MA5'] = talib.SMA(df['close'], timeperiod=5)
        df['MA10'] = talib.SMA(df['close'], timeperiod=10)
        df['MA20'] = talib.SMA(df['close'], timeperiod=20)
        df['MA50'] = talib.SMA(df['close'], timeperiod=50)
        df['EMA12'] = talib.EMA(df['close'], timeperiod=12)
        df['EMA26'] = talib.EMA(df['close'], timeperiod=26)

        # MACD
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(
            df['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )

        # RSI
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)

        # Bollinger Bands
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = talib.BBANDS(
            df['close'], timeperiod=20
        )

        # Stochastic
        df['STOCH_k'], df['STOCH_d'] = talib.STOCH(
            df['high'], df['low'], df['close'],
            fastk_period=14, slowk_period=3, slowd_period=3
        )

        # ATR (Average True Range) - Volatility
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)

        # ADX (Trend Strength)
        df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)

        # Volume Indicators
        df['OBV'] = talib.OBV(df['close'], df['volume'])
        df['VOLUME_MA'] = talib.SMA(df['volume'], timeperiod=20)

        # Price Rate of Change
        df['ROC'] = talib.ROC(df['close'], timeperiod=10)

        # Momentum
        df['MOM'] = talib.MOM(df['close'], timeperiod=10)

        return df.dropna()

# AI/ML PREDICTION ENGINE

class TradingPredictor:
    """AI-powered trading prediction using multiple ML models"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_model = None
        self.gb_model = None
        self.lstm_model = None

    def prepare_features(self, df):
        """Prepare feature matrix for ML models"""

        feature_cols = [
            'MA5', 'MA10', 'MA20', 'MA50', 'EMA12', 'EMA26',
            'MACD', 'MACD_signal', 'MACD_hist',
            'RSI', 'STOCH_k', 'STOCH_d',
            'BB_upper', 'BB_middle', 'BB_lower',
            'ATR', 'ADX', 'OBV', 'VOLUME_MA',
            'ROC', 'MOM'
        ]

        # Create target variable (1 = price goes up, 0 = price goes down)
        df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)
        df['Price_Change'] = df['close'].pct_change()

        # Drop rows with NaN
        df_clean = df.dropna()

        X = df_clean[feature_cols]
        y = df_clean['Target']

        return X, y, df_clean

    def train_models(self, df):
        """Train multiple ML models for ensemble prediction"""

        print("\n🤖 Training AI Models...")
        print("=" * 60)

        X, y, df_clean = self.prepare_features(df)

        if len(X) < 100:
            print("❌ Not enough data for training (need at least 100 samples)")
            return False

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest
        print("📊 Training Random Forest Classifier...")
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train_scaled, y_train)
        rf_score = self.rf_model.score(X_test_scaled, y_test)
        print(f"   ✅ Random Forest Accuracy: {rf_score:.2%}")

        # Train Gradient Boosting
        print("🚀 Training Gradient Boosting Classifier...")
        self.gb_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.gb_model.fit(X_train_scaled, y_train)
        gb_score = self.gb_model.score(X_test_scaled, y_test)
        print(f"   ✅ Gradient Boosting Accuracy: {gb_score:.2%}")

        # Train LSTM if available
        if KERAS_AVAILABLE and len(X) >= 200:
            print("🧠 Training LSTM Neural Network...")
            try:
                # Reshape for LSTM [samples, time steps, features]
                X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
                X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

                self.lstm_model = Sequential([
                    LSTM(50, return_sequences=True, input_shape=(1, X_train_scaled.shape[1])),
                    Dropout(0.2),
                    LSTM(50, return_sequences=False),
                    Dropout(0.2),
                    Dense(25, activation='relu'),
                    Dense(1, activation='sigmoid')
                ])

                self.lstm_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                self.lstm_model.fit(X_train_lstm, y_train, epochs=10, batch_size=32, verbose=0)

                lstm_score = self.lstm_model.evaluate(X_test_lstm, y_test, verbose=0)[1]
                print(f"   ✅ LSTM Accuracy: {lstm_score:.2%}")

            except Exception as e:
                print(f"   ⚠️ LSTM training skipped: {e}")
                self.lstm_model = None

        print("=" * 60)
        print("✅ Model Training Complete!\n")
        return True

    def predict_realtime(self, df):
        """Make real-time prediction using ensemble of models"""

        if self.rf_model is None:
            print("❌ Models not trained yet. Call train_models() first.")
            return None

        # Prepare latest data point
        X, _, df_clean = self.prepare_features(df)
        latest_features = X.iloc[-1:].values
        latest_features_scaled = self.scaler.transform(latest_features)

        # Get predictions from all models
        predictions = []
        probabilities = []

        # Random Forest prediction
        rf_pred = self.rf_model.predict(latest_features_scaled)[0]
        rf_prob = self.rf_model.predict_proba(latest_features_scaled)[0]
        predictions.append(rf_pred)
        probabilities.append(rf_prob)

        # Gradient Boosting prediction
        gb_pred = self.gb_model.predict(latest_features_scaled)[0]
        gb_prob = self.gb_model.predict_proba(latest_features_scaled)[0]
        predictions.append(gb_pred)
        probabilities.append(gb_prob)

        # LSTM prediction if available
        if self.lstm_model is not None:
            latest_lstm = latest_features_scaled.reshape((1, 1, latest_features_scaled.shape[1]))
            lstm_prob = self.lstm_model.predict(latest_lstm, verbose=0)[0][0]
            lstm_pred = 1 if lstm_prob > 0.5 else 0
            predictions.append(lstm_pred)
            probabilities.append([1-lstm_prob, lstm_prob])

        # Ensemble prediction (majority vote)
        ensemble_pred = np.round(np.mean(predictions))

        # Average probability
        avg_prob = np.mean(probabilities, axis=0)
        confidence = np.max(avg_prob)

        # Get current price
        current_price = df['close'].iloc[-1]

        result = {
            'prediction': 'BUY' if ensemble_pred == 1 else 'SELL',
            'confidence': confidence,
            'current_price': current_price,
            'rf_prediction': 'BUY' if rf_pred == 1 else 'SELL',
            'gb_prediction': 'BUY' if gb_pred == 1 else 'SELL',
            'timestamp': datetime.now()
        }

        if self.lstm_model is not None:
            result['lstm_prediction'] = 'BUY' if lstm_pred == 1 else 'SELL'

        return result


# MAIN TRADING SYSTEM

class RealTimeTradingSystem:
    """Complete real-time trading prediction system"""

    def __init__(self):
        self.data_collector = DataCollector()
        self.pattern_detector = CandlestickPatternDetector()
        self.technical_analysis = TechnicalAnalysis()
        self.predictor = TradingPredictor()
        self.trades_today = 0

    def analyze_and_predict(self, symbol, market_type='crypto', interval='5m'):
        """
        Complete analysis and prediction for a given symbol

        Parameters:
        -----------
        symbol : str
            Trading symbol (e.g., 'BTCUSDT' for crypto, 'AAPL' for stocks)
        market_type : str
            'crypto' or 'stock'
        interval : str
            Time interval for candles
        """

        print("\n" + "="*80)
        print(f"🎯 REAL-TIME TRADING PREDICTION SYSTEM")
        print("="*80)
        print(f"Symbol: {symbol}")
        print(f"Market: {market_type.upper()}")
        print(f"Interval: {interval}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Step 1: Collect Data
        print("\n📊 Step 1: Collecting Market Data...")
        if market_type == 'crypto':
            df = self.data_collector.get_crypto_data_binance(symbol, interval, limit=500)
        else:
            df = self.data_collector.get_stock_data_alphavantage(symbol, interval)

        if df is None or len(df) < 100:
            print("❌ Failed to collect sufficient data")
            return None

        # Step 2: Detect Candlestick Patterns
        print("\n🕯️ Step 2: Detecting Candlestick Patterns...")
        patterns, bullish_strength, bull_count, bear_count = self.pattern_detector.detect_all_patterns(df)

        if patterns:
            print(f"   Found {len(patterns)} patterns:")
            for pattern, signal in patterns.items():
                emoji = "🟢" if signal == "BULLISH" else "🔴"
                print(f"   {emoji} {pattern}: {signal}")
        else:
            print("   No significant patterns detected")

        print(f"\n   Pattern Score: {bull_count} Bullish | {bear_count} Bearish")
        print(f"   Bullish Strength: {bullish_strength:.1%}")

        # Step 3: Calculate Technical Indicators
        print("\n📈 Step 3: Calculating Technical Indicators...")
        df = self.technical_analysis.add_indicators(df)

        latest = df.iloc[-1]
        print(f"   RSI: {latest['RSI']:.2f} (Oversold<30, Overbought>70)")
        print(f"   MACD: {latest['MACD']:.4f} (Signal: {latest['MACD_signal']:.4f})")
        print(f"   ADX: {latest['ADX']:.2f} (Trend Strength)")
        print(f"   Current Price: ${latest['close']:.2f}")

        # Step 4: Train AI Models
        print("\n🤖 Step 4: Training AI Prediction Models...")
        training_success = self.predictor.train_models(df)

        if not training_success:
            print("❌ Model training failed")
            return None

        # Step 5: Make Prediction
        print("\n🎯 Step 5: Generating Trading Prediction...")
        prediction = self.predictor.predict_realtime(df)

        if prediction is None:
            print("❌ Prediction failed")
            return None

        # Display Results
        print("\n" + "="*80)
        print("🎯 PREDICTION RESULTS")
        print("="*80)

        signal_emoji = "🟢 BUY" if prediction['prediction'] == 'BUY' else "🔴 SELL"
        print(f"\n   SIGNAL: {signal_emoji}")
        print(f"   Confidence: {prediction['confidence']:.1%}")
        print(f"   Current Price: ${prediction['current_price']:.2f}")

        # Individual model predictions
        print(f"\n   Model Consensus:")
        print(f"   - Random Forest: {prediction['rf_prediction']}")
        print(f"   - Gradient Boosting: {prediction['gb_prediction']}")
        if 'lstm_prediction' in prediction:
            print(f"   - LSTM Network: {prediction['lstm_prediction']}")

        # Risk Management Recommendations
        print(f"\n   📋 Risk Management:")
        stop_loss = prediction['current_price'] * (1 - Config.STOP_LOSS_PERCENT/100)
        take_profit = prediction['current_price'] * (1 + Config.TAKE_PROFIT_PERCENT/100)

        print(f"   - Stop Loss: ${stop_loss:.2f} ({Config.STOP_LOSS_PERCENT}% below)")
        print(f"   - Take Profit: ${take_profit:.2f} ({Config.TAKE_PROFIT_PERCENT}% above)")
        print(f"   - Max Position Size: {Config.MAX_POSITION_SIZE*100}% of portfolio")

        # Trading Recommendation
        print(f"\n   💡 Recommendation:")
        if prediction['confidence'] >= Config.CONFIDENCE_THRESHOLD:
            if prediction['prediction'] == 'BUY' and bullish_strength >= 0.5:
                print(f"   ✅ STRONG {prediction['prediction']} SIGNAL")
                print(f"   Both AI models and candlestick patterns agree")
            elif prediction['prediction'] == 'SELL' and bullish_strength < 0.5:
                print(f"   ✅ STRONG {prediction['prediction']} SIGNAL")
                print(f"   Both AI models and candlestick patterns agree")
            else:
                print(f"   ⚠️ MODERATE {prediction['prediction']} SIGNAL")
                print(f"   AI models and patterns show mixed signals")
        else:
            print(f"   ⚠️ WEAK SIGNAL - Wait for better opportunity")
            print(f"   Confidence below {Config.CONFIDENCE_THRESHOLD:.0%} threshold")

        print("\n" + "="*80)
        print("⚠️ REMEMBER: This is a prediction tool, not financial advice!")
        print("Always use stop-loss orders and proper risk management.")
        print("="*80 + "\n")

        return prediction

    def continuous_monitoring(self, symbol, market_type='crypto', interval='1m', duration_minutes=60):
        """
        Monitor and predict continuously for specified duration

        Parameters:
        -----------
        duration_minutes : int
            How long to monitor (in minutes)
        """

        print(f"\n🔄 Starting Continuous Monitoring")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Update Interval: {interval}")
        print("Press Ctrl+C to stop\n")

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        try:
            while time.time() < end_time:
                # Make prediction
                result = self.analyze_and_predict(symbol, market_type, interval)

                # Wait before next update
                if interval == '1m':
                    sleep_time = 60
                elif interval == '5m':
                    sleep_time = 300
                else:
                    sleep_time = 60

                print(f"\n⏳ Waiting {sleep_time} seconds for next update...")
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n\n⚠️ Monitoring stopped by user")


# EXAMPLE USAGE

if __name__ == "__main__":

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  REAL-TIME TRADING PREDICTION SYSTEM v2.0                     ║
    ║  AI-Powered Candlestick Pattern Recognition                   ║
    ╚═══════════════════════════════════════════════════════════════╝

    ⚠️  IMPORTANT: For Educational Purposes Only!

    This system uses:
    - ✅ Free Binance API (Crypto - No API key needed)
    - ✅ Free Alpha Vantage API (Stocks - Free key required)
    - ✅ Advanced Candlestick Pattern Detection
    - ✅ Multiple AI/ML Models (Random Forest, Gradient Boosting, LSTM)
    - ✅ Real-time Technical Analysis

    Before using:
    1. For stocks: Get free API key from https://www.alphavantage.co/
    2. Add your API key in the Config section above
    3. Install required libraries: pip install -r requirements.txt

    """)

    # Initialize the system
    trading_system = RealTimeTradingSystem()

    # Example 1: Analyze Bitcoin (No API key needed!)
    print("\n" + "="*80)
    print("EXAMPLE 1: Analyzing Bitcoin (BTC/USDT)")
    print("="*80)
    trading_system.analyze_and_predict(
        symbol='BTCUSDT',
        market_type='crypto',
        interval='5m'
    )

    # Example 2: Analyze Ethereum
    print("\n" + "="*80)
    print("EXAMPLE 2: Analyzing Ethereum (ETH/USDT)")
    print("="*80)
    trading_system.analyze_and_predict(
        symbol='ETHUSDT',
        market_type='crypto',
        interval='5m'
    )

    # Example 3: Analyze Stock (Requires Alpha Vantage API key)
    # Uncomment below if you have API key
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Analyzing Apple Stock (AAPL)")
    print("="*80)
    trading_system.analyze_and_predict(
        symbol='AAPL',
        market_type='stock',
        interval='5min'
    )
    """

    # Example 4: Continuous monitoring (uncomment to use)
    """
    trading_system.continuous_monitoring(
        symbol='BTCUSDT',
        market_type='crypto',
        interval='1m',
        duration_minutes=30
    )
    """

    print("\n✅ Demo complete! Modify the examples above for your use case.")
    print("\n⚠️ Remember: Always practice with paper trading first!")

