from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class TransactionForm(FlaskForm):
    """Form for transaction fraud detection input"""
    
    # Transaction details
    transaction_amount = FloatField(
        'Transaction Amount ($)',
        validators=[
            DataRequired(message='Transaction amount is required'),
            NumberRange(min=0.01, max=100000, message='Amount must be between $0.01 and $100,000')
        ],
        render_kw={'placeholder': '0.00', 'step': '0.01', 'class': 'form-control'}
    )
    
    merchant_category = SelectField(
        'Merchant Category',
        choices=[
            ('grocery', 'Grocery Store'),
            ('gas_station', 'Gas Station'),
            ('restaurant', 'Restaurant'),
            ('retail', 'Retail Store'),
            ('online', 'Online Purchase'),
            ('atm', 'ATM Withdrawal'),
            ('pharmacy', 'Pharmacy'),
            ('hotel', 'Hotel/Travel'),
            ('entertainment', 'Entertainment'),
            ('other', 'Other')
        ],
        validators=[DataRequired(message='Please select a merchant category')],
        render_kw={'class': 'form-select'}
    )
    
    # Time-based features
    transaction_hour = IntegerField(
        'Transaction Hour (0-23)',
        validators=[
            DataRequired(message='Transaction hour is required'),
            NumberRange(min=0, max=23, message='Hour must be between 0 and 23')
        ],
        render_kw={'placeholder': '14', 'class': 'form-control'}
    )
    
    transaction_day = IntegerField(
        'Day of Week (1=Monday, 7=Sunday)',
        validators=[
            DataRequired(message='Day of week is required'),
            NumberRange(min=1, max=7, message='Day must be between 1 and 7')
        ],
        render_kw={'placeholder': '3', 'class': 'form-control'}
    )
    
    # Customer profile features
    customer_age = IntegerField(
        'Customer Age',
        validators=[
            DataRequired(message='Customer age is required'),
            NumberRange(min=18, max=120, message='Age must be between 18 and 120')
        ],
        render_kw={'placeholder': '35', 'class': 'form-control'}
    )
    
    account_age_days = IntegerField(
        'Account Age (Days)',
        validators=[
            DataRequired(message='Account age is required'),
            NumberRange(min=0, max=36500, message='Account age must be positive')
        ],
        render_kw={'placeholder': '365', 'class': 'form-control'}
    )
    
    # Risk indicators
    previous_failed_attempts = IntegerField(
        'Previous Failed Attempts (Last 30 days)',
        validators=[
            DataRequired(message='Failed attempts count is required'),
            NumberRange(min=0, max=100, message='Failed attempts must be between 0 and 100')
        ],
        render_kw={'placeholder': '0', 'class': 'form-control'}
    )
    
    merchant_risk_score = FloatField(
        'Merchant Risk Score (0.0-1.0)',
        validators=[
            DataRequired(message='Merchant risk score is required'),
            NumberRange(min=0.0, max=1.0, message='Risk score must be between 0.0 and 1.0')
        ],
        render_kw={'placeholder': '0.1', 'step': '0.01', 'class': 'form-control'}
    )
    
    transaction_frequency_24h = IntegerField(
        'Transaction Frequency (Last 24h)',
        validators=[
            DataRequired(message='Transaction frequency is required'),
            NumberRange(min=0, max=50, message='Frequency must be between 0 and 50')
        ],
        render_kw={'placeholder': '2', 'class': 'form-control'}
    )
    
    avg_transaction_amount_30d = FloatField(
        'Average Transaction Amount (Last 30 days)',
        validators=[
            DataRequired(message='Average transaction amount is required'),
            NumberRange(min=0.01, max=50000, message='Amount must be between $0.01 and $50,000')
        ],
        render_kw={'placeholder': '125.50', 'step': '0.01', 'class': 'form-control'}
    )
    
    location_risk_score = FloatField(
        'Location Risk Score (0.0-1.0)',
        validators=[
            DataRequired(message='Location risk score is required'),
            NumberRange(min=0.0, max=1.0, message='Risk score must be between 0.0 and 1.0')
        ],
        render_kw={'placeholder': '0.05', 'step': '0.01', 'class': 'form-control'}
    )
    
    device_risk_score = FloatField(
        'Device Risk Score (0.0-1.0)',
        validators=[
            DataRequired(message='Device risk score is required'),
            NumberRange(min=0.0, max=1.0, message='Risk score must be between 0.0 and 1.0')
        ],
        render_kw={'placeholder': '0.02', 'step': '0.01', 'class': 'form-control'}
    )
    
    submit = SubmitField('Analyze Transaction', render_kw={'class': 'btn btn-primary btn-lg w-100'})
    
    def validate_transaction_amount(self, field):
        """Custom validation for transaction amount"""
        if field.data and field.data <= 0:
            raise ValidationError('Transaction amount must be greater than 0')
    
    def validate_merchant_risk_score(self, field):
        """Custom validation for merchant risk score"""
        if field.data is not None and (field.data < 0 or field.data > 1):
            raise ValidationError('Merchant risk score must be between 0.0 and 1.0')


class StockPredictionForm(FlaskForm):
    """Form for stock market prediction input"""
    
    current_price = FloatField(
        'Current Stock Price ($)',
        validators=[
            DataRequired(message='Current price is required'),
            NumberRange(min=0.01, max=10000, message='Price must be between $0.01 and $10,000')
        ],
        render_kw={'placeholder': '150.25', 'step': '0.01', 'class': 'form-control'}
    )
    
    volume = IntegerField(
        'Daily Volume',
        validators=[
            DataRequired(message='Volume is required'),
            NumberRange(min=1, max=100000000, message='Volume must be positive')
        ],
        render_kw={'placeholder': '1000000', 'class': 'form-control'}
    )
    
    rsi = FloatField(
        'RSI (Relative Strength Index)',
        validators=[
            DataRequired(message='RSI is required'),
            NumberRange(min=0, max=100, message='RSI must be between 0 and 100')
        ],
        render_kw={'placeholder': '65.5', 'step': '0.1', 'class': 'form-control'}
    )
    
    macd = FloatField(
        'MACD (Moving Average Convergence Divergence)',
        validators=[
            DataRequired(message='MACD is required'),
            NumberRange(min=-50, max=50, message='MACD must be between -50 and 50')
        ],
        render_kw={'placeholder': '2.3', 'step': '0.1', 'class': 'form-control'}
    )
    
    moving_avg_20 = FloatField(
        '20-Day Moving Average ($)',
        validators=[
            DataRequired(message='20-day MA is required'),
            NumberRange(min=0.01, max=10000, message='MA must be between $0.01 and $10,000')
        ],
        render_kw={'placeholder': '148.50', 'step': '0.01', 'class': 'form-control'}
    )
    
    moving_avg_50 = FloatField(
        '50-Day Moving Average ($)',
        validators=[
            DataRequired(message='50-day MA is required'),
            NumberRange(min=0.01, max=10000, message='MA must be between $0.01 and $10,000')
        ],
        render_kw={'placeholder': '145.75', 'step': '0.01', 'class': 'form-control'}
    )
    
    volatility = FloatField(
        'Volatility (0.0-1.0)',
        validators=[
            DataRequired(message='Volatility is required'),
            NumberRange(min=0.0, max=1.0, message='Volatility must be between 0.0 and 1.0')
        ],
        render_kw={'placeholder': '0.25', 'step': '0.01', 'class': 'form-control'}
    )
    
    price_change_1d = FloatField(
        '1-Day Price Change (%)',
        validators=[
            DataRequired(message='1-day price change is required'),
            NumberRange(min=-50, max=50, message='Price change must be between -50% and 50%')
        ],
        render_kw={'placeholder': '2.5', 'step': '0.1', 'class': 'form-control'}
    )
    
    price_change_7d = FloatField(
        '7-Day Price Change (%)',
        validators=[
            DataRequired(message='7-day price change is required'),
            NumberRange(min=-50, max=50, message='Price change must be between -50% and 50%')
        ],
        render_kw={'placeholder': '5.2', 'step': '0.1', 'class': 'form-control'}
    )
    
    submit = SubmitField('Predict Stock Movement', render_kw={'class': 'btn btn-success btn-lg w-100'})


class LoanDefaultForm(FlaskForm):
    """Form for loan default prediction input"""
    
    loan_amount = FloatField(
        'Loan Amount ($)',
        validators=[
            DataRequired(message='Loan amount is required'),
            NumberRange(min=1000, max=500000, message='Loan amount must be between $1,000 and $500,000')
        ],
        render_kw={'placeholder': '25000', 'step': '100', 'class': 'form-control'}
    )
    
    annual_income = FloatField(
        'Annual Income ($)',
        validators=[
            DataRequired(message='Annual income is required'),
            NumberRange(min=10000, max=1000000, message='Income must be between $10,000 and $1,000,000')
        ],
        render_kw={'placeholder': '75000', 'step': '1000', 'class': 'form-control'}
    )
    
    credit_score = IntegerField(
        'Credit Score',
        validators=[
            DataRequired(message='Credit score is required'),
            NumberRange(min=300, max=850, message='Credit score must be between 300 and 850')
        ],
        render_kw={'placeholder': '720', 'class': 'form-control'}
    )
    
    debt_to_income = FloatField(
        'Debt-to-Income Ratio (0.0-1.0)',
        validators=[
            DataRequired(message='Debt-to-income ratio is required'),
            NumberRange(min=0.0, max=1.0, message='DTI must be between 0.0 and 1.0')
        ],
        render_kw={'placeholder': '0.35', 'step': '0.01', 'class': 'form-control'}
    )
    
    loan_term = IntegerField(
        'Loan Term (months)',
        validators=[
            DataRequired(message='Loan term is required'),
            NumberRange(min=12, max=84, message='Loan term must be between 12 and 84 months')
        ],
        render_kw={'placeholder': '48', 'class': 'form-control'}
    )
    
    employment_years = FloatField(
        'Employment Years',
        validators=[
            DataRequired(message='Employment years is required'),
            NumberRange(min=0, max=50, message='Employment years must be between 0 and 50')
        ],
        render_kw={'placeholder': '5.5', 'step': '0.5', 'class': 'form-control'}
    )
    
    home_ownership = SelectField(
        'Home Ownership',
        choices=[
            ('rent', 'Rent'),
            ('own', 'Own'),
            ('mortgage', 'Mortgage')
        ],
        validators=[DataRequired(message='Please select home ownership status')],
        render_kw={'class': 'form-select'}
    )
    
    loan_purpose = SelectField(
        'Loan Purpose',
        choices=[
            ('debt_consolidation', 'Debt Consolidation'),
            ('home_improvement', 'Home Improvement'),
            ('auto', 'Auto Purchase'),
            ('other', 'Other')
        ],
        validators=[DataRequired(message='Please select loan purpose')],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField('Assess Loan Risk', render_kw={'class': 'btn btn-warning btn-lg w-100'})
