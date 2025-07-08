"""
PDF Report Generation for Riskify
Creates professional PDF reports for fraud detection, stock prediction, and loan assessment
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime
from typing import Dict, Any

class RiskifyPDFGenerator:
    """Generate professional PDF reports for Riskify predictions"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for Riskify branding"""
        # Title style - Dark blue
        self.styles.add(ParagraphStyle(
            name='RiskifyTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style - Dark orange
        self.styles.add(ParagraphStyle(
            name='RiskifySubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#f97316'),
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#1a365d'),
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='RiskifyNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Risk warning style
        self.styles.add(ParagraphStyle(
            name='RiskWarning',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#dc2626'),
            spaceBefore=10,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
    
    def generate_fraud_report(self, prediction: Dict[str, Any], transaction_data: Dict[str, Any], timestamp: str) -> bytes:
        """Generate fraud detection PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch)
        
        story = []
        
        # Header
        story.append(Paragraph("RISKIFY", self.styles['RiskifyTitle']))
        story.append(Paragraph("Fraud Detection Analysis Report", self.styles['RiskifySubtitle']))
        story.append(Paragraph(f"Generated: {timestamp}", self.styles['RiskifyNormal']))
        story.append(Spacer(1, 20))
        
        # Risk Assessment Summary
        risk_level = "HIGH RISK" if prediction.get('is_fraud', False) else "LOW RISK"
        fraud_prob = prediction.get('fraud_probability', 0) * 100
        
        story.append(Paragraph("RISK ASSESSMENT SUMMARY", self.styles['SectionHeader']))
        
        # Create summary table
        summary_data = [
            ['Transaction Status:', risk_level],
            ['Fraud Probability:', f"{fraud_prob:.1f}%"],
            ['Confidence Level:', f"{prediction.get('confidence', 0)*100:.1f}%"],
            ['Model Used:', prediction.get('model_used', 'XGBoost')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Transaction Details
        story.append(Paragraph("TRANSACTION DETAILS", self.styles['SectionHeader']))
        
        transaction_details = [
            ['Amount:', f"${transaction_data.get('transaction_amount', 0):.2f}"],
            ['Merchant Category:', transaction_data.get('merchant_category', 'Unknown')],
            ['Transaction Hour:', f"{transaction_data.get('transaction_hour', 0)}:00"],
            ['Customer Age:', f"{transaction_data.get('customer_age', 0)} years"],
            ['Account Age:', f"{transaction_data.get('account_age_days', 0)} days"],
            ['Failed Attempts (30d):', str(transaction_data.get('previous_failed_attempts', 0))],
            ['Transaction Frequency (24h):', str(transaction_data.get('transaction_frequency_24h', 0))],
            ['Avg Amount (30d):', f"${transaction_data.get('avg_transaction_amount_30d', 0):.2f}"]
        ]
        
        details_table = Table(transaction_details, colWidths=[2.5*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Risk Factors
        if prediction.get('risk_factors'):
            story.append(Paragraph("IDENTIFIED RISK FACTORS", self.styles['SectionHeader']))
            for factor in prediction.get('risk_factors', []):
                story.append(Paragraph(f"• {factor}", self.styles['RiskifyNormal']))
            story.append(Spacer(1, 15))
        
        # Recommendation
        story.append(Paragraph("RECOMMENDATION", self.styles['SectionHeader']))
        recommendation = prediction.get('recommendation', 'Standard processing recommended')
        story.append(Paragraph(recommendation, self.styles['RiskifyNormal']))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Report generated by Riskify AI Risk Management Platform", self.styles['RiskifyNormal']))
        story.append(Paragraph("Developer: Takunda Mcdonald Gatakata (Data Science and Systems)", self.styles['RiskifyNormal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_stock_report(self, prediction: Dict[str, Any], stock_data: Dict[str, Any], timestamp: str) -> bytes:
        """Generate stock prediction PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch)
        
        story = []
        
        # Header
        story.append(Paragraph("RISKIFY", self.styles['RiskifyTitle']))
        story.append(Paragraph("Stock Market Prediction Report", self.styles['RiskifySubtitle']))
        story.append(Paragraph(f"Generated: {timestamp}", self.styles['RiskifyNormal']))
        story.append(Spacer(1, 20))
        
        # Prediction Summary
        story.append(Paragraph("PREDICTION SUMMARY", self.styles['SectionHeader']))
        
        prediction_data = [
            ['Predicted Direction:', prediction.get('predicted_direction', 'N/A')],
            ['Confidence Level:', f"{prediction.get('confidence', 0)*100:.1f}%"],
            ['Up Probability:', f"{prediction.get('up_probability', 0)*100:.1f}%"],
            ['Down Probability:', f"{prediction.get('down_probability', 0)*100:.1f}%"],
            ['Expected Return:', f"{prediction.get('expected_return', 0)*100:.2f}%"],
            ['Risk Level:', prediction.get('risk_level', 'Medium')]
        ]
        
        prediction_table = Table(prediction_data, colWidths=[2.5*inch, 3*inch])
        prediction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(prediction_table)
        story.append(Spacer(1, 20))
        
        # Market Data
        story.append(Paragraph("MARKET DATA ANALYSIS", self.styles['SectionHeader']))
        
        market_data = [
            ['Current Price:', f"${stock_data.get('current_price', 0):.2f}"],
            ['Daily Volume:', f"{stock_data.get('volume', 0):,}"],
            ['RSI:', f"{stock_data.get('rsi', 0):.1f}"],
            ['MACD:', f"{stock_data.get('macd', 0):.2f}"],
            ['20-Day MA:', f"${stock_data.get('moving_avg_20', 0):.2f}"],
            ['50-Day MA:', f"${stock_data.get('moving_avg_50', 0):.2f}"],
            ['Volatility:', f"{stock_data.get('volatility', 0)*100:.1f}%"],
            ['1-Day Change:', f"{stock_data.get('price_change_1d', 0):.1f}%"],
            ['7-Day Change:', f"{stock_data.get('price_change_7d', 0):.1f}%"]
        ]
        
        market_table = Table(market_data, colWidths=[2.5*inch, 3*inch])
        market_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(market_table)
        story.append(Spacer(1, 20))
        
        # Market Signals
        if prediction.get('market_signals'):
            story.append(Paragraph("MARKET SIGNALS", self.styles['SectionHeader']))
            for signal in prediction.get('market_signals', []):
                story.append(Paragraph(f"• {signal}", self.styles['RiskifyNormal']))
            story.append(Spacer(1, 15))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Report generated by Riskify AI Risk Management Platform", self.styles['RiskifyNormal']))
        story.append(Paragraph("Developer: Takunda Mcdonald Gatakata (Data Science and Systems)", self.styles['RiskifyNormal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_loan_report(self, prediction: Dict[str, Any], loan_data: Dict[str, Any], timestamp: str) -> bytes:
        """Generate loan assessment PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch)
        
        story = []
        
        # Header
        story.append(Paragraph("RISKIFY", self.styles['RiskifyTitle']))
        story.append(Paragraph("Loan Default Risk Assessment", self.styles['RiskifySubtitle']))
        story.append(Paragraph(f"Generated: {timestamp}", self.styles['RiskifyNormal']))
        story.append(Spacer(1, 20))
        
        # Risk Assessment Summary
        story.append(Paragraph("RISK ASSESSMENT SUMMARY", self.styles['SectionHeader']))
        
        risk_summary = [
            ['Default Probability:', f"{prediction.get('default_probability', 0)*100:.2f}%"],
            ['Safe Probability:', f"{prediction.get('safe_probability', 0)*100:.2f}%"],
            ['Risk Level:', prediction.get('risk_level', 'Medium')],
            ['Loan Score:', f"{prediction.get('loan_score', 0)}/850"],
            ['Recommendation:', prediction.get('recommendation', 'Review required')],
            ['Suggested Interest Rate:', f"{prediction.get('suggested_interest_rate', 0):.2f}%"]
        ]
        
        risk_table = Table(risk_summary, colWidths=[2.5*inch, 3*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 20))
        
        # Loan Application Details
        story.append(Paragraph("LOAN APPLICATION DETAILS", self.styles['SectionHeader']))
        
        loan_details = [
            ['Loan Amount:', f"${loan_data.get('loan_amount', 0):,.2f}"],
            ['Annual Income:', f"${loan_data.get('annual_income', 0):,.2f}"],
            ['Credit Score:', str(loan_data.get('credit_score', 0))],
            ['Debt-to-Income Ratio:', f"{loan_data.get('debt_to_income', 0)*100:.1f}%"],
            ['Loan Term:', f"{loan_data.get('loan_term', 0)} months"],
            ['Employment Years:', f"{loan_data.get('employment_years', 0):.1f} years"],
            ['Home Ownership:', loan_data.get('home_ownership', 'Unknown').title()],
            ['Loan Purpose:', loan_data.get('loan_purpose', 'Unknown').replace('_', ' ').title()]
        ]
        
        details_table = Table(loan_details, colWidths=[2.5*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Risk Factors
        if prediction.get('risk_factors'):
            story.append(Paragraph("IDENTIFIED RISK FACTORS", self.styles['SectionHeader']))
            for factor in prediction.get('risk_factors', []):
                if 'CRITICAL' in factor:
                    story.append(Paragraph(f"• {factor}", self.styles['RiskWarning']))
                else:
                    story.append(Paragraph(f"• {factor}", self.styles['RiskifyNormal']))
            story.append(Spacer(1, 15))
        
        # Financial Analysis
        loan_amount = float(loan_data.get('loan_amount', 0))
        annual_income = float(loan_data.get('annual_income', 0))
        if annual_income > 0:
            loan_to_income = loan_amount / annual_income
            story.append(Paragraph("FINANCIAL ANALYSIS", self.styles['SectionHeader']))
            story.append(Paragraph(f"Loan-to-Income Ratio: {loan_to_income:.1%}", self.styles['RiskifyNormal']))
            
            if loan_to_income > 1.0:
                story.append(Paragraph("⚠️ WARNING: Loan amount exceeds annual income - Extremely high risk", self.styles['RiskWarning']))
            elif loan_to_income > 0.5:
                story.append(Paragraph("⚠️ CAUTION: High loan-to-income ratio detected", self.styles['RiskWarning']))
            
            story.append(Spacer(1, 15))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Report generated by Riskify AI Risk Management Platform", self.styles['RiskifyNormal']))
        story.append(Paragraph("Developer: Takunda Mcdonald Gatakata (Data Science and Systems)", self.styles['RiskifyNormal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()