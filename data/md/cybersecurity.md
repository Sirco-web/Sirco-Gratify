# Cybersecurity Fundamentals

## OWASP Top 10 Vulnerabilities

### 1. SQL Injection
Attack where malicious SQL code is injected into input fields.

**Vulnerable Code (Python):**
```python
# NEVER DO THIS
query = f"SELECT * FROM users WHERE username = '{user_input}'"
db.execute(query)
```

**Attack Example:**
```
username: admin' OR '1'='1
# Results in: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# Returns all users
```

**Secure Code:**
```python
# Use parameterized queries
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (user_input,))
```

### 2. Cross-Site Scripting (XSS)
Injecting malicious scripts into web pages viewed by other users.

**Types:**
- **Stored XSS**: Malicious script stored in database
- **Reflected XSS**: Script in URL parameter
- **DOM-based XSS**: Vulnerability in client-side code

**Prevention:**
```python
# Flask: Use Markup to escape HTML
from markupsafe import escape
safe_output = escape(user_input)
```

```html
<!-- Django: Auto-escapes by default -->
<p>{{ user_input }}</p>

<!-- Or explicitly escape -->
<p>{{ user_input|escapejs }}</p>
```

### 3. Broken Authentication
Weak password policies, session management flaws, credential exposure.

**Best Practices:**
- Use strong password hashing (bcrypt, Argon2, not MD5/SHA1)
- Implement multi-factor authentication (MFA)
- Use secure session tokens with expiration
- Implement account lockout after failed attempts
- Never send passwords in emails

```python
# Secure password hashing with bcrypt
import bcrypt

password = "mypassword".encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
# Store hashed, never store plain password

# Verify
bcrypt.checkpw(password_attempt.encode('utf-8'), hashed)
```

### 4. Sensitive Data Exposure
Unencrypted sensitive data transmitted or stored.

**Prevention:**
- Use HTTPS/TLS for all data transmission
- Encrypt sensitive data at rest (AES-256)
- Remove sensitive data from logs
- Use environment variables for secrets, not hardcoded
- Implement proper access controls

```python
# Secure: Never log passwords
logger.info(f"User login: {username}")  # Good
logger.info(f"User login: {username}, password: {password}")  # NEVER

# Secure: Use environment variables
import os
db_password = os.getenv('DB_PASSWORD')  # Not in code
```

### 5. XML External Entity (XXE) Injection
Exploiting XML processing to access files or cause DoS.

**Vulnerable:**
```python
import xml.etree.ElementTree as ET
tree = ET.parse(untrusted_xml)  # Vulnerable
```

**Secure:**
```python
# Disable external entity processing
from defusedxml import ElementTree as ET
tree = ET.parse(untrusted_xml)
```

### 6. Broken Access Control
Users can access resources they shouldn't.

**Secure Implementation:**
```python
def get_user_data(user_id, requested_user_id):
    # Verify current user can access this data
    current_user = get_current_user()
    if current_user.id != requested_user_id and not current_user.is_admin:
        raise PermissionError("Unauthorized")
    return database.get_user(requested_user_id)
```

### 7. Security Misconfiguration
Default credentials, unnecessary features enabled, outdated software.

**Checklist:**
- Remove default accounts and passwords
- Disable verbose error messages in production
- Keep all software updated
- Minimize installed components
- Configure security headers

```python
# Flask: Set security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 8. Insecure Deserialization
Untrusted data deserialization can lead to code execution.

**Vulnerable (Python):**
```python
import pickle
data = pickle.loads(untrusted_data)  # Can execute arbitrary code
```

**Secure:**
```python
import json
data = json.loads(untrusted_data)  # Safe, limited to data structures
```

### 9. Using Components with Known Vulnerabilities
Outdated libraries with security flaws.

**Prevention:**
```bash
# Check for vulnerabilities
pip-audit
npm audit
bundle audit  # Ruby

# Keep dependencies updated
pip install --upgrade package-name
```

### 10. Insufficient Logging & Monitoring
Can't detect attacks without proper logging.

**Implementation:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log security events
logger.warning(f"Failed login attempt for user: {username}")
logger.critical(f"Unauthorized access attempt: {request.path}")
```

## Authentication Methods

### JWT (JSON Web Tokens)
Self-contained tokens with encoded claims.

```python
import jwt
import datetime

# Create token
token = jwt.encode({
    'user_id': 123,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}, 'secret_key', algorithm='HS256')

# Verify token
decoded = jwt.decode(token, 'secret_key', algorithms=['HS256'])
```

### OAuth 2.0
Delegated authorization framework for third-party services.

```python
# Using flask-oauth
oauth = OAuth()
google = oauth.remote_app('google', ...)
```

### SAML
XML-based for enterprise SSO.

### API Keys
Simple but less secure for high-value operations.

```python
# Secure: Check against hashed key
def verify_api_key(provided_key):
    hashed = hash_api_key(provided_key)
    return database.verify_key(hashed)
```
