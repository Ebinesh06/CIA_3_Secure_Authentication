# PROJECT TITLE
AI-Based Risk-Adaptive Secure Authentication System

# PROBLEM STATEMENT
Traditional authentication systems rely primarily on usernames and passwords. This makes them vulnerable to user anomalies such as unusual login time, new devices, repeated failed attempts, and suspicious IP addresses. A secure system should adapt to risk and apply stronger checks like MFA or blocking when necessary.

# OBJECTIVES
- Implement a secure authentication system.
- Use AI to analyze login behavior.
- Require MFA for medium-risk logins.
- Block high-risk logins.
- Record and display security events.

# TECHNOLOGIES / TOOLS USED
Python, Flask, SQLite, SQLAlchemy, bcrypt, JWT, PyOTP, Flask-Limiter, scikit-learn, pandas, NumPy, HTML, CSS, and JavaScript.

# SYSTEM / MODULE DESIGN
The applicaion uses a login module, AI risk engine, MFA verification, and audit dashboard. Risk is determined by analyzing behavioral features and passing them to an Isolation Forest model.

# CONCLUSION
The project successfully demonstrates adaptive authentication by combining traditional security with AI-based risk analysis. The result is a small but practical application security system suitable for a college micro-project.

# INDIVIDUAL CONTRIBUTION
Designed and implemented the system architecture, AI risk engine, security controls, MFA, and dashboard.

# REFERENCES
1. scikit-learn documentation
2. Flask official documentation
3. PyOTP documentation
4. OWASP authentication guidance
