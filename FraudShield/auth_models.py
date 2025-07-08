"""
Authentication models for Riskify role-based access control
"""
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid
from datetime import datetime

class UserRole(Enum):
    """User roles with different access levels"""
    RISK_MANAGER = "risk_manager"
    MARKET_RISK_ANALYST = "market_risk_analyst"
    CREDIT_RISK_ANALYST = "credit_risk_analyst"
    OPERATIONAL_RISK_ANALYST = "operational_risk_analyst"

class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, username, email, password_hash, role, full_name=None):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name or username
        self.created_at = datetime.now()
        self.last_login = None
        self._is_active = True
    
    @property
    def is_active(self):
        """Override UserMixin is_active property"""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """Allow setting is_active"""
        self._is_active = value
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_role_display(self):
        """Get user-friendly role name"""
        role_names = {
            UserRole.RISK_MANAGER: "Risk Manager",
            UserRole.MARKET_RISK_ANALYST: "Market Risk Analyst", 
            UserRole.CREDIT_RISK_ANALYST: "Credit Risk Analyst",
            UserRole.OPERATIONAL_RISK_ANALYST: "Operational Risk Analyst"
        }
        return role_names.get(self.role, "Unknown Role")
    
    def get_accessible_pages(self):
        """Get list of pages this user can access"""
        access_map = {
            UserRole.RISK_MANAGER: [
                'index', 'fraud_detection', 'stock_prediction', 'loan_prediction', 
                'dashboard', 'transaction_history', 'batch_analysis'
            ],
            UserRole.MARKET_RISK_ANALYST: [
                'index', 'stock_prediction'
            ],
            UserRole.CREDIT_RISK_ANALYST: [
                'index', 'loan_prediction'
            ],
            UserRole.OPERATIONAL_RISK_ANALYST: [
                'index', 'fraud_detection', 'dashboard', 'transaction_history', 'batch_analysis'
            ]
        }
        return access_map.get(self.role, ['index'])
    
    def can_access(self, page):
        """Check if user can access a specific page"""
        return page in self.get_accessible_pages()
    
    def get_dashboard_url(self):
        """Get the appropriate dashboard URL for this user role"""
        dashboard_map = {
            UserRole.RISK_MANAGER: 'index',  # Full system access
            UserRole.MARKET_RISK_ANALYST: 'stock_prediction',
            UserRole.CREDIT_RISK_ANALYST: 'loan_prediction', 
            UserRole.OPERATIONAL_RISK_ANALYST: 'fraud_detection'
        }
        return dashboard_map.get(self.role, 'index')

class UserStore:
    """In-memory user storage (ready for database upgrade)"""
    
    def __init__(self):
        self.users = {}
        self.users_by_username = {}
        self.users_by_email = {}
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users for testing"""
        default_users = [
            {
                'username': 'admin',
                'email': 'admin@riskify.com',
                'password': 'admin123',
                'role': UserRole.RISK_MANAGER,
                'full_name': 'System Administrator'
            },
            {
                'username': 'market_analyst',
                'email': 'market@riskify.com', 
                'password': 'market123',
                'role': UserRole.MARKET_RISK_ANALYST,
                'full_name': 'Market Risk Analyst'
            },
            {
                'username': 'credit_analyst',
                'email': 'credit@riskify.com',
                'password': 'credit123', 
                'role': UserRole.CREDIT_RISK_ANALYST,
                'full_name': 'Credit Risk Analyst'
            },
            {
                'username': 'ops_analyst',
                'email': 'ops@riskify.com',
                'password': 'ops123',
                'role': UserRole.OPERATIONAL_RISK_ANALYST,
                'full_name': 'Operational Risk Analyst'
            }
        ]
        
        for user_data in default_users:
            self.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data['role'],
                full_name=user_data['full_name']
            )
    
    def create_user(self, username, email, password, role, full_name=None):
        """Create a new user"""
        if username in self.users_by_username:
            raise ValueError("Username already exists")
        
        if email in self.users_by_email:
            raise ValueError("Email already exists")
        
        password_hash = generate_password_hash(password)
        user = User(username, email, password_hash, role, full_name)
        
        self.users[user.id] = user
        self.users_by_username[username] = user
        self.users_by_email[email] = user
        
        return user
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return self.users_by_username.get(username)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.users_by_email.get(email)
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate user by username/email and password"""
        user = self.get_user_by_username(username_or_email)
        if not user:
            user = self.get_user_by_email(username_or_email)
        
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.now()
            return user
        
        return None
    
    def get_all_users(self):
        """Get all users"""
        return list(self.users.values())
    
    def update_user(self, user_id, full_name=None, email=None, password=None):
        """Update user information"""
        if user_id not in self.users:
            return None
            
        user = self.users[user_id]
        
        if full_name:
            user.full_name = full_name
        if email:
            user.email = email
        if password:
            user.password_hash = generate_password_hash(password)
            
        return user

# Global user store instance
user_store = UserStore()