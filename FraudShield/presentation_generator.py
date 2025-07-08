"""
Riskify System Presentation PDF Generator
Creates a comprehensive PDF presentation with system overview, input field explanations, and workflow descriptions.
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white, blue, red, green, orange
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

class RiskifyPresentationGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Custom colors
        self.primary_color = Color(26/255, 54/255, 93/255)  # #1a365d
        self.secondary_color = Color(249/255, 115/255, 22/255)  # #f97316
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=self.primary_color,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.secondary_color,
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceBefore=16,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Field description style
        self.styles.add(ParagraphStyle(
            name='FieldDesc',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4,
            fontName='Helvetica'
        ))

    def create_presentation(self, filename="riskify_system_presentation.pdf"):
        """Create the complete PDF presentation"""
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        self.story = []
        
        # Add content sections
        self.add_title_page()
        self.add_executive_summary()
        self.add_system_overview()
        self.add_fraud_detection_section()
        self.add_stock_prediction_section()
        self.add_loan_assessment_section()
        self.add_user_roles_section()
        self.add_technical_architecture()
        self.add_workflow_description()
        self.add_benefits_conclusion()
        
        # Build PDF
        self.doc.build(self.story)
        return filename
    
    def add_title_page(self):
        """Add title page"""
        self.story.append(Spacer(1, 2*inch))
        
        # Main title
        title = Paragraph("RISKIFY", self.styles['CustomTitle'])
        self.story.append(title)
        
        subtitle = Paragraph("AI-Powered Risk Management Platform", self.styles['CustomSubtitle'])
        self.story.append(subtitle)
        
        self.story.append(Spacer(1, 1*inch))
        
        # Description
        desc = Paragraph(
            "Comprehensive Machine Learning Solutions for Financial Risk Assessment",
            self.styles['Heading2']
        )
        self.story.append(desc)
        
        self.story.append(Spacer(1, 1.5*inch))
        
        # Features overview
        features = [
            "• Fraud Detection with XGBoost Algorithm",
            "• Stock Market Prediction using Random Forest",
            "• Loan Default Assessment with Advanced ML",
            "• Role-Based Access Control System",
            "• Real-Time Analytics Dashboard",
            "• Comprehensive Reporting Tools"
        ]
        
        for feature in features:
            self.story.append(Paragraph(feature, self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 1*inch))
        
        # Developer info
        dev_info = Paragraph(
            f"<b>Developed by:</b> Takunda Mcdonald Gatakata<br/>"
            f"<b>Contact:</b> 0775919353 / 0718111419<br/>"
            f"<b>Specialization:</b> Data Science and Systems<br/>"
            f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        )
        self.story.append(dev_info)
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self):
        """Add executive summary"""
        self.story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        
        summary_text = """
        Riskify is a comprehensive AI-powered risk management platform specifically designed for financial institutions. 
        The system integrates three specialized machine learning models to provide intelligent risk assessment across 
        multiple domains: fraud detection, stock market prediction, and loan default assessment.
        
        Built with cutting-edge technology including XGBoost and Random Forest algorithms, Riskify offers real-time 
        analysis, predictive insights, and automated decision support. The platform features a sophisticated role-based 
        access control system, ensuring that users only access relevant tools based on their organizational responsibilities.
        
        Key differentiators include automated risk scoring, comprehensive batch processing capabilities, detailed reporting 
        functions, and an intuitive web-based interface that requires no technical expertise to operate effectively.
        """
        
        self.story.append(Paragraph(summary_text, self.styles['Normal']))
        self.story.append(PageBreak())
    
    def add_system_overview(self):
        """Add system overview section"""
        self.story.append(Paragraph("System Overview", self.styles['CustomTitle']))
        
        # Platform architecture
        self.story.append(Paragraph("Platform Architecture", self.styles['SectionHeading']))
        
        arch_text = """
        Riskify is built on a modern, scalable architecture designed for high-performance financial risk analysis:
        """
        self.story.append(Paragraph(arch_text, self.styles['Normal']))
        
        arch_points = [
            "<b>Frontend:</b> Bootstrap 5-powered responsive web interface with real-time updates",
            "<b>Backend:</b> Python Flask framework with RESTful API design",
            "<b>Database:</b> PostgreSQL for reliable data storage and transaction management",
            "<b>Machine Learning:</b> XGBoost and Random Forest algorithms with optimized feature engineering",
            "<b>Security:</b> Role-based authentication with secure session management",
            "<b>Deployment:</b> Cloud-ready with scalable infrastructure support"
        ]
        
        for point in arch_points:
            self.story.append(Paragraph(f"• {point}", self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Core capabilities
        self.story.append(Paragraph("Core Capabilities", self.styles['SectionHeading']))
        
        capabilities = [
            "<b>Real-Time Processing:</b> Instant risk analysis and prediction results",
            "<b>Batch Operations:</b> CSV upload for bulk transaction analysis",
            "<b>Automated Reporting:</b> PDF generation and data export functionality",
            "<b>Dashboard Analytics:</b> Live statistics and performance metrics",
            "<b>Multi-Model Integration:</b> Seamless switching between different AI models",
            "<b>User Management:</b> Comprehensive profile and access control system"
        ]
        
        for capability in capabilities:
            self.story.append(Paragraph(f"• {capability}", self.styles['BulletPoint']))
        
        self.story.append(PageBreak())
    
    def add_fraud_detection_section(self):
        """Add fraud detection section with input field explanations"""
        self.story.append(Paragraph("Fraud Detection System", self.styles['CustomTitle']))
        
        # Overview
        overview_text = """
        The fraud detection system utilizes an advanced XGBoost machine learning model to analyze transaction patterns 
        and identify potentially fraudulent activities. The system processes multiple risk factors in real-time to 
        provide accurate fraud probability scores and automated risk classifications.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Input fields explanation
        self.story.append(Paragraph("Input Fields Explanation", self.styles['SectionHeading']))
        
        fraud_fields = [
            ("<b>Transaction Amount:</b>", "The monetary value of the transaction. Higher amounts typically carry higher risk and are analyzed more carefully by the fraud detection algorithm."),
            
            ("<b>Merchant Category:</b>", "Classification of the merchant type (e.g., grocery, gas station, online retail, ATM). Different categories have varying fraud risk profiles based on historical data."),
            
            ("<b>Customer Age:</b>", "Age of the account holder in years. Helps identify unusual patterns when combined with spending behavior and transaction history."),
            
            ("<b>Account Age (Days):</b>", "Number of days since the account was opened. Newer accounts often present higher fraud risk due to limited transaction history."),
            
            ("<b>Transaction Hour:</b>", "Hour of the day when transaction occurred (0-23). Unusual timing patterns can indicate fraudulent activity, especially for certain merchant types."),
            
            ("<b>Day of Week:</b>", "Day when transaction occurred (0=Monday, 6=Sunday). Weekend and weekday patterns differ significantly for legitimate vs. fraudulent transactions."),
            
            ("<b>Merchant Risk Score:</b>", "Pre-calculated risk assessment of the merchant (0-10 scale). Based on historical fraud rates, merchant verification status, and business reputation."),
            
            ("<b>Location Risk Score:</b>", "Geographic risk assessment (0-10 scale). Considers factors like regional fraud rates, economic stability, and regulatory environment."),
            
            ("<b>Device Risk Score:</b>", "Assessment of the device used for transaction (0-10 scale). Evaluates device fingerprinting, IP reputation, and usage patterns."),
            
            ("<b>Failed Login Attempts:</b>", "Number of recent failed login attempts on the account. Multiple failures can indicate account compromise or brute force attacks."),
            
            ("<b>Transaction Frequency (24h):</b>", "Number of transactions in the past 24 hours. Rapid transaction sequences can indicate card testing or account takeover."),
            
            ("<b>Average Transaction Amount:</b>", "Historical average transaction amount for this account. Significant deviations from normal spending patterns trigger additional scrutiny.")
        ]
        
        for field_name, description in fraud_fields:
            self.story.append(Paragraph(field_name, self.styles['FieldDesc']))
            self.story.append(Paragraph(description, self.styles['Normal']))
            self.story.append(Spacer(1, 0.1*inch))
        
        # Risk scoring
        self.story.append(Paragraph("Risk Assessment Output", self.styles['SectionHeading']))
        
        risk_output = """
        The system provides comprehensive risk assessment including:
        • Fraud probability percentage (0-100%)
        • Risk level classification (Low, Medium, High, Critical)
        • Detailed risk factor analysis
        • Recommended actions (Approve, Review, Decline)
        • Confidence score for the prediction
        """
        self.story.append(Paragraph(risk_output, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_stock_prediction_section(self):
        """Add stock prediction section with input field explanations"""
        self.story.append(Paragraph("Stock Market Prediction System", self.styles['CustomTitle']))
        
        # Overview
        overview_text = """
        The stock prediction system employs a Random Forest ensemble learning algorithm to analyze technical indicators 
        and market signals. It predicts price direction (UP/DOWN) and calculates expected returns based on comprehensive 
        market analysis and volatility assessments.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Input fields explanation
        self.story.append(Paragraph("Input Fields Explanation", self.styles['SectionHeading']))
        
        stock_fields = [
            ("<b>Stock Symbol:</b>", "The trading symbol/ticker of the stock (e.g., AAPL, TSLA). Used to identify the specific security for analysis and historical data retrieval."),
            
            ("<b>Current Price:</b>", "The most recent trading price of the stock. Serves as the baseline for predicting future price movements and calculating potential returns."),
            
            ("<b>Volume:</b>", "Number of shares traded recently. High volume often indicates strong investor interest and can confirm price movement trends."),
            
            ("<b>Market Cap (Billions):</b>", "Total market value of the company in billions. Larger companies typically show different volatility patterns than smaller companies."),
            
            ("<b>RSI (Relative Strength Index):</b>", "Technical indicator (0-100) measuring price momentum. Values above 70 suggest overbought conditions, below 30 suggest oversold conditions."),
            
            ("<b>MACD (Moving Average Convergence Divergence):</b>", "Trend-following momentum indicator. Positive values suggest upward momentum, negative values suggest downward momentum."),
            
            ("<b>50-Day Moving Average:</b>", "Average closing price over the past 50 trading days. Used to identify medium-term trends and support/resistance levels."),
            
            ("<b>200-Day Moving Average:</b>", "Average closing price over the past 200 trading days. Indicates long-term trend direction and major support/resistance zones."),
            
            ("<b>Volatility (30-day):</b>", "Measure of price fluctuation over 30 days (as percentage). Higher volatility indicates greater price uncertainty and risk."),
            
            ("<b>Beta:</b>", "Measure of stock's correlation with overall market movements. Beta > 1 means more volatile than market, Beta < 1 means less volatile."),
            
            ("<b>P/E Ratio:</b>", "Price-to-Earnings ratio indicating valuation relative to earnings. Helps assess whether stock is overvalued or undervalued."),
            
            ("<b>Sector:</b>", "Industry classification (Technology, Healthcare, Finance, etc.). Different sectors respond differently to market conditions and economic factors.")
        ]
        
        for field_name, description in stock_fields:
            self.story.append(Paragraph(field_name, self.styles['FieldDesc']))
            self.story.append(Paragraph(description, self.styles['Normal']))
            self.story.append(Spacer(1, 0.1*inch))
        
        # Prediction output
        self.story.append(Paragraph("Prediction Output", self.styles['SectionHeading']))
        
        prediction_output = """
        The system provides comprehensive market analysis including:
        • Price direction prediction (UP/DOWN) with confidence percentage
        • Expected return calculation based on volatility and market conditions
        • Risk assessment for the investment opportunity
        • Technical analysis summary with key indicators
        • Market signal interpretation and trading recommendations
        """
        self.story.append(Paragraph(prediction_output, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_loan_assessment_section(self):
        """Add loan assessment section with input field explanations"""
        self.story.append(Paragraph("Loan Default Assessment System", self.styles['CustomTitle']))
        
        # Overview
        overview_text = """
        The loan assessment system uses an advanced XGBoost model to evaluate borrower creditworthiness and predict 
        default probability. It analyzes financial profiles, credit history, and employment data to provide 
        comprehensive loan risk assessments and interest rate recommendations.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Input fields explanation
        self.story.append(Paragraph("Input Fields Explanation", self.styles['SectionHeading']))
        
        loan_fields = [
            ("<b>Loan Amount:</b>", "The principal amount requested by the borrower. Larger loans carry higher absolute risk and require more thorough evaluation."),
            
            ("<b>Annual Income:</b>", "Borrower's total yearly income from all sources. Primary factor in determining ability to repay the loan obligation."),
            
            ("<b>Credit Score:</b>", "FICO or equivalent credit score (300-850). Higher scores indicate better credit history and lower default risk."),
            
            ("<b>Employment Length (Years):</b>", "Number of years at current employment. Longer employment indicates job stability and consistent income flow."),
            
            ("<b>Debt-to-Income Ratio:</b>", "Percentage of monthly income going to debt payments. Higher ratios indicate greater financial stress and default risk."),
            
            ("<b>Loan Purpose:</b>", "Intended use of loan funds (home improvement, debt consolidation, etc.). Different purposes have varying risk profiles."),
            
            ("<b>Home Ownership Status:</b>", "Whether borrower owns, rents, or has mortgage. Property ownership can serve as collateral and indicates financial stability."),
            
            ("<b>Number of Credit Lines:</b>", "Total number of open credit accounts. Too few or too many accounts can indicate higher risk."),
            
            ("<b>Age:</b>", "Borrower's age in years. Age correlates with financial experience and earning potential patterns."),
            
            ("<b>Loan Term (Months):</b>", "Duration of the loan in months. Longer terms reduce monthly payments but increase total interest and default risk."),
            
            ("<b>Interest Rate:</b>", "Proposed annual percentage rate for the loan. Higher rates reflect higher perceived risk but also increase default probability."),
            
            ("<b>Previous Defaults:</b>", "Number of previous loan defaults or bankruptcies. Strong predictor of future default behavior.")
        ]
        
        for field_name, description in loan_fields:
            self.story.append(Paragraph(field_name, self.styles['FieldDesc']))
            self.story.append(Paragraph(description, self.styles['Normal']))
            self.story.append(Spacer(1, 0.1*inch))
        
        # Assessment output
        self.story.append(Paragraph("Assessment Output", self.styles['SectionHeading']))
        
        assessment_output = """
        The system provides comprehensive loan evaluation including:
        • Default probability percentage with risk classification
        • Recommended interest rate based on risk profile
        • Loan approval recommendation (Approve, Review, Decline)
        • Risk score on 300-850 scale (similar to credit scores)
        • Detailed risk factor analysis and explanations
        • Alternative loan terms suggestions for improved approval odds
        """
        self.story.append(Paragraph(assessment_output, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_user_roles_section(self):
        """Add user roles and access control section"""
        self.story.append(Paragraph("User Roles & Access Control", self.styles['CustomTitle']))
        
        # Overview
        overview_text = """
        Riskify implements a sophisticated four-tier role-based access control system, ensuring users only access 
        relevant tools and data based on their organizational responsibilities and security clearance levels.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Role descriptions
        roles = [
            ("<b>Risk Manager</b>", "Complete system access with administrative privileges. Can access all three prediction models, analytics dashboards, user management, and system configuration. Ideal for senior risk officers and department heads."),
            
            ("<b>Market Risk Analyst</b>", "Specialized access to stock market prediction tools only. Can analyze market trends, generate investment recommendations, and access market-related reports. Perfect for equity analysts and portfolio managers."),
            
            ("<b>Credit Risk Analyst</b>", "Dedicated access to loan default assessment system. Can evaluate borrower profiles, assess credit risk, and generate loan approval recommendations. Designed for credit officers and underwriters."),
            
            ("<b>Operational Risk Analyst</b>", "Focused access to fraud detection systems. Can analyze transaction patterns, identify suspicious activities, and manage fraud alerts. Tailored for fraud investigators and security teams.")
        ]
        
        for role_name, description in roles:
            self.story.append(Paragraph(role_name, self.styles['SectionHeading']))
            self.story.append(Paragraph(description, self.styles['Normal']))
            self.story.append(Spacer(1, 0.2*inch))
        
        # Security features
        self.story.append(Paragraph("Security Features", self.styles['SectionHeading']))
        
        security_features = [
            "• Secure password hashing with industry-standard algorithms",
            "• Session management with automatic timeout protection",
            "• Role-based page access restrictions with automatic redirects",
            "• Audit trails for all user actions and system access",
            "• Profile update functionality with current password verification",
            "• Secure logout process with session invalidation"
        ]
        
        for feature in security_features:
            self.story.append(Paragraph(feature, self.styles['BulletPoint']))
        
        self.story.append(PageBreak())
    
    def add_technical_architecture(self):
        """Add technical architecture section"""
        self.story.append(Paragraph("Technical Architecture", self.styles['CustomTitle']))
        
        # Technology stack
        self.story.append(Paragraph("Technology Stack", self.styles['SectionHeading']))
        
        tech_stack = """
        <b>Backend Technologies:</b>
        • Python Flask web framework for robust server-side logic
        • PostgreSQL database for reliable data persistence
        • XGBoost and Scikit-learn for machine learning models
        • NumPy and Pandas for data processing and analysis
        • Flask-Login for secure user authentication
        • Gunicorn WSGI server for production deployment
        
        <b>Frontend Technologies:</b>
        • Bootstrap 5 for responsive, mobile-first design
        • JavaScript for real-time user interface interactions
        • Font Awesome icons for professional visual elements
        • Custom CSS with modern design principles
        • HTML5 with semantic markup structure
        
        <b>Machine Learning Stack:</b>
        • XGBoost for gradient boosting algorithms
        • Random Forest for ensemble learning
        • Feature engineering pipelines for data preprocessing
        • Model serialization with Pickle for deployment
        • Cross-validation for model performance verification
        """
        
        self.story.append(Paragraph(tech_stack, self.styles['Normal']))
        
        # System requirements
        self.story.append(Paragraph("System Requirements", self.styles['SectionHeading']))
        
        requirements = """
        <b>Server Requirements:</b>
        • Python 3.8+ runtime environment
        • PostgreSQL 12+ database server
        • 4GB+ RAM for optimal performance
        • 10GB+ storage space for data and models
        • SSL certificate for secure HTTPS connections
        
        <b>Client Requirements:</b>
        • Modern web browser (Chrome, Firefox, Safari, Edge)
        • JavaScript enabled for full functionality
        • Internet connection for real-time features
        • No additional software installation required
        """
        
        self.story.append(Paragraph(requirements, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_workflow_description(self):
        """Add system workflow description"""
        self.story.append(Paragraph("System Workflow & Usage", self.styles['CustomTitle']))
        
        # Login process
        self.story.append(Paragraph("1. User Authentication", self.styles['SectionHeading']))
        
        login_process = """
        Users begin by accessing the Riskify login page where they enter their credentials. The system validates 
        the username/email and password combination, then redirects users to their role-appropriate dashboard. 
        New users can register through the signup process, selecting their organizational role during registration.
        """
        self.story.append(Paragraph(login_process, self.styles['Normal']))
        
        # Navigation
        self.story.append(Paragraph("2. Dashboard Navigation", self.styles['SectionHeading']))
        
        navigation_process = """
        Upon successful login, users see a personalized dashboard showing only the modules they can access based 
        on their role. The navigation bar adapts dynamically, presenting relevant options while hiding restricted 
        functionality. Users can access their profile settings, view available tools, and sign out securely.
        """
        self.story.append(Paragraph(navigation_process, self.styles['Normal']))
        
        # Prediction workflow
        self.story.append(Paragraph("3. Prediction Workflow", self.styles['SectionHeading']))
        
        prediction_workflow = """
        <b>Individual Analysis:</b>
        1. Select the appropriate prediction model (Fraud, Stock, or Loan)
        2. Complete the input form with relevant data
        3. Submit for real-time analysis
        4. Review detailed results and recommendations
        5. Export reports or save analysis for future reference
        
        <b>Batch Processing:</b>
        1. Access the batch analysis feature
        2. Upload CSV file with properly formatted data
        3. Map columns to required input fields
        4. Process multiple records simultaneously
        5. Download comprehensive results report
        """
        self.story.append(Paragraph(prediction_workflow, self.styles['Normal']))
        
        # Reporting
        self.story.append(Paragraph("4. Reporting & Analytics", self.styles['SectionHeading']))
        
        reporting_process = """
        The system provides comprehensive reporting capabilities including real-time dashboards with key metrics, 
        downloadable PDF reports with detailed analysis, CSV export functionality for data integration, and 
        historical analysis tools for trend identification. Users can generate custom reports tailored to their 
        specific needs and organizational requirements.
        """
        self.story.append(Paragraph(reporting_process, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_benefits_conclusion(self):
        """Add benefits and conclusion section"""
        self.story.append(Paragraph("Benefits & Conclusion", self.styles['CustomTitle']))
        
        # Key benefits
        self.story.append(Paragraph("Key Benefits", self.styles['SectionHeading']))
        
        benefits = [
            "<b>Improved Risk Management:</b> Advanced AI algorithms provide more accurate risk assessments than traditional methods, reducing financial losses and improving decision-making quality.",
            
            "<b>Operational Efficiency:</b> Automated analysis reduces manual review time, allowing staff to focus on high-value activities while processing more transactions efficiently.",
            
            "<b>Real-Time Decision Making:</b> Instant predictions enable immediate response to fraud attempts, market opportunities, and loan applications, improving customer experience.",
            
            "<b>Scalable Architecture:</b> Cloud-ready design accommodates growing transaction volumes and expanding user bases without performance degradation.",
            
            "<b>Compliance Support:</b> Comprehensive audit trails and detailed reporting help meet regulatory requirements and internal governance standards.",
            
            "<b>Cost Reduction:</b> Reduced false positives in fraud detection, better loan pricing accuracy, and improved investment decisions lead to significant cost savings."
        ]
        
        for benefit in benefits:
            self.story.append(Paragraph(f"• {benefit}", self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.1*inch))
        
        # ROI considerations
        self.story.append(Paragraph("Return on Investment", self.styles['SectionHeading']))
        
        roi_text = """
        Organizations implementing Riskify typically see measurable returns within 3-6 months through reduced fraud 
        losses, improved loan portfolio performance, and better investment decision outcomes. The system's ability to 
        process high volumes automatically while maintaining accuracy translates directly to operational cost savings 
        and improved risk-adjusted returns.
        """
        self.story.append(Paragraph(roi_text, self.styles['Normal']))
        
        # Future enhancements
        self.story.append(Paragraph("Future Enhancements", self.styles['SectionHeading']))
        
        future_text = """
        Planned system enhancements include additional machine learning models for specialized risk scenarios, 
        integration with external data sources for enriched analysis, mobile application development for field 
        access, and advanced visualization tools for complex data relationships. The modular architecture ensures 
        easy integration of new capabilities as they become available.
        """
        self.story.append(Paragraph(future_text, self.styles['Normal']))
        
        # Conclusion
        self.story.append(Paragraph("Conclusion", self.styles['SectionHeading']))
        
        conclusion_text = """
        Riskify represents a comprehensive solution for modern financial risk management challenges. By combining 
        advanced machine learning algorithms with intuitive user interfaces and robust security features, the 
        platform enables organizations to make better risk decisions faster and more accurately than ever before.
        
        The system's role-based architecture ensures appropriate access control while maximizing usability for 
        each user type. With proven technology, comprehensive training materials, and ongoing support, Riskify 
        is positioned to deliver immediate value and long-term competitive advantages for forward-thinking 
        financial institutions.
        """
        self.story.append(Paragraph(conclusion_text, self.styles['Normal']))
        
        self.story.append(Spacer(1, 1*inch))
        
        # Contact information
        contact_info = Paragraph(
            "<b>For more information or system demonstration:</b><br/>"
            "Takunda Mcdonald Gatakata<br/>"
            "Phone: 0775919353 / 0718111419<br/>"
            "Specialization: Data Science and Systems<br/>"
            f"Document Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Normal']
        )
        self.story.append(contact_info)

def main():
    """Generate the Riskify presentation PDF"""
    generator = RiskifyPresentationGenerator()
    filename = generator.create_presentation()
    print(f"Presentation generated: {filename}")
    return filename

if __name__ == "__main__":
    main()