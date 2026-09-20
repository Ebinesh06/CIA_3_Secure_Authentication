# TEAM PRESENTATION GUIDE

## AI-Based Risk-Adaptive Secure Authentication System

This is the teammate-friendly guide for understanding the completed project before tomorrow’s presentation and viva.

---

## SECTION 1 — PROJECT AT A GLANCE

### 1. Project name
AI-Based Risk-Adaptive Secure Authentication System

### 2. One-line explanation
This project adds AI-based risk analysis to normal login systems so that suspicious login behaviour can trigger stronger checks like MFA instead of blindly allowing access.

### 3. Problem we are solving
Traditional username/password login only checks whether the password is correct. It does not look at whether the login looks normal for that user. A user may type the correct password but still be logging in from a strange location, unusual device, unusual time, or after many failed attempts. In those cases, password-only authentication is weak.

### 4. Why normal username/password authentication is not enough
A password proves only that a person typed the right string. It does not confirm whether the access request is consistent with the user’s normal behaviour. The same password can be used from a new computer, new IP, or unusual hour, and the system may still accept it without asking for extra verification.

### 5. What makes our project AI-based
The project collects login behaviour and sends the behaviour data to an Isolation Forest model. This model learns what “normal login behaviour” looks like and flags unusual patterns as anomalies. The anomaly result is converted into a risk score and then into a security decision.

### 6. What happens after a user attempts login
After submitting a username and password, the app validates the credentials, collects metadata such as IP, device, hour, failed-attempt count, and other behavioural signals, and then evaluates those features with the AI model.

### 7. What is the final security decision
The system converts the AI result into a risk score and then chooses one of three outcomes:

- LOW: allow login
- MEDIUM: require MFA
- HIGH: block login and log the event

### Simple flow
User Login
↓
Collect Login Behaviour
↓
Extract Features
↓
AI Anomaly Detection
↓
Calculate Risk Score
↓
LOW / MEDIUM / HIGH
↓
Security Action

### Step-by-step explanation
- User Login: The user enters username/email and password.
- Collect Login Behaviour: The app records how the login request looks in context, including time, IP, device, recent attempts, and failed count.
- Extract Features: These values are converted into a feature vector used by the model.
- AI Anomaly Detection: Isolation Forest checks whether the pattern looks normal or unusual.
- Calculate Risk Score: The model output and behavioural features are mapped to a score from 0 to 100.
- LOW / MEDIUM / HIGH: The score is classified into one of the three risk levels.
- Security Action: The system either allows access, asks for MFA, or blocks the login.

---

## SECTION 2 — THE PROBLEM STATEMENT

What security problem does this project solve?

This project addresses the weakness of password-only authentication when login behaviour is suspicious. In real life, login attempts may happen from:

- a new device or browser
- a new IP address
- an unusual time of day
- a large number of failed attempts
- unusually frequent or very infrequent login activity

For example:

- Correct password but new IP address: this may be a suspicious sign.
- Correct password but login at 3:00 AM from a new device: unusual and may require stronger verification.
- Repeated failed login attempts before success: the system should not trust the login immediately.

Password-only systems often ignore these behavioural indicators. The system can still accept a valid password that is being used in a high-risk context. This project tries to reduce that blind trust by adding risk-aware behaviour analysis.

This is not a claim that AI alone proves identity. The project is a demonstration of adaptive authentication, not a full production security system.

---

## SECTION 3 — OUR SOLUTION

The project combines traditional authentication with behavioural risk analysis.

### User authentication
Users register with a username, email, and password. Passwords are hashed before storing them in the database using bcrypt via passlib.

### Behaviour collection
When a user logs in, the app gathers login metadata such as:

- current login hour
- failed attempts count
- recent login attempts in the last 24 hours
- whether the IP is new
- whether the device/browser is new
- time since previous login
- login frequency

### Feature extraction
These values are converted into a feature vector used by the model. The actual features are defined in the AI risk engine.

### Isolation Forest
The app uses scikit-learn’s Isolation Forest to learn what normal login patterns look like. It does not need labels like “suspicious” or “not suspicious” in the same way as a supervised model. It tries to isolate anomalies from the normal distribution.

### Risk score
The model result, plus extra scoring rules based on risky signals, produce a score from 0 to 100.

### Risk levels
The actual thresholds used in the project are:

- LOW: 0–39
- MEDIUM: 40–69
- HIGH: 70–100

These thresholds are implemented in the project code.

### Security action
The risk result triggers one of these three actions:

- LOW: user is allowed to log in
- MEDIUM: user must complete MFA verification before access
- HIGH: login is blocked and a security event is logged

### Final outcomes
LOW:
Risk score 0–39
→ Allow login

MEDIUM:
Risk score 40–69
→ Require MFA

HIGH:
Risk score 70–100
→ Block login and record security event

---

## SECTION 4 — WHAT EXACTLY IS THE AI?

### 1. What is Isolation Forest?
Isolation Forest is an anomaly-detection algorithm. Instead of trying to classify a login as “safe” or “unsafe” in a normal supervised way, it learns a pattern of normal behaviour and tries to isolate points that are far away from that pattern.

### 2. Why did we use it?
The project needs to detect unusual login behaviour, not just known attack signatures. Isolation Forest is well-suited for anomaly detection where suspicious logins are rare and not easy to label in a simple dataset.

### 3. Is it supervised or unsupervised?
This project uses Isolation Forest as an unsupervised anomaly detector. It learns the structure of normal login data and identifies outliers without requiring explicit labels like “malicious” in the training data.

### 4. What does it learn?
It learns the typical distribution of safe login behaviour from synthetic normal data. That data includes values such as typical login hour, low failed-attempt counts, normal recent attempt counts, and non-suspicious timing patterns.

### 5. What is an anomaly?
An anomaly is a login pattern that is unusually different from the normal behaviour observed during training. Examples include new IP, new device, unusual time, repeated failed attempts, and abnormal frequency.

### 6. How does it decide whether a login looks unusual?
The app creates a feature vector from the current login context and passes it into the trained model. The model outputs a decision score. If the pattern is far from the learned normal region, it is treated as an anomaly.

### 7. How is the AI output converted into a risk score?
The project takes the model’s decision score and adjusts it using additional behavioural signals. It adds points for things like new IP, new device, repeated failed attempts, off-hours login, too many recent attempts, long time gap since last login, and high login frequency.

### 8. How does the AI result affect the actual login?
The result is not used to “fully authenticate” the user by itself. Instead, it decides the risk level:

- LOW → allow
- MEDIUM → require MFA
- HIGH → block

### Simple analogy
Imagine the AI learns what a normal user’s login usually looks like. If a login appears very different from that pattern, like logging in at 3 a.m. from a new device and a new IP, the model treats it as suspicious. The app then raises the risk and asks for MFA or blocks the session.

---

## SECTION 5 — AI FEATURES

The actual features used by the AI are defined in the project’s risk engine and the login feature builder.

| Feature | Meaning | Why It Matters |
|---|---|---|
| login_hour | The current time of login in hour format | Logins outside normal hours can be more suspicious |
| failed_attempts | Number of failed login attempts for the user | Many failures suggest brute-force or attack attempts |
| recent_attempts | Number of recent attempts in the last 24 hours | A burst of recent attempts can indicate unusual activity |
| new_ip | Whether the IP differs from the user’s last known IP | New IPs may be suspicious if they differ from the normal pattern |
| new_device | Whether the device/browser differs from previous login data | New device/browser can indicate risk or account takeover |
| time_since_previous_login | Time gap since last login | Very long or irregular gaps can be abnormal |
| login_frequency | A frequency-based signal based on recent login activity | Unusually high activity can indicate suspicious behaviour |

### Simple examples
- A login at 3:00 AM may get a higher hour-based risk.
- A user with several failed attempts is treated as more risky.
- A login from a different IP than usual is flagged as new_ip.
- A login from a device not previously used is flagged as new_device.

---

## SECTION 6 — LOW / MEDIUM / HIGH EXAMPLES

### NORMAL LOGIN
- Familiar behaviour
- AI detects low anomaly
- LOW risk
- User is allowed access

Example: username demo, password Demo@123, standard login time, normal device, normal IP.

### SUSPICIOUS LOGIN
- Behaviour differs from normal
- AI raises anomaly score
- MEDIUM risk
- MFA required

Example: login simulated with medium demo mode, new IP, new device, unusual timing, moderate failed attempts. The app redirects to the MFA check.

### HIGH-RISK LOGIN
- Strongly anomalous behaviour
- AI and behavioural rules push risk high
- HIGH risk
- Login is blocked and event is recorded

Example: high-risk demo mode with unusual hour, multiple recent attempts, repeated failed attempts, and a suspicious login pattern. The app blocks the request and shows the risk result.

### Important note
The demo modes in the project are intentionally designed to demonstrate the three cases. These are educational demo scenarios, not a claim of real-world threat detection accuracy.

---

## SECTION 7 — SECURITY FEATURES

The project implements real security mechanisms in the repository.

### 1. Password hashing
Passwords are stored as hashed values using bcrypt through passlib. This protects stored credentials even if the database is exposed.

### 2. Password verification
When a user logs in, the submitted password is checked against the stored hash using secure verification. The app does not compare plain text directly.

### 3. MFA / TOTP
For medium-risk logins, the app requires a one-time password generated from a TOTP secret using PyOTP. This adds an extra verification layer beyond the password.

### 4. Rate limiting
Flask-Limiter is configured to limit repeated login attempts. This reduces brute-force behaviour and helps control abnormal traffic patterns.

### 5. Failed login tracking
Each user has a failed_attempts counter. If the user exceeds the configured threshold, the account can be temporarily locked.

### 6. Temporary lockout
The app uses MAX_LOGIN_ATTEMPTS and LOCKOUT_MINUTES from config to lock an account for a short time after repeated failures. This blocks repeated guesses and reduces attack efficiency.

### 7. Input validation
The system validates username, email, and password format before creating or updating accounts. This helps reduce malformed input and basic form abuse.

### 8. Secure headers
Flask-Talisman is used to add security headers such as content-security-policy and frame protection. This improves browser-side security posture.

### 9. Session management
The app stores session information for logged-in users and uses JWT tokens for access. It also clears the session on logout.

### 10. Generic authentication errors
The application does not reveal whether the username exists or whether the password was wrong in a detailed way. It gives a generic login failure message.

### 11. Audit logging
Security events are recorded in the audit log table. These include events such as login success, login blocked, MFA required, and MFA success/failure.

### 12. Environment-based secrets
The app loads environment variables such as SECRET_KEY, JWT_SECRET_KEY, and DATABASE_URL from the environment or defaults. The repository includes .env.example to show the expected variables without exposing any real secrets.

---

## SECTION 8 — TECHNOLOGY STACK

| Technology | Purpose |
|---|---|
| Python | Main backend language and application logic |
| Flask | Web framework for routes, sessions, and UI rendering |
| SQLite | Local database used for persistence |
| SQLAlchemy | ORM for database models and querying |
| scikit-learn | ML library used for anomaly detection |
| Isolation Forest | AI model for detecting abnormal login behaviour |
| PyOTP | TOTP generation and MFA verification |
| bcrypt/passlib | Password hashing and verification |
| Flask-Limiter | Rate limiting for login attempts |
| HTML/CSS/JavaScript | Frontend pages and dashboard interactions |
| NumPy/Pandas | Data handling and feature preparation for the model |

---

## SECTION 9 — PROJECT ARCHITECTURE

### Repository structure
- app.py — application bootstrap and database initialization
- config.py — app settings and environment-based configuration
- ai/ — AI model training and risk evaluation logic
- models/ — database models for users, login attempts, MFA, and audit logs
- routes/ — authentication, dashboard, and security routes
- utils/ — shared utilities for validation, hashing, JWT, and limiting
- templates/ — login, MFA, dashboard, profile, and logs pages
- static/ — CSS and JavaScript assets
- tests/ — formal pytest verification
- .env.example — example environment config
- .gitignore — ignore generated and secret files

### Simple architecture diagram
Browser
   ↓
Flask Routes
   ↓
Authentication Logic
   ↓
Feature Extraction
   ↓
Isolation Forest
   ↓
Risk Engine
   ↓
LOW / MEDIUM / HIGH
   ↓
Allow / MFA / Block
   ↓
Database + Audit Logs
   ↓
Dashboard / Security Views

### What each layer does
- Browser: user interacts with login, dashboard, and MFA pages
- Flask Routes: handle requests and user flow
- Authentication Logic: verifies credentials and MFA
- Feature Extraction: builds behavioural feature vector
- Isolation Forest: identifies unusual patterns
- Risk Engine: produces risk score and classification
- Database + Audit Logs: stores users, attempts, and security events
- Dashboard: displays summary and recent events

---

## SECTION 10 — DATABASE

The project uses SQLite as the database, configured through SQLAlchemy.

### Important models
#### User
Stored in users table. Contains:

- id
- username
- email
- password_hash
- mfa_secret
- created_at
- failed_attempts
- locked_until
- last_login_at
- last_ip
- last_device

This table stores user identity and behavioural state needed for authentication decisions.

#### LoginAttempt
Stored in login_attempts table. Contains:

- id
- user_id
- timestamp
- ip_address
- user_agent
- failed
- risk_score
- risk_level
- outcome
- details

This captures each login evaluation and whether it succeeded, failed, required MFA, or was blocked.

#### AuditLog
Stored in audit_logs table. Contains:

- id
- user_id
- timestamp
- event
- risk_score
- risk_level
- action
- details

This stores security events such as login failure, MFA challenge, block, and MFA success/failure.

#### MFAConfiguration
Stored in mfa_configurations table. Contains:

- id
- user_id
- secret
- enabled
- created_at

This stores the per-user MFA secret and enabled state.

### How login attempts are recorded
Each login attempt is saved as a LoginAttempt record with timestamp, IP, user agent, error flag, risk score, risk level, outcome, and details.

### How security events are recorded
AuditLog records each important event, so the dashboard and security logs pages can show what happened and how the system responded.

---

## SECTION 11 — LOGIN FLOW

The complete login process in the actual repository is:

1. User enters username/email and password.
2. The app finds the user by username or email.
3. It checks whether the account is temporarily locked.
4. It verifies the password securely using the stored hash.
5. If credentials are wrong, it increases failed_attempts and logs a generic failure.
6. If credentials are correct, it captures the login metadata: time, IP, user-agent, recent attempts, and count values.
7. It builds a feature dictionary from these values.
8. The AI engine evaluates the feature vector using Isolation Forest.
9. The app calculates the risk score and risk level.
10. If the level is HIGH, the login is blocked and recorded.
11. If the level is MEDIUM, the app stores pending MFA context and redirects to MFA.
12. If the level is LOW, the user is allowed into the dashboard.
13. Every outcome is stored in login_attempts and audit_logs.

This is the real flow implemented by the project.

---

## SECTION 12 — MFA FLOW

### When MFA is triggered
MFA is triggered when the login is classified as MEDIUM risk.

### What TOTP means
TOTP stands for Time-Based One-Time Password. The app uses PyOTP to generate a 6-digit code based on a secret and current time.

### How the OTP is verified
The system looks up the user’s stored secret, generates the current TOTP value, and verifies it with a valid window of 1. If the code matches, MFA passes.

### What happens after successful MFA
After successful verification:

- the pending MFA session is cleared
- the user is logged in
- the system saves the successful login data
- the audit log records MFA success
- the dashboard is opened

### What happens if MFA fails
If the OTP is incorrect, the app shows an error and writes an MFA failure event to the audit log.

---

## SECTION 13 — DEMO FLOW FOR PRESENTATION

Use the actual demo flow from the project.

### DEMO 1 — Normal Login
What to do:
- Go to the login page.
- Use username: demo
- Use password: Demo@123
- Select “Normal login” from the demo simulation dropdown

What happens:
- The app verifies the password.
- Feature values are normal.
- The AI risk score should stay low.
- The user is redirected to the dashboard.

What to say:
“This is the normal login case. The user behaviour looks consistent with the usual pattern, so the risk is low and no extra challenge is needed.”

### DEMO 2 — Medium Risk
What to do:
- Use demo credentials again.
- Select “Suspicious login (MFA required)”

Expected risk:
- Risk level should be MEDIUM
- The app redirects to the MFA page

What to say:
“The login pattern looks unusual, so the system treats it as medium-risk. Instead of allowing access directly, it requires second-factor verification.”

### DEMO 3 — High Risk
What to do:
- Use demo credentials.
- Select “High-risk login (blocked)”

Expected risk:
- Risk level should be HIGH
- The request is blocked
- The system logs the event

What to say:
“This login is strongly abnormal, so the system blocks it and records a security event instead of allowing access.”

### Important presentation warning
Do not display or announce secret values like:

- .env keys
- JWT secret values
- database URLs with real secrets
- TOTP secret shown on the MFA page during live presentation without caution

Only demonstrate the actual app flow using the safe demo credentials and the app’s GUI. Keep secrets out of the presentation.

---

## SECTION 14 — TESTING RESULTS

The repository includes a formal pytest test suite in tests/test_auth_flows.py.

### Current verified result
Command run:

pytest -q

Result:

6 passed, 4 warnings in 53.44s

### What the six tests verify
1. Login page loads correctly
2. Password hashing and verification logic works
3. Normal login succeeds with low risk
4. Medium-risk flow redirects to MFA and succeeds after OTP verification
5. High-risk login is blocked
6. Audit events are recorded correctly

### What the warnings are
The warnings are SQLAlchemy LegacyAPIWarning messages caused by legacy usage of Query.get() in the project code. These warnings do not fail the tests and do not break the application behaviour. They are warnings only.

### Important point
The application is functionally verified by tests, and the warnings are not a failure condition.

---

## SECTION 15 — TEAM MEMBER CONTRIBUTIONS

Based on the project allocation given for this micro-project:

| Team Member | Contribution | What they should understand |
|---|---|---|
| Aaron V Shibu | AI/ML & Risk Analysis | Isolation Forest, anomaly detection, risk score calculation, features, thresholds |
| Ann Mary Johnson | Authentication & Security | password verification, secure login flow, MFA, lockout, rate limiting |
| Alan | Backend, Database & Security Logging | Flask routes, SQLAlchemy models, audit logs, event processing |
| Ebinesh V | Frontend, Dashboard & Testing | login pages, UI, dashboard, charts, testing and validation |

### Each person — likely viva questions
#### Aaron V Shibu
- What is an anomaly in login behaviour?
  Answer: A behaviour that is different from the normal pattern, like unusual hour, new device, or new IP.
- Why use Isolation Forest?
  Answer: It is suitable for anomaly detection when attack patterns are rare and difficult to label.
- How is risk score derived?
  Answer: From model output and behavioural signals added together.
- What is the difference between model output and risk level?
  Answer: Model output is the anomaly signal; risk level is the security category used to decide the action.

#### Ann Mary Johnson
- Why is MFA required only for medium-risk logins?
  Answer: It adds a step-up check without blocking low-risk logins unnecessarily.
- How are passwords protected?
  Answer: By one-way hashing with bcrypt.
- What happens during repeated failed attempts?
  Answer: The failed count increases and the account may be temporarily locked.
- Why is rate limiting useful?
  Answer: It slows down repeated abuse attempts and reduces brute-force pressure.

#### Alan
- What happens when the system records a login event?
  Answer: It stores a LoginAttempt with outcome, risk, and details.
- Why keep audit logs?
  Answer: For monitoring, security review, and dashboard display.
- What is the role of the database models?
  Answer: They preserve users, login outcomes, MFA setup, and security events.
- Why is SQLite used here?
  Answer: It is simple, local, and suitable for a micro-project demonstration.

#### Ebinesh V
- What is shown on the dashboard?
  Answer: Security stats, risk trends, recent events, and login activity.
- Why is the UI important in this project?
  Answer: It makes the risk decisions visible and helps explain the project clearly.
- What test evidence do you have?
  Answer: Six pytest checks passed.
- How does the demo help with presentation?
  Answer: It shows low-risk success, medium-risk MFA, and high-risk block clearly.

---

## SECTION 16 — FACULTY VIVA / PRESENTATION QUESTIONS

Below are likely questions with short answers.

### A. Basic Project Questions
1. What is your project about?
   Answer: An AI-based risk-aware authentication system that adds MFA or blocks login when behaviour looks suspicious.

2. What is the main problem it solves?
   Answer: Password-only login ignores abnormal behaviour, so dangerous logins may be accepted.

3. Why is this better than normal login?
   Answer: It adds behavioural analysis and adaptive security checks.

4. What is the final goal of the system?
   Answer: Allow safe logins, challenge suspicious ones with MFA, and block high-risk attempts.

### B. AI / ML Questions
5. What is Isolation Forest?
   Answer: An anomaly-detection model that isolates unusual points from normal behaviour.

6. Why did you use Isolation Forest?
   Answer: It fits anomaly-based risk detection better than a simple rule-only model.

7. Is this model supervised?
   Answer: No, it is used as an unsupervised anomaly detector.

8. What does the model learn?
   Answer: The normal pattern of login behaviour from synthetic training data.

9. What is an anomaly in this project?
   Answer: A login that differs strongly from normal behaviour such as new IP, new device, unusual time, or repeated failed attempts.

### C. Cryptography & Security Questions
10. How are passwords stored?
   Answer: As bcrypt hashes.

11. Why not store plain text passwords?
   Answer: Because a database leak would expose all user passwords.

12. What is MFA?
   Answer: Multi-factor authentication, which adds a second factor beyond the password.

13. What is TOTP?
   Answer: Time-based one-time password generated from a secret and current time.

14. Why do we need rate limiting?
   Answer: To reduce brute-force attempts and abusive repeated login traffic.

### D. Authentication Questions
15. What happens in LOW risk?
   Answer: The user is allowed to log in.

16. What happens in MEDIUM risk?
   Answer: MFA is required.

17. What happens in HIGH risk?
   Answer: Login is blocked and logged.

18. Is the AI the only decision-maker?
   Answer: No. It contributes to the risk score, but the final decision is still enforced by the app logic and security rules.

### E. Flask / Backend Questions
19. What backend framework is used?
   Answer: Flask.

20. What does the app do when a login is submitted?
   Answer: Validates input, checks credentials, computes risk, and applies the risk-based decision.

21. What is the role of the routes folder?
   Answer: It contains the login, dashboard, profile, and security-log endpoints.

22. Why use a Flask app for this project?
   Answer: It is simple, fast, and suitable for a college-level micro project.

### F. Database Questions
23. What database is used?
   Answer: SQLite.

24. What tables are important?
   Answer: users, login_attempts, audit_logs, and mfa_configurations.

25. Why are attempts logged?
   Answer: To monitor events, display dashboard statistics, and review security decisions.

### G. Testing Questions
26. How did you test the project?
   Answer: By running pytest on the repository’s formal test suite.

27. How many tests currently pass?
   Answer: Six tests pass.

28. Did the warnings cause any failures?
   Answer: No. The warnings are SQLAlchemy legacy warnings only.

### H. Project Limitation Questions
29. Is this production-ready?
   Answer: It is a solid educational demo project, not a full real-world production system.

30. Is the training data real?
   Answer: No. It uses synthetic data for this demo implementation.

31. What is a possible downside of this model?
   Answer: It can produce false positives or false negatives if the normal pattern is not well calibrated.

32. What would improve the system later?
   Answer: Real-world behavioural data, better model calibration, and stronger production security controls.

---

## SECTION 17 — QUESTIONS FACULTY MAY ASK ABOUT AI

### AI DEFENCE

#### Why AI is needed
AI is useful because password-only authentication is not enough when login context is unusual. AI helps the system notice behavioural anomalies that rules alone may miss.

#### What exactly is predicted/detected
The model detects whether the current login pattern looks abnormal compared with normal login history.

#### Why anomaly detection
Because suspicious logins are rare and not always cleanly labelled. Anomaly detection is a practical way to flag unusual patterns.

#### Why Isolation Forest
It is effective for anomaly detection and is simple to implement in a project like this.

#### Training data
The project uses synthetic normal login data generated in the risk engine. This is not real user behavioural data.

#### Features
The model uses:

- login_hour
- failed_attempts
- recent_attempts
- new_ip
- new_device
- time_since_previous_login
- login_frequency

#### Anomaly score
The model produces a decision score indicating how far the current behaviour is from normal.

#### Risk score
The project translates the model output and behavioural flags into a 0–100 risk score.

#### Thresholds
- LOW: 0–39
- MEDIUM: 40–69
- HIGH: 70–100

#### False positives
A real user may occasionally appear suspicious due to unusual timing or a new device, causing a medium-risk challenge.

#### False negatives
An extremely realistic attack may still pass if it looks close to normal behaviour.

#### Limitations
This is a student project and not a full large-scale security platform.

### Distinction: AI model output vs Risk score vs Risk level vs Security action
- AI model output: anomaly signal from the Isolation Forest
- Risk score: numeric value from 0 to 100 created from the model output and additional checks
- Risk level: LOW / MEDIUM / HIGH classification
- Security action: allow / MFA / block decision

This distinction is important because the model does not directly “grant” or “deny” access. The app logic interprets the result and takes the security action.

---

## SECTION 18 — CRYPTOGRAPHY / SECURITY CONNECTION

This project connects to the Cryptography and Network Security course in several practical ways.

### Implemented in the project
- Secure authentication using password verification
- Password hashing with bcrypt/passlib
- MFA using TOTP (PyOTP)
- Session-based user state and JWT token usage
- Rate limiting to reduce automated attack attempts
- Audit logs and monitoring of login outcomes
- Security headers via Flask-Talisman

### Relevant security concepts, not all implemented directly
- End-to-end encryption: not implemented as a core application feature
- TLS/HTTPS enforcement: the app uses secure headers, but the project is not a full TLS deployment setup
- Public key infrastructure: not implemented here

### Important distinction
The project demonstrates practical security controls used in authentication systems, but it is not a full enterprise cryptographic architecture. It is a focused educational implementation of secure authentication and adaptive risk-based access control.

---

## SECTION 19 — LIMITATIONS

The project has realistic limitations based on actual implementation.

- Synthetic training data is used, not real-world behavioural telemetry
- The anomaly model is lightweight and designed for a micro-project
- False positives are possible when a legitimate user behaves unusually
- False negatives are possible if an attacker behaves like a normal user
- Model calibration can be improved with richer history and tuning
- It is a local demo project, not a production deployment
- Secret management should be stronger in a real deployment environment
- Monitoring would need to scale for large real-world systems

These limitations are honest and consistent with the project’s scope.

---

## SECTION 20 — FUTURE ENHANCEMENTS

These are reasonable future improvements, not implemented features.

- Real user behaviour dataset for model training
- More behavioural features such as geolocation and device fingerprinting
- Better model calibration with larger historical data
- Role-based access control
- SMS or email-based security alerts
- Redis-based centralized rate limiting
- Cloud deployment and monitoring
- SIEM or log aggregation integration
- Continuous authentication using additional signals during the session

---

## SECTION 21 — HOW TO RUN THE PROJECT

Use the following commands in Windows PowerShell.

### 1. Clone the repository
```powershell
git clone https://github.com/Ebinesh06/CIA_3_Secure_Authentication.git
```

### 2. Enter the project folder
```powershell
cd "c:\Users\Ebinesh\OneDrive\Desktop\Nah Nah\crypto_secure_authentication_cia_3"
```

### 3. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Initialize the database
```powershell
python -m flask --app app init-db
```

### 6. Start the app
```powershell
python app.py
```

### 7. Open the browser
Visit:

http://127.0.0.1:5000/login

### 8. Run tests
```powershell
.\.venv\Scripts\python -m pytest -q
```

---

## SECTION 22 — PRESENTATION CHEAT SHEET

### PROJECT:
AI-Based Risk-Adaptive Secure Authentication

### PROBLEM:
Password-only authentication ignores suspicious behaviour such as unusual time, new IP, new device, or repeated failed attempts.

### AI:
Isolation Forest anomaly detection using behavioural login features.

### FEATURES:
- login_hour
- failed_attempts
- recent_attempts
- new_ip
- new_device
- time_since_previous_login
- login_frequency

### RISK:
LOW → Allow
MEDIUM → MFA
HIGH → Block

### SECURITY:
Password hashing + MFA + rate limiting + audit logs + session protection + lockout + secure headers

### DATABASE:
SQLite with SQLAlchemy models for users, login attempts, MFA configuration, and audit logs

### BACKEND:
Flask

### TEST:
6 passed, 4 warnings

### 30-SECOND PROJECT EXPLANATION

“Our project improves normal password authentication by adding AI-based risk analysis. The system watches how a user logs in, checks features like time, device, IP, and failed attempts, and uses an Isolation Forest model to detect suspicious behaviour. If the risk is low, login is allowed; if medium, MFA is required; if high, the login is blocked. This makes authentication more adaptive and more secure than password-only systems.”

---

## SECTION 23 — 2-MINUTE PRESENTATION SCRIPT

“Traditional authentication depends mainly on passwords, but a correct password is not always enough. A login can look normal in terms of credentials but still be suspicious because it is coming from a new device, a new IP, an unusual time, or after repeated failed attempts. Our project adds AI-based behaviour analysis to handle exactly that.

The system collects login behaviour and extracts features such as login hour, failed attempt count, recent attempts, IP change, device change, and time since last login. These features are passed into an Isolation Forest model, which is used for anomaly detection. The model does not decide access by itself; it contributes to a risk score between 0 and 100.

If the risk is low, the user is allowed to log in. If it is medium, the app requires MFA using a TOTP-based OTP. If it is high, the login is blocked and a security event is recorded. This makes the authentication flow adaptive rather than fixed.

The project also uses password hashing, rate limiting, failed-attempt tracking, lockout, and audit logs, so the system has both AI-based risk detection and stronger security controls. We tested the project with pytest and the current result is six passing tests with warnings only, which are not failures. In short, this project demonstrates how machine learning can support secure authentication without replacing the core login process.”

---

## SECTION 24 — IMPORTANT: DON'T LIE / DON'T OVERCLAIM

The team should avoid making these claims unless they are clearly true.

- Do not say the model predicts cyberattacks in a real-world sense.
- Do not say this is production-ready for large-scale real deployments.
- Do not say encryption is implemented if it is not.
- Do not say real user data was used when the model is trained on synthetic data.
- Do not claim AI alone authenticates the user.
- Do not confuse anomaly detection with password verification.
- Do not expose secret keys, environment values, or TOTP secrets in the viva.
- Do not claim that every suspicious login is definitively malicious.
- Do not say the system is fully secure without caveats; this is a focused educational implementation.

---

## SECTION 25 — FINAL PROJECT FACTS

### FACTS WE ALL NEED TO REMEMBER

- Project title: AI-Based Risk-Adaptive Secure Authentication System
- Course: Cryptography and Network Security, CSE535
- Tech stack: Python, Flask, SQLite, SQLAlchemy, scikit-learn, PyOTP, bcrypt/passlib, Flask-Limiter, HTML/CSS/JavaScript, NumPy/Pandas
- AI model: Isolation Forest
- AI features: login_hour, failed_attempts, recent_attempts, new_ip, new_device, time_since_previous_login, login_frequency
- Risk thresholds: LOW 0–39, MEDIUM 40–69, HIGH 70–100
- Security actions: LOW = allow, MEDIUM = MFA, HIGH = block
- Database: SQLite with SQLAlchemy models
- Security controls: hashing, MFA, rate limiting, lockout, audit logging, secure headers, session handling
- Testing result: 6 passed, 4 warnings
- GitHub repository: https://github.com/Ebinesh06/CIA_3_Secure_Authentication.git
- Team members: Aaron V Shibu, Ann Mary Johnson, Alan, Ebinesh V
- Demo credentials: username = demo, password = Demo@123

### Safe presentation note
The app includes a real TOTP secret in the MFA page for local demo purposes. This should not be exposed or announced during presentation. Keep the demo controlled and avoid revealing any secret values.

---

## FINAL NOTE FOR THE TEAM

This project is a practical demonstration of adaptive authentication using AI. It is not a claim of full enterprise security or real-world production protection. It is a strong student project that successfully shows how AI risk analysis can support the authentication decision and improve security beyond a password-only login.

Before the viva, each teammate should review:

- the login flow
- the risk thresholds
- the AI explanation
- the security controls
- the demo scenarios
- the test result

That is enough to explain the project confidently and honestly.
