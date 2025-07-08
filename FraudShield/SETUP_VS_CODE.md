# Running Fraud Detection App in VS Code

## Prerequisites
- Python 3.8+
- VS Code with Python extension
- PostgreSQL (optional - app falls back to in-memory storage)

## Local Setup Instructions

### 1. Download Project Files
Copy these files from the Replit project to your local machine:
- `app.py` - Main Flask application
- `main.py` - Entry point
- `forms.py` - Form definitions
- `ml_service.py` - ML prediction service
- `models.py` - Database models
- `templates/` folder - All HTML templates
- `static/` folder - CSS, JavaScript, and assets
- `attached_assets/xgb_model_1751364025628.pkl` - XGBoost model file

### 2. Install Dependencies
```bash
pip install Flask==3.0.0
pip install Flask-WTF==1.2.1
pip install WTForms==3.1.1
pip install XGBoost==2.0.3
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install psycopg2-binary==2.9.9
pip install email-validator==2.1.0
pip install gunicorn==21.2.0
pip install scikit-learn==1.3.2
```

Or create a `requirements.txt` file with the above packages and run:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in your project root:
```env
SESSION_SECRET=your-secret-key-here-change-this
DATABASE_URL=postgresql://username:password@localhost:5432/frauddb
FLASK_ENV=development
FLASK_DEBUG=true
```

### 4. Database Setup (Optional)
If you want to use PostgreSQL:
```bash
# Install PostgreSQL locally
# Create database
createdb frauddb

# The app will create tables automatically
```

**Note:** The app works without PostgreSQL - it automatically falls back to in-memory storage.

### 5. Run the Application

**Recommended Method for VS Code (No Database Required):**
```bash
python run_local.py
```

**Alternative Methods:**
```bash
# Method 1: Direct Flask
python main.py

# Method 2: Flask command
export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000

# Method 3: With Gunicorn
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

**For Database-Free Development:**
Set environment variable before running:
```bash
export USE_DATABASE=false
python main.py
```

### 6. Access the Application
Open your browser and go to: `http://localhost:5000`

## VS Code Configuration

### Launch Configuration
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

### Workspace Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "__pycache__/": true,
        "*.pyc": true
    }
}
```

## Project Structure
```
fraud-detection-app/
├── app.py                  # Main Flask app
├── main.py                 # Entry point
├── forms.py                # Form definitions
├── ml_service.py           # ML prediction service
├── models.py               # Database models
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── prediction.html
│   ├── dashboard.html
│   └── ...
├── static/                 # Static assets
│   ├── css/style.css
│   └── js/main.js
├── attached_assets/        # ML model files
│   └── xgb_model_*.pkl
└── .env                    # Environment variables
```

## Testing the Application

### Low Risk Transaction Test:
- Amount: $50
- Merchant: Grocery Store
- Customer Age: 45
- Account Age: 500 days
- Risk Scores: 0.1

### High Risk Transaction Test:
- Amount: $8000
- Merchant: Online Purchase
- Failed Attempts: 5
- Hour: 2 (2 AM)
- Risk Scores: 0.8+

## Features Available
- ✅ Real-time fraud detection
- ✅ Analytics dashboard
- ✅ Transaction history
- ✅ Batch CSV processing
- ✅ REST API endpoints
- ✅ Database persistence (PostgreSQL or in-memory)
- ✅ Responsive Stripe-inspired design

## Troubleshooting

### Common Issues:
1. **Model not found**: Ensure `xgb_model_*.pkl` is in `attached_assets/` folder
2. **Database errors**: App falls back to in-memory storage automatically
3. **Port conflicts**: Change port in run command if 5000 is taken
4. **Import errors**: Make sure all dependencies are installed

### Debug Mode:
Add this to your code for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

The application includes comprehensive error handling and will provide detailed logs to help troubleshoot any issues.