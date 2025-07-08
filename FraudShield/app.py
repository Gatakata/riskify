import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from forms import TransactionForm, StockPredictionForm, LoanDefaultForm
from auth_forms import LoginForm, SignupForm
from auth_models import user_store, UserRole
from profile_forms import ProfileUpdateForm
from ml_service import FraudDetectionService
from stock_ml_service import StockPredictionService
from loan_ml_service import LoanDefaultPredictionService
from models import transaction_store, TransactionStatus
from pdf_generator import RiskifyPDFGenerator
import json
import io
import csv

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return user_store.get_user_by_id(user_id)

# Role-based access control decorator
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for(current_user.get_dashboard_url()))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize ML services
fraud_service = FraudDetectionService()
stock_service = StockPredictionService()
loan_service = LoanDefaultPredictionService()

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for(current_user.get_dashboard_url()))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = user_store.authenticate_user(
            form.username_or_email.data,
            form.password.data
        )
        
        if user:
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Redirect to user's appropriate dashboard
            next_page = request.args.get('next')
            if next_page and user.can_access(next_page.strip('/')):
                return redirect(next_page)
            return redirect(url_for(user.get_dashboard_url()))
        else:
            flash('Invalid username/email or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for(current_user.get_dashboard_url()))
    
    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = user_store.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                role=UserRole(form.role.data),
                full_name=form.full_name.data
            )
            
            login_user(user)
            flash(f'Account created successfully! Welcome, {user.full_name}!', 'success')
            return redirect(url_for(user.get_dashboard_url()))
            
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    user_name = current_user.full_name
    logout_user()
    flash(f'You have been logged out successfully. Goodbye, {user_name}!', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Update user information
        updated_user = user_store.update_user(
            current_user.id,
            full_name=form.full_name.data,
            email=form.email.data,
            password=form.new_password.data if form.new_password.data else None
        )
        
        if updated_user:
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Error updating profile. Please try again.', 'error')
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    
    return render_template('profile.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main landing page - shows welcome page for anonymous users, dashboard for logged-in users"""
    if current_user.is_authenticated:
        # For Risk Managers, show the full system home page
        if current_user.role == UserRole.RISK_MANAGER:
            return render_template('home.html', user=current_user)
        else:
            # For other roles, redirect to their specific dashboard
            return redirect(url_for(current_user.get_dashboard_url()))
    else:
        # Show public landing page for non-authenticated users
        return render_template('welcome.html')

@app.route('/fraud', methods=['GET', 'POST'])
@role_required(UserRole.RISK_MANAGER, UserRole.OPERATIONAL_RISK_ANALYST)
def fraud_detection():
    """Fraud detection page with transaction form"""
    form = TransactionForm()
    
    if form.validate_on_submit():
        try:
            # Extract form data
            transaction_data = {
                'transaction_amount': float(form.transaction_amount.data),
                'merchant_category': form.merchant_category.data,
                'transaction_hour': int(form.transaction_hour.data),
                'transaction_day': int(form.transaction_day.data),
                'customer_age': int(form.customer_age.data),
                'account_age_days': int(form.account_age_days.data),
                'previous_failed_attempts': int(form.previous_failed_attempts.data),
                'merchant_risk_score': float(form.merchant_risk_score.data),
                'transaction_frequency_24h': int(form.transaction_frequency_24h.data),
                'avg_transaction_amount_30d': float(form.avg_transaction_amount_30d.data),
                'location_risk_score': float(form.location_risk_score.data),
                'device_risk_score': float(form.device_risk_score.data)
            }
            
            # Make prediction
            prediction_result = fraud_service.predict(transaction_data)
            
            # Save transaction to history
            status = TransactionStatus.DECLINED if prediction_result['is_fraud'] else TransactionStatus.APPROVED
            saved_transaction = transaction_store.save_transaction(transaction_data, prediction_result, status)
            
            # Store prediction in session for download
            session['last_fraud_prediction'] = {
                'prediction': prediction_result,
                'transaction_data': transaction_data,
                'transaction': saved_transaction,
                'timestamp': datetime.now().isoformat()
            }
            
            return render_template('prediction.html', 
                                 result=prediction_result, 
                                 transaction_data=transaction_data,
                                 transaction_id=saved_transaction['id'])
                                 
        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            flash(f'Error processing transaction: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template('fraud.html', form=form)

@app.route('/stock', methods=['GET', 'POST'])
@role_required(UserRole.RISK_MANAGER, UserRole.MARKET_RISK_ANALYST)
def stock_prediction():
    """Stock market prediction page"""
    form = StockPredictionForm()
    
    if form.validate_on_submit():
        try:
            # Extract form data
            stock_data = {
                'current_price': form.current_price.data,
                'volume': form.volume.data,
                'rsi': form.rsi.data,
                'macd': form.macd.data,
                'moving_avg_20': form.moving_avg_20.data,
                'moving_avg_50': form.moving_avg_50.data,
                'volatility': form.volatility.data,
                'price_change_1d': form.price_change_1d.data,
                'price_change_7d': form.price_change_7d.data
            }
            
            # Make prediction
            prediction_result = stock_service.predict(stock_data)
            
            # Store prediction in session for download
            session['last_stock_prediction'] = {
                'prediction': prediction_result,
                'stock_data': stock_data,
                'timestamp': datetime.now().isoformat()
            }
            
            return render_template('stock_prediction.html', 
                                prediction=prediction_result,
                                stock_data=stock_data)
                                
        except Exception as e:
            flash(f"Error processing stock prediction: {str(e)}", 'error')
            logging.error(f"Stock prediction error: {str(e)}")
    
    return render_template('stock.html', form=form)

@app.route('/loan', methods=['GET', 'POST'])
@role_required(UserRole.RISK_MANAGER, UserRole.CREDIT_RISK_ANALYST)
def loan_prediction():
    """Loan default prediction page"""
    form = LoanDefaultForm()
    
    if form.validate_on_submit():
        try:
            # Extract form data
            loan_data = {
                'loan_amount': form.loan_amount.data,
                'annual_income': form.annual_income.data,
                'credit_score': form.credit_score.data,
                'debt_to_income': form.debt_to_income.data,
                'loan_term': form.loan_term.data,
                'employment_years': form.employment_years.data,
                'home_ownership': form.home_ownership.data,
                'loan_purpose': form.loan_purpose.data
            }
            
            # Make prediction
            prediction_result = loan_service.predict(loan_data)
            
            # Store prediction in session for download
            session['last_loan_prediction'] = {
                'prediction': prediction_result,
                'loan_data': loan_data,
                'timestamp': datetime.now().isoformat()
            }
            
            return render_template('loan_prediction.html', 
                                prediction=prediction_result,
                                loan_data=loan_data)
                                
        except Exception as e:
            flash(f"Error processing loan prediction: {str(e)}", 'error')
            logging.error(f"Loan prediction error: {str(e)}")
    
    return render_template('loan.html', form=form)

@app.route('/dashboard')
@role_required(UserRole.RISK_MANAGER, UserRole.OPERATIONAL_RISK_ANALYST)
def dashboard():
    """Analytics dashboard with fraud statistics"""
    stats = transaction_store.get_fraud_statistics()
    recent_transactions = transaction_store.get_all_transactions()[:10]
    alerts = transaction_store.get_recent_alerts(5)
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_transactions=recent_transactions,
                         alerts=alerts)

@app.route('/history')
@role_required(UserRole.RISK_MANAGER, UserRole.OPERATIONAL_RISK_ANALYST)
def transaction_history():
    """Transaction history page"""
    transactions = transaction_store.get_all_transactions()
    return render_template('history.html', transactions=transactions)

@app.route('/transaction/<int:transaction_id>')
def transaction_detail(transaction_id):
    """Detailed view of a specific transaction"""
    transaction = transaction_store.get_transaction_by_id(transaction_id)
    if not transaction:
        flash('Transaction not found', 'error')
        return redirect(url_for('transaction_history'))
    
    return render_template('transaction_detail.html', transaction=transaction)

@app.route('/api/transactions')
def api_transactions():
    """API endpoint for transaction data"""
    transactions = transaction_store.get_all_transactions()
    return jsonify(transactions)

@app.route('/api/stats')
def api_stats():
    """API endpoint for fraud statistics"""
    stats = transaction_store.get_fraud_statistics()
    return jsonify(stats)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for fraud prediction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['transaction_amount', 'merchant_category', 'transaction_hour', 
                          'customer_age', 'previous_failed_attempts', 'merchant_risk_score',
                          'location_risk_score', 'device_risk_score']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add default values for optional fields
        transaction_data = {
            'transaction_amount': float(data['transaction_amount']),
            'merchant_category': data['merchant_category'],
            'transaction_hour': int(data['transaction_hour']),
            'transaction_day': int(data.get('transaction_day', 3)),
            'customer_age': int(data['customer_age']),
            'account_age_days': int(data.get('account_age_days', 365)),
            'previous_failed_attempts': int(data['previous_failed_attempts']),
            'merchant_risk_score': float(data['merchant_risk_score']),
            'transaction_frequency_24h': int(data.get('transaction_frequency_24h', 1)),
            'avg_transaction_amount_30d': float(data.get('avg_transaction_amount_30d', 100.0)),
            'location_risk_score': float(data['location_risk_score']),
            'device_risk_score': float(data['device_risk_score'])
        }
        
        # Make prediction
        prediction_result = fraud_service.predict(transaction_data)
        
        # Save transaction
        status = TransactionStatus.DECLINED if prediction_result['is_fraud'] else TransactionStatus.APPROVED
        saved_transaction = transaction_store.save_transaction(transaction_data, prediction_result, status)
        
        return jsonify({
            'transaction_id': saved_transaction['id'],
            'prediction': prediction_result
        })
        
    except Exception as e:
        logging.error(f"API prediction error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/export/csv')
def export_csv():
    """Export transaction history as CSV"""
    transactions = transaction_store.get_all_transactions()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Timestamp', 'Amount', 'Merchant Category', 'Customer Age', 
                    'Fraud Probability', 'Is Fraud', 'Confidence', 'Status', 'Risk Level'])
    
    # Write data
    for transaction in transactions:
        writer.writerow([
            transaction['id'],
            transaction['timestamp'],
            transaction['amount'],
            transaction['merchant_category'],
            transaction['customer_age'],
            f"{transaction['fraud_probability']:.3f}",
            transaction['is_fraud'],
            f"{transaction['confidence']:.3f}",
            transaction['status'],
            transaction['risk_level']
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'fraud_transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/batch-analysis', methods=['GET', 'POST'])
@role_required(UserRole.RISK_MANAGER, UserRole.OPERATIONAL_RISK_ANALYST)
def batch_analysis():
    """Batch processing for multiple transactions"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV data
                csv_data = file.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_data))
                
                results = []
                for row in csv_reader:
                    try:
                        transaction_data = {
                            'transaction_amount': float(row.get('amount', 0)),
                            'merchant_category': row.get('merchant_category', 'other'),
                            'transaction_hour': int(row.get('hour', 12)),
                            'transaction_day': int(row.get('day', 3)),
                            'customer_age': int(row.get('customer_age', 35)),
                            'account_age_days': int(row.get('account_age_days', 365)),
                            'previous_failed_attempts': int(row.get('failed_attempts', 0)),
                            'merchant_risk_score': float(row.get('merchant_risk_score', 0.1)),
                            'transaction_frequency_24h': int(row.get('frequency_24h', 1)),
                            'avg_transaction_amount_30d': float(row.get('avg_amount_30d', 100)),
                            'location_risk_score': float(row.get('location_risk_score', 0.05)),
                            'device_risk_score': float(row.get('device_risk_score', 0.02))
                        }
                        
                        prediction_result = fraud_service.predict(transaction_data)
                        status = TransactionStatus.DECLINED if prediction_result['is_fraud'] else TransactionStatus.APPROVED
                        saved_transaction = transaction_store.save_transaction(transaction_data, prediction_result, status)
                        
                        results.append({
                            'row_data': row,
                            'prediction': prediction_result,
                            'transaction_id': saved_transaction['id']
                        })
                        
                    except Exception as e:
                        logging.error(f"Error processing row: {str(e)}")
                        continue
                
                flash(f'Successfully processed {len(results)} transactions', 'success')
                return render_template('batch_results.html', results=results)
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('batch_analysis.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    model_status = fraud_service.is_model_loaded()
    return jsonify({
        'status': 'healthy' if model_status else 'model_not_loaded',
        'model_loaded': model_status,
        'total_transactions': len(transaction_store.get_all_transactions())
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', 
                         title='Page Not Found',
                         content='<div class="alert alert-warning">Page not found</div>'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return render_template('base.html', 
                         title='Server Error',
                         content='<div class="alert alert-danger">Internal server error occurred</div>'), 500

# Download report routes
@app.route('/download/fraud-report')
def download_fraud_report():
    """Download fraud detection report as PDF/text"""
    if 'last_fraud_prediction' not in session:
        flash('No recent fraud prediction to download', 'error')
        return redirect(url_for('fraud_detection'))
    
    data = session['last_fraud_prediction']
    prediction = data['prediction']
    transaction_data = data['transaction_data']
    timestamp = data['timestamp']
    
    # Generate PDF report
    pdf_generator = RiskifyPDFGenerator()
    pdf_content = pdf_generator.generate_fraud_report(prediction, transaction_data, timestamp)
    
    # Create response
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=fraud_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response

@app.route('/download/stock-report')
def download_stock_report():
    """Download stock prediction report"""
    if 'last_stock_prediction' not in session:
        flash('No recent stock prediction to download', 'error')
        return redirect(url_for('stock_prediction'))
    
    data = session['last_stock_prediction']
    prediction = data['prediction']
    stock_data = data['stock_data']
    timestamp = data['timestamp']
    
    report_content = f"""RISKIFY - STOCK MARKET PREDICTION REPORT
Generated: {timestamp}

=== PREDICTION RESULTS ===
Predicted Direction: {prediction['predicted_direction']}
Confidence Level: {prediction['confidence']:.1%}
Up Probability: {prediction['up_probability']:.1%}
Down Probability: {prediction['down_probability']:.1%}
Expected Return: {prediction['expected_return']:.2%}
Risk Level: {prediction['risk_level']}

=== INPUT DATA ===
Current Price: ${stock_data['current_price']:.2f}
Volume: {stock_data['volume']:,}
RSI: {stock_data['rsi']:.1f}
MACD: {stock_data['macd']:.2f}
20-Day MA: ${stock_data['moving_avg_20']:.2f}
50-Day MA: ${stock_data['moving_avg_50']:.2f}
Volatility: {stock_data['volatility']:.1%}
1-Day Change: {stock_data['price_change_1d']:.1f}%
7-Day Change: {stock_data['price_change_7d']:.1f}%

=== MARKET SIGNALS ===
{chr(10).join([f"• {signal}" for signal in prediction.get('market_signals', [])])}

=== MODEL INFORMATION ===
Algorithm: {prediction['model_used']}
Analysis Type: Technical Indicator Analysis

---
Report generated by Riskify AI Risk Management Platform
Developer: Takunda Mcdonald Gatakata (Data Science and Systems)
"""
    
    # Generate PDF report
    pdf_generator = RiskifyPDFGenerator()
    pdf_content = pdf_generator.generate_stock_report(prediction, stock_data, timestamp)
    
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=stock_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response

@app.route('/download/loan-report')
def download_loan_report():
    """Download loan assessment report"""
    if 'last_loan_prediction' not in session:
        flash('No recent loan prediction to download', 'error')
        return redirect(url_for('loan_prediction'))
    
    data = session['last_loan_prediction']
    prediction = data['prediction']
    loan_data = data['loan_data']
    timestamp = data['timestamp']
    
    report_content = f"""RISKIFY - LOAN DEFAULT ASSESSMENT REPORT
Generated: {timestamp}

=== RISK ASSESSMENT ===
Default Probability: {prediction['default_probability']:.1%}
Safe Probability: {prediction['safe_probability']:.1%}
Risk Level: {prediction['risk_level']}
Loan Score: {prediction['loan_score']}/850
Confidence: {prediction['confidence']:.1%}

=== RECOMMENDATION ===
{prediction['recommendation']}
Suggested Interest Rate: {prediction['suggested_interest_rate']:.2f}% APR

=== APPLICANT DETAILS ===
Loan Amount: ${loan_data['loan_amount']:,.2f}
Annual Income: ${loan_data['annual_income']:,.2f}
Credit Score: {loan_data['credit_score']}
Debt-to-Income Ratio: {loan_data['debt_to_income']:.1%}
Loan Term: {loan_data['loan_term']} months
Employment Years: {loan_data['employment_years']:.1f}
Home Ownership: {loan_data['home_ownership'].title()}
Loan Purpose: {loan_data['loan_purpose'].replace('_', ' ').title()}

=== FINANCIAL RATIOS ===
Loan-to-Income Ratio: {(loan_data['loan_amount']/loan_data['annual_income']*100):.1f}%
Monthly Income: ${loan_data['annual_income']/12:,.2f}

=== RISK FACTORS ===
{chr(10).join([f"• {factor}" for factor in prediction.get('risk_factors', [])])}

=== MODEL INFORMATION ===
Algorithm: {prediction['model_used']}
Assessment Type: Credit Risk Evaluation

---
Report generated by Riskify AI Risk Management Platform
Developer: Takunda Mcdonald Gatakata (Data Science and Systems)
"""
    
    # Generate PDF report
    pdf_generator = RiskifyPDFGenerator()
    pdf_content = pdf_generator.generate_loan_report(prediction, loan_data, timestamp)
    
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=loan_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response

@app.route('/download/presentation')
def download_presentation():
    """Download the comprehensive Riskify system presentation PDF"""
    try:
        # Import the presentation generator
        from presentation_generator import RiskifyPresentationGenerator
        
        # Generate the presentation
        generator = RiskifyPresentationGenerator()
        filename = generator.create_presentation()
        
        # Send the file
        return send_file(
            filename,
            as_attachment=True,
            download_name=f'Riskify_System_Presentation_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"Error generating presentation: {str(e)}")
        flash('Error generating presentation. Please try again.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
