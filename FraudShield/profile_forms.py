"""
User profile forms for Riskify
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError
from auth_models import user_store


class ProfileUpdateForm(FlaskForm):
    """Form for updating user profile information"""
    
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
    
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address'),
            Length(max=120, message='Email must be less than 120 characters')
        ],
        render_kw={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        }
    )
    
    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Current password is required to make changes')
        ],
        render_kw={
            'placeholder': 'Enter your current password',
            'class': 'form-control'
        }
    )
    
    new_password = PasswordField(
        'New Password (Optional)',
        validators=[
            Optional(),
            Length(min=6, max=128, message='New password must be between 6 and 128 characters')
        ],
        render_kw={
            'placeholder': 'Enter new password (leave blank to keep current)',
            'class': 'form-control'
        }
    )
    
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            EqualTo('new_password', message='Passwords must match')
        ],
        render_kw={
            'placeholder': 'Confirm new password',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Update Profile',
        render_kw={'class': 'btn btn-primary btn-lg'}
    )
    
    def validate_email(self, field):
        """Custom validation for email uniqueness (excluding current user)"""
        from flask_login import current_user
        if field.data != current_user.email:
            existing_user = user_store.get_user_by_email(field.data)
            if existing_user:
                raise ValidationError('This email is already registered with another account.')
    
    def validate_current_password(self, field):
        """Custom validation for current password"""
        from flask_login import current_user
        if not current_user.check_password(field.data):
            raise ValidationError('Current password is incorrect.')