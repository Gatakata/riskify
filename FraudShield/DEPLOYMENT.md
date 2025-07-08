# Riskify Deployment Guide

## Pre-Deployment Checklist

### Required Files ✅
- `main.py` - Application entry point
- `app.py` - Main Flask application
- `Procfile` - Gunicorn configuration for Render
- `runtime.txt` - Python version specification
- `deploy-requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `.gitignore` - Git ignore patterns

### Environment Variables Required
- `SESSION_SECRET` - Flask session secret key (generate a secure random string)
- `DATABASE_URL` - PostgreSQL connection string (provided by Render)

## GitHub Setup

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Riskify AI Risk Management Platform"
   git branch -M main
   git remote add origin https://github.com/yourusername/riskify.git
   git push -u origin main
   ```

2. **Repository Structure**
   ```
   riskify/
   ├── main.py                    # ✅ Entry point
   ├── app.py                     # ✅ Flask app
   ├── Procfile                   # ✅ Deployment config
   ├── runtime.txt                # ✅ Python version
   ├── deploy-requirements.txt    # ✅ Dependencies
   ├── README.md                  # ✅ Documentation
   ├── .gitignore                 # ✅ Git ignore
   ├── auth_models.py             # ✅ Authentication
   ├── auth_forms.py              # ✅ Forms
   ├── models.py                  # ✅ Data models
   ├── forms.py                   # ✅ Prediction forms
   ├── ml_service.py              # ✅ ML services
   ├── templates/                 # ✅ HTML templates
   ├── static/                    # ✅ Static assets
   └── attached_assets/           # ✅ ML model files
   ```

## Render Deployment

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub account

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Choose your riskify repository

### Step 3: Configuration
- **Name**: `riskify-ai-platform`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r deploy-requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
- **Instance Type**: `Free` (for testing) or `Starter` (for production)

### Step 4: Environment Variables
Add these in Render dashboard:
- `SESSION_SECRET`: Generate using `python -c "import secrets; print(secrets.token_hex(32))"`
- `DATABASE_URL`: Add PostgreSQL database (Render will auto-generate)

### Step 5: Add PostgreSQL Database
1. In Render dashboard, click "New" → "PostgreSQL"
2. Name: `riskify-database`
3. Copy the connection string to `DATABASE_URL` environment variable

### Step 6: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Monitor build logs for any issues

## Post-Deployment

### Verification Steps
1. **Check Application Status**: Green "Live" status in Render
2. **Test Authentication**: Try demo accounts
3. **Test AI Models**: Submit test predictions
4. **Download PDF**: Verify presentation download works

### Demo Accounts for Testing
- **Risk Manager**: `admin` / `admin123`
- **Market Risk Analyst**: `market_analyst` / `market123`
- **Credit Risk Analyst**: `credit_analyst` / `credit123`
- **Operational Risk Analyst**: `ops_analyst` / `ops123`

### Monitoring
- Check Render logs for errors
- Monitor application performance
- Set up alerts for downtime (Render Pro feature)

## Troubleshooting

### Common Issues
1. **Build Failures**: Check `deploy-requirements.txt` for missing dependencies
2. **Database Connection**: Verify `DATABASE_URL` environment variable
3. **Session Issues**: Ensure `SESSION_SECRET` is set
4. **Model Loading**: Check that ML model files are included in repository

### Log Access
- Render Dashboard → Your Service → Logs
- Real-time monitoring of application output

## Production Considerations

### Security
- Use strong `SESSION_SECRET` (32+ characters)
- Enable HTTPS (automatic on Render)
- Consider rate limiting for API endpoints

### Performance
- Upgrade to Starter plan for better performance
- Consider caching for ML model predictions
- Monitor database performance

### Scaling
- Render auto-scales based on traffic
- Consider database connection pooling
- Monitor memory usage with large ML models

## Support
For deployment issues:
- Check Render documentation
- Review application logs
- Contact: Takunda Mcdonald Gatakata (0775919353/0718111419)

---
**Note**: Make sure to copy `deploy-requirements.txt` to `requirements.txt` in your GitHub repository for standard Python deployment practices.