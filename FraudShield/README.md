# Riskify - AI Risk Management Platform

Riskify is a comprehensive Flask-based AI risk management platform designed for financial institutions. The application features three specialized machine learning models for fraud detection, stock market prediction, and loan default assessment.

## Features

### 🔐 Role-Based Authentication System
- **Risk Manager**: Full system access to all three AI models
- **Market Risk Analyst**: Stock prediction access only
- **Credit Risk Analyst**: Loan assessment access only  
- **Operational Risk Analyst**: Fraud detection access only

### 🤖 AI Prediction Models
1. **Fraud Detection**: XGBoost model for transaction fraud analysis
2. **Stock Market Prediction**: Random Forest model for price direction prediction
3. **Loan Default Assessment**: XGBoost model for loan default risk evaluation

### 📊 Dashboard & Analytics
- Real-time fraud statistics and alerts
- Transaction history and detailed analysis
- Batch processing for multiple transactions
- Export capabilities (CSV, PDF reports)

### 📋 Professional Documentation
- Comprehensive system presentation (PDF download)
- Detailed input field explanations for all AI models
- User role descriptions and access control documentation

## Demo Accounts

- **Risk Manager**: `admin` / `admin123`
- **Market Risk Analyst**: `market_analyst` / `market123`
- **Credit Risk Analyst**: `credit_analyst` / `credit123`
- **Operational Risk Analyst**: `ops_analyst` / `ops123`

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Machine Learning**: XGBoost, Scikit-learn, Pandas, NumPy
- **Frontend**: Bootstrap 5, Font Awesome, Custom CSS
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: Werkzeug password hashing, session management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd riskify
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export SESSION_SECRET="your-secret-key-here"
export DATABASE_URL="postgresql://user:password@localhost/riskify"
```

4. Run the application:
```bash
python main.py
```

## Deployment

### Render Deployment
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn --bind 0.0.0.0:$PORT main:app`
5. Add environment variables:
   - `SESSION_SECRET`: Generate a secure random string
   - `DATABASE_URL`: Use Render's PostgreSQL add-on

### Environment Variables
- `SESSION_SECRET`: Required for Flask sessions
- `DATABASE_URL`: PostgreSQL connection string

## Project Structure

```
riskify/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── auth_models.py        # User authentication models
├── auth_forms.py         # Authentication forms
├── models.py             # Data models
├── forms.py              # Prediction forms
├── ml_service.py         # ML service implementations
├── templates/            # HTML templates
├── static/               # Static assets
└── attached_assets/      # ML model files
```

## Color Scheme

- **Primary Blue**: #1a365d (Dark blue for headers, navigation)
- **Accent Orange**: #f97316 (Orange for buttons, highlights)
- **Background**: White and light grays
- **Text**: Dark colors for readability

## Developer

**Takunda Mcdonald Gatakata**
- Phone: 0775919353 / 0718111419
- Specialization: Data Science and Systems

## License

This project is proprietary software developed for financial institutions.