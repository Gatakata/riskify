"""
Loan Default Prediction Service using XGBoost
Predicts probability of loan default based on borrower characteristics
"""

import logging
import numpy as np
import pandas as pd
import xgboost as xgb
import pickle
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

class LoanDefaultPredictionService:
    """Service for loan default prediction using XGBoost"""
    
    def __init__(self):
        self.model = None
        self.feature_names = [
            'loan_amount', 'annual_income', 'credit_score', 'debt_to_income',
            'loan_term', 'employment_years', 'home_ownership', 'loan_purpose'
        ]
        self._load_model()
    
    def _load_model(self):
        """Load or create XGBoost model for loan default prediction"""
        model_path = os.path.join('attached_assets', 'loan_xgb_model.pkl')
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logging.info("Loan default prediction model loaded successfully")
            else:
                # Create and train a demo model with synthetic data
                self._create_demo_model()
                logging.info("Created demo loan default prediction model")
                
        except Exception as e:
            logging.error(f"Error loading loan model: {str(e)}")
            self._create_demo_model()
    
    def _create_demo_model(self):
        """Create a demo XGBoost model for loan default prediction"""
        try:
            # Generate synthetic training data for demonstration
            np.random.seed(42)
            n_samples = 2000
            
            # Generate realistic loan features
            loan_amount = np.random.lognormal(10, 0.8, n_samples)  # $10k-$50k typical
            annual_income = np.random.lognormal(11, 0.6, n_samples)  # $30k-$150k
            credit_score = np.random.normal(650, 80, n_samples).clip(300, 850)
            debt_to_income = np.random.beta(2, 5, n_samples) * 0.6  # 0-60%
            loan_term = np.random.choice([12, 24, 36, 48, 60], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1])
            employment_years = np.random.exponential(3, n_samples).clip(0, 30)
            home_ownership = np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.4, 0.2])  # 0=rent, 1=own, 2=mortgage
            loan_purpose = np.random.choice([0, 1, 2, 3], n_samples, p=[0.3, 0.2, 0.3, 0.2])  # 0=debt_consolidation, 1=home, 2=auto, 3=other
            
            X = np.column_stack([
                loan_amount, annual_income, credit_score, debt_to_income,
                loan_term, employment_years, home_ownership, loan_purpose
            ])
            
            # Create realistic default probability based on financial logic
            default_prob = (
                0.02 +  # Base default rate
                0.15 * (credit_score < 600) / 850 +  # Low credit score
                0.20 * (debt_to_income > 0.4) +  # High debt-to-income
                0.10 * (loan_amount / annual_income > 0.3) +  # High loan-to-income
                0.05 * (employment_years < 2) +  # Short employment
                0.05 * (loan_term > 48) / 60  # Long term loans
            )
            
            y = np.random.binomial(1, np.clip(default_prob, 0.01, 0.4), n_samples)
            
            # Train XGBoost model
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            )
            
            self.model.fit(X, y)
            
            # Save model
            model_path = os.path.join('attached_assets', 'loan_xgb_model.pkl')
            os.makedirs('attached_assets', exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            logging.info("Demo loan default prediction model created and saved")
            
        except Exception as e:
            logging.error(f"Error creating demo loan model: {str(e)}")
            self.model = None
    
    def _encode_features(self, loan_data: Dict[str, Any]) -> np.ndarray:
        """Encode loan data into feature vector"""
        try:
            # Map categorical values
            home_ownership_map = {'rent': 0, 'own': 1, 'mortgage': 2}
            loan_purpose_map = {
                'debt_consolidation': 0,
                'home_improvement': 1,
                'auto': 2,
                'other': 3
            }
            
            features = np.array([
                float(loan_data['loan_amount']),
                float(loan_data['annual_income']),
                float(loan_data['credit_score']),
                float(loan_data['debt_to_income']),
                float(loan_data['loan_term']),
                float(loan_data['employment_years']),
                home_ownership_map.get(loan_data['home_ownership'], 0),
                loan_purpose_map.get(loan_data['loan_purpose'], 3)
            ])
            
            return features.reshape(1, -1)
            
        except Exception as e:
            logging.error(f"Error encoding loan features: {str(e)}")
            # Return neutral features if encoding fails
            return np.array([[25000, 50000, 650, 0.3, 36, 5, 0, 0]])
    
    def predict(self, loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make loan default prediction"""
        try:
            if self.model is None:
                return self._fallback_prediction(loan_data)
            
            # Encode features
            features = self._encode_features(loan_data)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(features)[0]
            prediction = self.model.predict(features)[0]
            
            # Get probabilities
            safe_prob = prediction_proba[0] if len(prediction_proba) > 1 else 1 - prediction_proba[0]
            default_prob = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
            
            # Adjust probabilities based on loan characteristics
            default_prob = self._adjust_probability(loan_data, default_prob)
            safe_prob = 1.0 - default_prob
            
            # Determine risk level and recommendation
            risk_level = self._calculate_risk_level(default_prob)
            recommendation = self._get_recommendation(default_prob, loan_data)
            
            # Calculate suggested interest rate
            suggested_rate = self._calculate_interest_rate(default_prob, loan_data)
            
            result = {
                'default_probability': float(round(default_prob, 4)),
                'safe_probability': float(round(safe_prob, 4)),
                'is_high_risk': bool(default_prob > 0.15),
                'risk_level': str(risk_level),
                'recommendation': str(recommendation),
                'confidence': float(round(max(safe_prob, default_prob), 4)),
                'suggested_interest_rate': float(round(suggested_rate, 2)),
                'model_used': 'XGBoost',
                'risk_factors': self._identify_risk_factors(loan_data),
                'loan_score': int(self._calculate_loan_score(default_prob))
            }
            
            logging.info(f"Loan prediction: {risk_level} risk with {default_prob:.2%} default probability")
            return result
            
        except Exception as e:
            logging.error(f"Loan prediction error: {str(e)}")
            return self._fallback_prediction(loan_data)
    
    def _adjust_probability(self, loan_data: Dict[str, Any], raw_probability: float) -> float:
        """Adjust model probability based on loan characteristics"""
        try:
            adjusted_prob = raw_probability
            
            # Loan-to-Income ratio check (CRITICAL RISK FACTOR)
            loan_amount = float(loan_data['loan_amount'])
            annual_income = float(loan_data['annual_income'])
            loan_to_income_ratio = loan_amount / annual_income
            
            if loan_to_income_ratio > 1.0:  # Loan exceeds annual income
                adjusted_prob = max(adjusted_prob, 0.8)  # Force high risk (at least 80%)
                adjusted_prob *= 2.0  # Double the existing risk
            elif loan_to_income_ratio > 0.5:  # Loan is more than half of income
                adjusted_prob *= 1.4  # Significant increase in risk
            elif loan_to_income_ratio < 0.2:  # Conservative loan amount
                adjusted_prob *= 0.7  # Reduce risk for conservative borrowing
            
            # Credit score adjustments
            credit_score = float(loan_data['credit_score'])
            if credit_score < 580:
                adjusted_prob *= 1.5  # Increase risk for poor credit
            elif credit_score > 750:
                adjusted_prob *= 0.7  # Decrease risk for excellent credit
            
            # Debt-to-income adjustments
            dti = float(loan_data['debt_to_income'])
            if dti > 0.4:
                adjusted_prob *= 1.3  # High DTI increases risk
            elif dti < 0.2:
                adjusted_prob *= 0.8  # Low DTI decreases risk
            
            # Employment stability
            employment_years = float(loan_data['employment_years'])
            if employment_years < 2:
                adjusted_prob *= 1.2  # Short employment history
            elif employment_years > 10:
                adjusted_prob *= 0.9  # Stable employment
            
            # Home ownership
            if loan_data['home_ownership'] == 'own':
                adjusted_prob *= 0.85  # Homeowners typically lower risk
            
            return np.clip(adjusted_prob, 0.01, 0.95)  # Allow up to 95% default risk
            
        except Exception as e:
            logging.error(f"Error adjusting loan probability: {str(e)}")
            return raw_probability
    
    def _calculate_risk_level(self, default_prob: float) -> str:
        """Calculate risk level based on default probability"""
        if default_prob < 0.05:
            return "LOW"
        elif default_prob < 0.15:
            return "MEDIUM"
        elif default_prob < 0.3:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _get_recommendation(self, default_prob: float, loan_data: Dict[str, Any]) -> str:
        """Get loan recommendation based on risk assessment"""
        if default_prob < 0.05:
            return "APPROVE - Excellent candidate"
        elif default_prob < 0.1:
            return "APPROVE - Good candidate with standard terms"
        elif default_prob < 0.2:
            return "APPROVE with conditions - Higher interest rate recommended"
        elif default_prob < 0.3:
            return "REVIEW REQUIRED - High risk, consider additional security"
        else:
            return "DECLINE - Unacceptable risk level"
    
    def _calculate_interest_rate(self, default_prob: float, loan_data: Dict[str, Any]) -> float:
        """Calculate suggested interest rate based on risk"""
        try:
            # Base rate (current market rate assumption)
            base_rate = 8.0
            
            # Risk premium based on default probability
            risk_premium = default_prob * 15  # Up to 15% premium for highest risk
            
            # Credit score adjustment
            credit_score = float(loan_data['credit_score'])
            if credit_score > 750:
                credit_adjustment = -1.0  # Premium for excellent credit
            elif credit_score < 600:
                credit_adjustment = 2.0   # Penalty for poor credit
            else:
                credit_adjustment = 0.0
            
            # Loan term adjustment (longer terms = higher rates)
            loan_term = float(loan_data['loan_term'])
            term_adjustment = (loan_term - 36) * 0.05  # 0.05% per month over 36
            
            suggested_rate = base_rate + risk_premium + credit_adjustment + term_adjustment
            
            return max(6.0, min(suggested_rate, 25.0))  # Cap between 6% and 25%
            
        except Exception as e:
            logging.error(f"Error calculating interest rate: {str(e)}")
            return 12.0  # Default rate
    
    def _identify_risk_factors(self, loan_data: Dict[str, Any]) -> list:
        """Identify key risk factors for the loan"""
        risk_factors = []
        
        try:
            credit_score = float(loan_data['credit_score'])
            dti = float(loan_data['debt_to_income'])
            employment_years = float(loan_data['employment_years'])
            loan_amount = float(loan_data['loan_amount'])
            annual_income = float(loan_data['annual_income'])
            
            if credit_score < 650:
                risk_factors.append(f"Below average credit score ({credit_score})")
            
            if dti > 0.36:
                risk_factors.append(f"High debt-to-income ratio ({dti:.1%})")
            
            if employment_years < 3:
                risk_factors.append(f"Short employment history ({employment_years:.1f} years)")
            
            loan_to_income_ratio = loan_amount / annual_income
            if loan_to_income_ratio > 1.0:
                risk_factors.append(f"CRITICAL: Loan amount (${loan_amount:,.0f}) exceeds annual income (${annual_income:,.0f})")
            elif loan_to_income_ratio > 0.5:
                risk_factors.append(f"High loan-to-income ratio ({loan_to_income_ratio:.1%})")
            elif loan_to_income_ratio > 0.4:
                risk_factors.append("Moderate loan amount relative to income")
            
            loan_term = float(loan_data['loan_term'])
            if loan_term > 48:
                risk_factors.append(f"Long loan term ({loan_term} months)")
            
            if loan_data['home_ownership'] == 'rent':
                risk_factors.append("Renter (no property ownership)")
            
            if not risk_factors:
                risk_factors.append("Low risk profile")
                
        except Exception as e:
            logging.error(f"Error identifying risk factors: {str(e)}")
            risk_factors.append("Unable to assess risk factors")
        
        return risk_factors
    
    def _calculate_loan_score(self, default_prob: float) -> int:
        """Calculate a loan score (higher is better) based on default probability"""
        # Convert default probability to score (300-850 range like credit scores)
        score = int(850 - (default_prob * 550))
        return max(300, min(score, 850))
    
    def _fallback_prediction(self, loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction when model is not available"""
        try:
            # Simple rule-based assessment
            credit_score = float(loan_data['credit_score'])
            dti = float(loan_data['debt_to_income'])
            
            # Basic risk calculation
            if credit_score >= 700 and dti <= 0.3:
                default_prob = 0.08
            elif credit_score >= 650 and dti <= 0.4:
                default_prob = 0.15
            else:
                default_prob = 0.25
            
            return {
                'default_probability': round(default_prob, 4),
                'safe_probability': round(1 - default_prob, 4),
                'is_high_risk': default_prob > 0.15,
                'risk_level': self._calculate_risk_level(default_prob),
                'recommendation': self._get_recommendation(default_prob, loan_data),
                'confidence': 0.6,
                'suggested_interest_rate': 12.0,
                'model_used': 'Rule-Based Fallback',
                'risk_factors': ['Model unavailable - using basic assessment'],
                'loan_score': self._calculate_loan_score(default_prob)
            }
            
        except Exception as e:
            logging.error(f"Fallback prediction error: {str(e)}")
            return {
                'default_probability': 0.2,
                'safe_probability': 0.8,
                'is_high_risk': True,
                'risk_level': 'HIGH',
                'recommendation': 'REVIEW REQUIRED - Assessment error',
                'confidence': 0.5,
                'suggested_interest_rate': 15.0,
                'model_used': 'Error Fallback',
                'risk_factors': ['Prediction error occurred'],
                'loan_score': 500
            }
    
    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self.model is not None