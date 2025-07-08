import os
import pickle
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional

class FraudDetectionService:
    """Service for loading and using XGBoost fraud detection model"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.feature_names = [
            'transaction_amount',
            'merchant_category_encoded',
            'transaction_hour',
            'transaction_day',
            'customer_age',
            'account_age_days',
            'previous_failed_attempts',
            'merchant_risk_score',
            'transaction_frequency_24h',
            'avg_transaction_amount_30d',
            'location_risk_score',
            'device_risk_score'
        ]
        self.merchant_category_mapping = {
            'grocery': 0,
            'gas_station': 1,
            'restaurant': 2,
            'retail': 3,
            'online': 4,
            'atm': 5,
            'pharmacy': 6,
            'hotel': 7,
            'entertainment': 8,
            'other': 9
        }
        self._load_model()
    
    def _load_model(self):
        """Load the XGBoost model from pickle file"""
        try:
            # Try to load the model from the uploaded file
            model_paths = [
                'attached_assets/xgb_model_1751364025628.pkl',
                'xgb_model_1751364025628.pkl',
                'xgb_model.pkl'
            ]
            
            for model_path in model_paths:
                if os.path.exists(model_path):
                    logging.info(f"Loading model from {model_path}")
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    self.model_loaded = True
                    logging.info("XGBoost model loaded successfully")
                    return
            
            # If no model file found, log warning but continue
            logging.warning("No XGBoost model file found. Predictions will use fallback logic.")
            self.model_loaded = False
            
        except Exception as e:
            logging.error(f"Error loading XGBoost model: {str(e)}")
            self.model_loaded = False
    
    def _encode_features(self, transaction_data: Dict[str, Any]) -> np.ndarray:
        """Encode transaction data into feature vector - using 8 features to match loaded model"""
        features = []
        
        # Use 8-feature format to match the loaded XGBoost model
        features.append(transaction_data['transaction_amount'])
        merchant_category = transaction_data['merchant_category']
        features.append(self.merchant_category_mapping.get(merchant_category, 9))
        features.append(transaction_data['transaction_hour'])
        features.append(transaction_data['customer_age'])
        features.append(transaction_data['previous_failed_attempts'])
        features.append(transaction_data['merchant_risk_score'])
        features.append(transaction_data['location_risk_score'])
        features.append(transaction_data['device_risk_score'])
        
        return np.array(features).reshape(1, -1)
    
    def _fallback_prediction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction logic when model is not available"""
        logging.info("Using fallback prediction logic")
        
        # Simple rule-based fraud detection for fallback
        risk_score = 0.0
        
        # High amount transactions
        if transaction_data['transaction_amount'] > 5000:
            risk_score += 0.3
        
        # Multiple failed attempts
        if transaction_data['previous_failed_attempts'] > 3:
            risk_score += 0.4
        
        # High merchant risk
        if transaction_data['merchant_risk_score'] > 0.7:
            risk_score += 0.3
        
        # High transaction frequency
        if transaction_data['transaction_frequency_24h'] > 10:
            risk_score += 0.2
        
        # Unusual hours (late night/early morning)
        hour = transaction_data['transaction_hour']
        if hour < 6 or hour > 23:
            risk_score += 0.1
        
        # High location risk
        if transaction_data['location_risk_score'] > 0.5:
            risk_score += 0.2
        
        # High device risk
        if transaction_data['device_risk_score'] > 0.5:
            risk_score += 0.2
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        is_fraud = risk_score > 0.5
        confidence = risk_score if is_fraud else (1.0 - risk_score)
        
        return {
            'is_fraud': bool(is_fraud),
            'fraud_probability': float(risk_score),
            'confidence': float(confidence),
            'model_used': 'fallback_rules'
        }
    
    def predict(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make fraud prediction for transaction"""
        try:
            if not self.model_loaded or self.model is None:
                logging.info("Model not loaded, using fallback prediction")
                return self._fallback_prediction(transaction_data)
            
            # Encode features
            features = self._encode_features(transaction_data)
            logging.info(f"Encoded features: {features}")
            
            # Make prediction
            try:
                prediction_proba = self.model.predict_proba(features)
                logging.info(f"Model prediction probabilities: {prediction_proba}")
                
                # Check if prediction returns expected format
                if len(prediction_proba[0]) >= 2:
                    fraud_probability = prediction_proba[0][1]  # Probability of fraud class
                else:
                    logging.warning("Unexpected model output format, using fallback")
                    return self._fallback_prediction(transaction_data)
                
            except Exception as model_error:
                logging.error(f"Model prediction failed: {str(model_error)}")
                return self._fallback_prediction(transaction_data)
            
            # Apply some sanity checks and adjustments
            fraud_probability = max(0.0, min(1.0, float(fraud_probability)))
            
            # Make the model less aggressive - adjust probability based on input values
            adjusted_probability = self._adjust_probability(transaction_data, fraud_probability)
            
            is_fraud = adjusted_probability > 0.5
            
            # Calculate confidence (distance from decision boundary)
            confidence = abs(adjusted_probability - 0.5) * 2
            
            result = {
                'is_fraud': bool(is_fraud),
                'fraud_probability': float(adjusted_probability),
                'confidence': float(confidence),
                'model_used': 'xgboost'
            }
            
            logging.info(f"Final prediction: {result}")
            return result
            
        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            # Fall back to rule-based prediction
            return self._fallback_prediction(transaction_data)
    
    def _adjust_probability(self, transaction_data: Dict[str, Any], raw_probability: float) -> float:
        """Adjust model probability to be more realistic based on input characteristics"""
        adjusted = raw_probability
        
        # Reduce probability for low-risk characteristics
        if transaction_data['transaction_amount'] < 100:
            adjusted *= 0.7  # Lower amounts are typically less risky
            
        if transaction_data['customer_age'] > 50:
            adjusted *= 0.8  # Older customers may be lower risk
            
        if transaction_data['account_age_days'] > 365:
            adjusted *= 0.6  # Established accounts are lower risk
            
        if transaction_data['previous_failed_attempts'] == 0:
            adjusted *= 0.5  # No previous failures is good
            
        if transaction_data['merchant_risk_score'] < 0.3:
            adjusted *= 0.7  # Low merchant risk
            
        if transaction_data['location_risk_score'] < 0.2:
            adjusted *= 0.8  # Low location risk
            
        if transaction_data['device_risk_score'] < 0.2:
            adjusted *= 0.8  # Low device risk
            
        # Increase probability for high-risk characteristics
        if transaction_data['transaction_amount'] > 5000:
            adjusted *= 1.3  # High amounts increase risk
            
        if transaction_data['previous_failed_attempts'] > 2:
            adjusted *= 1.5  # Multiple failures increase risk
            
        if transaction_data['merchant_risk_score'] > 0.7:
            adjusted *= 1.4  # High merchant risk
            
        # Transaction timing adjustments
        hour = transaction_data['transaction_hour']
        if hour < 6 or hour > 23:
            adjusted *= 1.2  # Unusual hours slightly increase risk
        else:
            adjusted *= 0.9  # Normal hours reduce risk
            
        # Ensure we stay within bounds
        return max(0.0, min(1.0, adjusted))
    
    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self.model_loaded and self.model is not None
