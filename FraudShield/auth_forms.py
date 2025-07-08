"""
Authentication forms for Riskify login and signup
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from auth_models import UserRole, user_store

class LoginForm(FlaskForm):
    """Login form for user authentication"""
    
    username_or_email = StringField(
        'Username or Email',
        validators=[
            DataRequired(message='Username or email is required'),
            Length(min=3, max=80, message='Must be between 3 and 80 characters')
        ],
        render_kw={
            'placeholder': 'Enter username or email',
            'class': 'form-control',
            'autocomplete': 'username'
        }
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters')
        ],
        render_kw={
            'placeholder': 'Enter password',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }
    )
    
    submit = SubmitField(
        'Sign In',
        render_kw={'class': 'btn btn-primary btn-lg w-100'}
    )

class SignupForm(FlaskForm):
    """Signup form for new user registration"""
    
    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Full name is required'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ],
        render_kw={
            'placeholder': 'Enter your full name',
            'class': 'form-control'
        }
    )
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=30, message='Username must be between 3 and 30 characters')
        ],
        render_kw={
            'placeholder': 'Choose a username',
            'class': 'form-control',
            'autocomplete': 'username'
        }
    )
    
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address'),
            Length(max=120, message='Email must be less than 120 characters')
        ],
        render_kw={
            'placeholder': 'Enter your email address',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    role = SelectField(
        'Role',
        choices=[
            (UserRole.RISK_MANAGER.value, 'Risk Manager - Full System Access'),
            (UserRole.MARKET_RISK_ANALYST.value, 'Market Risk Analyst - Stock Prediction Only'),
            (UserRole.CREDIT_RISK_ANALYST.value, 'Credit Risk Analyst - Loan Assessment Only'),
            (UserRole.OPERATIONAL_RISK_ANALYST.value, 'Operational Risk Analyst - Fraud Detection Only')
        ],
        validators=[DataRequired(message='Please select a role')],
        render_kw={'class': 'form-select'}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, max=128, message='Password must be between 6 and 128 characters')
        ],
        render_kw={
            'placeholder': 'Create a password (min 6 characters)',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={
            'placeholder': 'Re-enter your password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    submit = SubmitField(
        'Create Account',
        render_kw={'class': 'btn btn-success btn-lg w-100'}
    )
    
    def validate_username(self, field):
        """Custom validation for username uniqueness"""
        if user_store.get_user_by_username(field.data):
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, field):
        """Custom validation for email uniqueness"""
        if user_store.get_user_by_email(field.data):
            raise ValidationError('Email already registered. Please use a different email or sign in.')