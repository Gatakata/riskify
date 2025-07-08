"""
Stock Market Prediction Service using Random Forest
Predicts stock price movement direction (up/down) based on technical indicators
"""

import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

class StockPredictionService:
    """Service for stock market prediction using Random Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'current_price', 'volume', 'rsi', 'macd', 'moving_avg_20',
            'moving_avg_50', 'volatility', 'price_change_1d', 'price_change_7d'
        ]
        self._load_model()
    
    def _load_model(self):
        """Load or create Random Forest model for stock prediction"""
        model_path = os.path.join('attached_assets', 'stock_rf_model.pkl')
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                logging.info("Stock prediction model loaded successfully")
            else:
                # Create and train a demo model with synthetic data
                self._create_demo_model()
                logging.info("Created demo stock prediction model")
                
        except Exception as e:
            logging.error(f"Error loading stock model: {str(e)}")
            self._create_demo_model()
    
    def _create_demo_model(self):
        """Create a demo Random Forest model for stock prediction"""
        try:
            # Generate synthetic training data for demonstration
            np.random.seed(42)
            n_samples = 1000
            
            # Generate realistic stock market features
            X = np.random.randn(n_samples, len(self.feature_names))
            
            # Create realistic relationships
            # Higher RSI and MACD tend to predict upward movement
            # Higher volatility creates more uncertainty
            price_up_prob = (
                0.3 + 
                0.2 * (X[:, 2] > 0) +  # RSI effect
                0.2 * (X[:, 3] > 0) +  # MACD effect
                0.1 * (X[:, 1] > 0) -  # Volume effect
                0.1 * np.abs(X[:, 6])  # Volatility reduces predictability
            )
            
            y = np.random.binomial(1, np.clip(price_up_prob, 0.1, 0.9), n_samples)
            
            # Fit scaler and model
            X_scaled = self.scaler.fit_transform(X)
            
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            self.model.fit(X_scaled, y)
            
            # Save model
            model_path = os.path.join('attached_assets', 'stock_rf_model.pkl')
            os.makedirs('attached_assets', exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler
                }, f)
            
            logging.info("Demo stock prediction model created and saved")
            
        except Exception as e:
            logging.error(f"Error creating demo stock model: {str(e)}")
            self.model = None
    
    def _encode_features(self, stock_data: Dict[str, Any]) -> np.ndarray:
        """Encode stock data into feature vector"""
        try:
            features = np.array([
                float(stock_data['current_price']),
                float(stock_data['volume']),
                float(stock_data['rsi']),
                float(stock_data['macd']),
                float(stock_data['moving_avg_20']),
                float(stock_data['moving_avg_50']),
                float(stock_data['volatility']),
                float(stock_data['price_change_1d']),
                float(stock_data['price_change_7d'])
            ])
            
            return self.scaler.transform(features.reshape(1, -1))
            
        except Exception as e:
            logging.error(f"Error encoding stock features: {str(e)}")
            # Return neutral features if encoding fails
            return np.zeros((1, len(self.feature_names)))
    
    def predict(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make stock price direction prediction"""
        try:
            if self.model is None:
                return self._fallback_prediction(stock_data)
            
            # Encode features
            features = self._encode_features(stock_data)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(features)[0]
            prediction = self.model.predict(features)[0]
            
            # Get probabilities for both classes
            down_prob = prediction_proba[0] if len(prediction_proba) > 1 else 1 - prediction_proba[0]
            up_prob = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
            
            # Adjust probabilities based on market indicators
            up_prob = self._adjust_probability(stock_data, up_prob)
            down_prob = 1.0 - up_prob
            
            # Determine prediction and confidence
            predicted_direction = "UP" if up_prob > 0.5 else "DOWN"
            confidence = max(up_prob, down_prob)
            
            # Calculate expected return
            expected_return = self._calculate_expected_return(stock_data, up_prob)
            
            result = {
                'predicted_direction': str(predicted_direction),
                'up_probability': float(round(up_prob, 4)),
                'down_probability': float(round(down_prob, 4)),
                'confidence': float(round(confidence, 4)),
                'expected_return': float(round(expected_return, 4)),
                'model_used': 'Random Forest',
                'risk_level': str(self._calculate_risk_level(confidence, stock_data)),
                'market_signals': self._analyze_market_signals(stock_data)
            }
            
            logging.info(f"Stock prediction: {predicted_direction} with {confidence:.2%} confidence")
            return result
            
        except Exception as e:
            logging.error(f"Stock prediction error: {str(e)}")
            return self._fallback_prediction(stock_data)
    
    def _adjust_probability(self, stock_data: Dict[str, Any], raw_probability: float) -> float:
        """Adjust model probability based on market indicators"""
        try:
            adjusted_prob = raw_probability
            
            # RSI adjustments
            rsi = float(stock_data['rsi'])
            if rsi > 70:  # Overbought
                adjusted_prob *= 0.8
            elif rsi < 30:  # Oversold
                adjusted_prob *= 1.2
            
            # MACD adjustments
            macd = float(stock_data['macd'])
            if macd > 0:
                adjusted_prob *= 1.1
            else:
                adjusted_prob *= 0.9
            
            # Volume adjustments
            volume = float(stock_data['volume'])
            avg_volume = 1000000  # Assume average volume
            if volume > avg_volume * 1.5:  # High volume
                adjusted_prob *= 1.05
            
            # Moving average trend
            ma_20 = float(stock_data['moving_avg_20'])
            ma_50 = float(stock_data['moving_avg_50'])
            if ma_20 > ma_50:  # Bullish trend
                adjusted_prob *= 1.1
            else:  # Bearish trend
                adjusted_prob *= 0.9
            
            # Volatility adjustments
            volatility = float(stock_data['volatility'])
            if volatility > 0.3:  # High volatility
                # Pull towards 0.5 (more uncertain)
                adjusted_prob = 0.5 + (adjusted_prob - 0.5) * 0.8
            
            return np.clip(adjusted_prob, 0.05, 0.95)
            
        except Exception as e:
            logging.error(f"Error adjusting stock probability: {str(e)}")
            return raw_probability
    
    def _calculate_expected_return(self, stock_data: Dict[str, Any], up_prob: float) -> float:
        """Calculate expected return based on prediction and volatility"""
        try:
            volatility = float(stock_data['volatility'])
            current_price = float(stock_data['current_price'])
            
            # Expected daily return based on direction probability and volatility
            up_return = volatility * 0.8  # Expected gain if up
            down_return = -volatility * 0.6  # Expected loss if down
            
            expected_return = (up_prob * up_return) + ((1 - up_prob) * down_return)
            return expected_return
            
        except Exception as e:
            logging.error(f"Error calculating expected return: {str(e)}")
            return 0.0
    
    def _calculate_risk_level(self, confidence: float, stock_data: Dict[str, Any]) -> str:
        """Calculate risk level for the stock prediction"""
        try:
            volatility = float(stock_data['volatility'])
            
            if confidence > 0.8 and volatility < 0.2:
                return "LOW"
            elif confidence > 0.7 and volatility < 0.3:
                return "MEDIUM"
            elif confidence > 0.6:
                return "HIGH"
            else:
                return "VERY_HIGH"
                
        except Exception as e:
            logging.error(f"Error calculating risk level: {str(e)}")
            return "HIGH"
    
    def _analyze_market_signals(self, stock_data: Dict[str, Any]) -> list:
        """Analyze market signals from the stock data"""
        signals = []
        
        try:
            rsi = float(stock_data['rsi'])
            macd = float(stock_data['macd'])
            ma_20 = float(stock_data['moving_avg_20'])
            ma_50 = float(stock_data['moving_avg_50'])
            volatility = float(stock_data['volatility'])
            
            if rsi > 70:
                signals.append("Overbought (RSI > 70)")
            elif rsi < 30:
                signals.append("Oversold (RSI < 30)")
            
            if macd > 0:
                signals.append("Bullish MACD")
            else:
                signals.append("Bearish MACD")
            
            if ma_20 > ma_50:
                signals.append("Golden Cross (MA20 > MA50)")
            else:
                signals.append("Death Cross (MA20 < MA50)")
            
            if volatility > 0.3:
                signals.append("High Volatility")
            elif volatility < 0.1:
                signals.append("Low Volatility")
            
        except Exception as e:
            logging.error(f"Error analyzing market signals: {str(e)}")
            signals.append("Unable to analyze signals")
        
        return signals
    
    def _fallback_prediction(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction when model is not available"""
        try:
            # Simple rule-based prediction
            rsi = float(stock_data['rsi'])
            macd = float(stock_data['macd'])
            
            bullish_signals = 0
            if rsi < 30:  # Oversold
                bullish_signals += 1
            if macd > 0:  # Positive MACD
                bullish_signals += 1
            
            up_prob = 0.3 + (bullish_signals * 0.2)  # Base 30% + signals
            
            return {
                'predicted_direction': "UP" if up_prob > 0.5 else "DOWN",
                'up_probability': round(up_prob, 4),
                'down_probability': round(1 - up_prob, 4),
                'confidence': 0.6,
                'expected_return': 0.0,
                'model_used': 'Rule-Based Fallback',
                'risk_level': 'HIGH',
                'market_signals': ['Model unavailable - using basic rules']
            }
            
        except Exception as e:
            logging.error(f"Fallback prediction error: {str(e)}")
            return {
                'predicted_direction': "HOLD",
                'up_probability': 0.5,
                'down_probability': 0.5,
                'confidence': 0.5,
                'expected_return': 0.0,
                'model_used': 'Error Fallback',
                'risk_level': 'VERY_HIGH',
                'market_signals': ['Prediction error occurred']
            }
    
    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self.model is not None