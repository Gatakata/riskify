import os
from datetime import datetime
from enum import Enum
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TransactionStatus(Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    PENDING = "pending"
    FLAGGED = "flagged"

class DatabaseConnection:
    """PostgreSQL database connection manager"""
    
    def __init__(self):
        self.connection_string = os.environ.get('DATABASE_URL')
        if not self.connection_string:
            logging.warning("DATABASE_URL not set, using fallback connection")
            # Fallback for development - check if we have individual PostgreSQL environment variables
            pguser = os.environ.get('PGUSER')
            pgpassword = os.environ.get('PGPASSWORD') 
            pghost = os.environ.get('PGHOST')
            pgport = os.environ.get('PGPORT')
            pgdatabase = os.environ.get('PGDATABASE')
            
            if all([pguser, pgpassword, pghost, pgport, pgdatabase]):
                self.connection_string = f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"
            else:
                # Fall back to in-memory storage if no database available
                self.use_database = False
                logging.warning("No database configuration found, using in-memory storage")
                return
        
        self.use_database = True
        self._create_tables()
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS transactions (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            amount DECIMAL(12,2) NOT NULL,
                            merchant_category VARCHAR(50) NOT NULL,
                            customer_age INTEGER NOT NULL,
                            fraud_probability DECIMAL(5,4) NOT NULL,
                            is_fraud BOOLEAN NOT NULL,
                            confidence DECIMAL(5,4) NOT NULL,
                            model_used VARCHAR(50) NOT NULL,
                            status VARCHAR(20) NOT NULL,
                            risk_level VARCHAR(20) NOT NULL,
                            transaction_data JSONB NOT NULL,
                            risk_factors TEXT[]
                        )
                    """)
                    
                    # Create indexes for better performance
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_transactions_timestamp 
                        ON transactions(timestamp DESC)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_transactions_fraud 
                        ON transactions(is_fraud)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_transactions_risk_level 
                        ON transactions(risk_level)
                    """)
                    
                conn.commit()
                logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {str(e)}")
            raise

class Transaction:
    """Transaction model for storing fraud analysis results"""
    
    def __init__(self):
        self.transactions = []  # In-memory fallback
        self.id_counter = 1
        
        # Check if database should be used
        use_db_env = os.environ.get('USE_DATABASE', 'true').lower()
        if use_db_env in ['false', '0', 'no']:
            self.use_database = False
            logging.info("Database disabled by environment variable. Using in-memory storage.")
            return
        
        # Try to initialize database connection
        try:
            self.db = DatabaseConnection()
            with self.db.get_connection() as conn:
                logging.info("Database connection successful")
            self.use_database = True
        except Exception as e:
            logging.warning(f"Database connection failed: {str(e)}. Using in-memory storage.")
            self.use_database = False
    
    def save_transaction(self, transaction_data, prediction_result, status=TransactionStatus.PENDING):
        """Save transaction analysis to database or in-memory storage"""
        if self.use_database:
            return self._save_to_database(transaction_data, prediction_result, status)
        else:
            return self._save_to_memory(transaction_data, prediction_result, status)
    
    def _save_to_database(self, transaction_data, prediction_result, status):
        """Save transaction to PostgreSQL database"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    risk_level = self._calculate_risk_level(prediction_result['fraud_probability'])
                    risk_factors = self._identify_risk_factors(transaction_data)
                    
                    cursor.execute("""
                        INSERT INTO transactions (
                            amount, merchant_category, customer_age, fraud_probability,
                            is_fraud, confidence, model_used, status, risk_level,
                            transaction_data, risk_factors
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """, (
                        float(transaction_data['transaction_amount']),
                        str(transaction_data['merchant_category']),
                        int(transaction_data['customer_age']),
                        float(prediction_result['fraud_probability']),
                        bool(prediction_result['is_fraud']),
                        float(prediction_result['confidence']),
                        str(prediction_result['model_used']),
                        str(status.value),
                        str(risk_level),
                        json.dumps(transaction_data),
                        risk_factors
                    ))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # Convert to dict format for compatibility
                    transaction_record = dict(result)
                    transaction_record['timestamp'] = transaction_record['timestamp'].isoformat()
                    if isinstance(transaction_record['transaction_data'], str):
                        transaction_record['transaction_data'] = json.loads(transaction_record['transaction_data'])
                    # transaction_data might already be a dict from the database
                    
                    logging.info(f"Transaction {transaction_record['id']} saved to database")
                    return transaction_record
                    
        except Exception as e:
            logging.error(f"Error saving transaction to database: {str(e)}")
            raise
    
    def _save_to_memory(self, transaction_data, prediction_result, status):
        """Save transaction to in-memory storage"""
        transaction_record = {
            'id': self.id_counter,
            'timestamp': datetime.now().isoformat(),
            'amount': transaction_data['transaction_amount'],
            'merchant_category': transaction_data['merchant_category'],
            'customer_age': transaction_data['customer_age'],
            'fraud_probability': prediction_result['fraud_probability'],
            'is_fraud': prediction_result['is_fraud'],
            'confidence': prediction_result['confidence'],
            'model_used': prediction_result['model_used'],
            'status': status.value,
            'risk_level': self._calculate_risk_level(prediction_result['fraud_probability']),
            'transaction_data': transaction_data,
            'risk_factors': self._identify_risk_factors(transaction_data)
        }
        
        self.transactions.append(transaction_record)
        self.id_counter += 1
        logging.info(f"Transaction {transaction_record['id']} saved to memory")
        return transaction_record
    
    def get_all_transactions(self):
        """Get all transactions sorted by timestamp"""
        if self.use_database:
            return self._get_all_from_database()
        else:
            return sorted(self.transactions, key=lambda x: x['timestamp'], reverse=True)
    
    def _get_all_from_database(self):
        """Get all transactions from database"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM transactions 
                        ORDER BY timestamp DESC
                    """)
                    
                    results = cursor.fetchall()
                    transactions = []
                    
                    for row in results:
                        transaction = dict(row)
                        transaction['timestamp'] = transaction['timestamp'].isoformat()
                        if isinstance(transaction['transaction_data'], str):
                            transaction['transaction_data'] = json.loads(transaction['transaction_data'])
                        # transaction_data might already be a dict from PostgreSQL JSONB
                        transactions.append(transaction)
                    
                    return transactions
                    
        except Exception as e:
            logging.error(f"Error fetching all transactions: {str(e)}")
            return []
    
    def get_transaction_by_id(self, transaction_id):
        """Get specific transaction by ID"""
        if self.use_database:
            return self._get_transaction_from_database(transaction_id)
        else:
            for transaction in self.transactions:
                if transaction['id'] == transaction_id:
                    return transaction
            return None
    
    def _get_transaction_from_database(self, transaction_id):
        """Get transaction from database by ID"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM transactions WHERE id = %s
                    """, (transaction_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        transaction = dict(result)
                        transaction['timestamp'] = transaction['timestamp'].isoformat()
                        if isinstance(transaction['transaction_data'], str):
                            transaction['transaction_data'] = json.loads(transaction['transaction_data'])
                        # transaction_data might already be a dict from PostgreSQL JSONB
                        return transaction
                    
                    return None
                    
        except Exception as e:
            logging.error(f"Error fetching transaction {transaction_id}: {str(e)}")
            return None
    
    def get_fraud_statistics(self):
        """Calculate fraud detection statistics"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get basic statistics
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_transactions,
                            COUNT(*) FILTER (WHERE is_fraud = true) as fraud_detected,
                            COUNT(*) FILTER (WHERE risk_level IN ('high', 'critical')) as high_risk_count,
                            COALESCE(SUM(amount), 0) as total_amount_processed,
                            COALESCE(AVG(amount), 0) as average_amount
                        FROM transactions
                    """)
                    
                    result = cursor.fetchone()
                    
                    if result and result[0] > 0:
                        total, fraud_detected, high_risk_count, total_amount, avg_amount = result
                        fraud_rate = round((fraud_detected / total) * 100, 2) if total > 0 else 0
                        
                        return {
                            'total_transactions': total,
                            'fraud_detected': fraud_detected,
                            'fraud_rate': fraud_rate,
                            'average_amount': round(float(avg_amount), 2),
                            'high_risk_count': high_risk_count,
                            'total_amount_processed': round(float(total_amount), 2)
                        }
                    else:
                        return {
                            'total_transactions': 0,
                            'fraud_detected': 0,
                            'fraud_rate': 0,
                            'average_amount': 0,
                            'high_risk_count': 0,
                            'total_amount_processed': 0
                        }
                        
        except Exception as e:
            logging.error(f"Error calculating fraud statistics: {str(e)}")
            return {
                'total_transactions': 0,
                'fraud_detected': 0,
                'fraud_rate': 0,
                'average_amount': 0,
                'high_risk_count': 0,
                'total_amount_processed': 0
            }
    
    def get_recent_alerts(self, limit=10):
        """Get recent high-risk transactions"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM transactions 
                        WHERE risk_level IN ('high', 'critical') OR fraud_probability > 0.7
                        ORDER BY timestamp DESC
                        LIMIT %s
                    """, (limit,))
                    
                    results = cursor.fetchall()
                    alerts = []
                    
                    for row in results:
                        alert = dict(row)
                        alert['timestamp'] = alert['timestamp'].isoformat()
                        alert['transaction_data'] = json.loads(alert['transaction_data'])
                        alerts.append(alert)
                    
                    return alerts
                    
        except Exception as e:
            logging.error(f"Error fetching recent alerts: {str(e)}")
            return []
    
    def _calculate_risk_level(self, fraud_probability):
        """Calculate risk level based on fraud probability"""
        if fraud_probability >= 0.8:
            return 'critical'
        elif fraud_probability >= 0.6:
            return 'high'
        elif fraud_probability >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _identify_risk_factors(self, transaction_data):
        """Identify key risk factors for the transaction"""
        risk_factors = []
        
        if transaction_data['transaction_amount'] > 5000:
            risk_factors.append('High transaction amount')
        
        if transaction_data['previous_failed_attempts'] > 3:
            risk_factors.append('Multiple failed attempts')
        
        if transaction_data['merchant_risk_score'] > 0.7:
            risk_factors.append('High merchant risk')
        
        if transaction_data['location_risk_score'] > 0.5:
            risk_factors.append('High location risk')
        
        if transaction_data['device_risk_score'] > 0.5:
            risk_factors.append('High device risk')
        
        hour = transaction_data['transaction_hour']
        if hour < 6 or hour > 22:
            risk_factors.append('Unusual transaction time')
        
        if transaction_data['transaction_frequency_24h'] > 10:
            risk_factors.append('High transaction frequency')
        
        return risk_factors

# Global transaction store instance
transaction_store = Transaction()