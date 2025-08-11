# Security Authentication and Authorization Scheme Design

## 1. User Authentication Mechanism

### 1.1 JWT Token Mechanism

#### Implementation Plan:
- Use JWT (JSON Web Tokens) for user identity authentication
- Adopt asymmetric encryption algorithm (RS256) to ensure Token security
- Access Token validity period: 1 hour
- Refresh Token validity period: 7 days
- Token contains basic user information (user_id, username, roles, etc.)

#### Token Structure:
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 123456,
    "username": "example_user",
    "roles": ["user"],
    "exp": 1677652288,
    "iat": 1677648688,
    "iss": "bailian-api-platform"
  }
}
```

#### Authentication Process:
1. User submits login credentials
2. Backend verifies user identity
3. Generate JWT Access Token and Refresh Token
4. Return Tokens to client
5. Client carries Access Token in subsequent requests
6. Backend verifies Token validity
7. Use Refresh Token to refresh when Token expires

### 1.2 OAuth2 Integration (Optional Extension)

#### Implementation Plan:
- Integrate third-party login (WeChat, GitHub, Google, etc.)
- Use OAuth2.0 protocol standard
- Provide standard authorization code flow
- Support PKCE to enhance security

## 2. API Interface Authorization Mechanism

### 2.1 RBAC Permission Model

#### Role Design:
- **Regular User (user)**: Can create conversations, send messages, view history
- **Premium User (premium_user)**: In addition to regular user permissions, can use more advanced models
- **Administrator (admin)**: System management permissions, can view all user data

#### Permission Control:
- Role-Based Access Control (RBAC)
- Fine-grained API permission verification
- Define required permission levels for each API endpoint

#### Permission Verification Process:
1. Parse JWT Token to obtain user role information
2. Check required permissions for API endpoint
3. Verify if user roles meet permission requirements
4. Execute business logic if authorized, otherwise return 403 error

### 2.2 Data-Level Permission Control

#### Implementation Plan:
- Users can only access their own data (associated with user ID)
- Conversations and messages are isolated through user_id
- Administrators can access all user data (determined by role)

## 3. Data Transmission Security

### 3.1 HTTPS Encrypted Transmission

#### Implementation Plan:
- Enforce HTTPS protocol
- TLS 1.2 or higher version
- Use secure encryption suites
- HSTS (HTTP Strict Transport Security) header

### 3.2 Sensitive Data Encryption Storage

#### Implementation Plan:
- User passwords are stored using bcrypt hash (already reflected in database design)
- API keys are encrypted during transmission
- Sensitive configuration information is encrypted storage

### 3.3 Database Connection Security

#### Implementation Plan:
- Use SSL/TLS to encrypt database connections
- Configure database users with principle of least privilege
- Rotate database credentials regularly

## 4. Password Security Policy

### 4.1 Password Complexity Requirements

#### Implementation Plan:
- Minimum length: 8 characters
- Must contain uppercase and lowercase letters, numbers, and special characters
- Disallow common weak passwords
- Disallow same as username or email

### 4.2 Password Storage Security

#### Implementation Plan:
- Use bcrypt algorithm for hashing
- Salt value is automatically generated and stored
- Hash iteration count: 12 rounds

### 4.3 Password Reset Mechanism

#### Implementation Plan:
- Send password reset link via email
- Reset link validity period: 1 hour
- Original password is immediately invalidated after reset

## 5. API Call Rate Limiting

### 5.1 Rate Limiting Strategy

#### Implementation Plan:
- Rate limiting based on user API calls
- Regular users: 10 calls per minute
- Premium users: 100 calls per minute
- Administrators: No limit or higher limit

### 5.2 Rate Limiting Algorithm

#### Implementation Plan:
- Use token bucket algorithm
- Redis stores rate limiting counters
- Unified rate limiting in distributed environments

### 5.3 Rate Limiting Response

#### Implementation Plan:
- Return 429 status code when limit is exceeded
- Include rate limiting information in response headers:
  - X-RateLimit-Limit: 100
  - X-RateLimit-Remaining: 99
  - X-RateLimit-Reset: 1677652288

## 6. Alibaba Cloud Bailian API Key Security Management

### 6.1 Key Storage Security

#### Implementation Plan:
- API keys are not stored in the database
- Use environment variables or secret management services (such as HashiCorp Vault)
- Rotate API keys regularly
- Rotate multiple keys to reduce single point of failure

### 6.2 Key Access Control

#### Implementation Plan:
- Access keys only in services that need to call Alibaba Cloud APIs
- Use service account principle of least privilege
- Log key access

### 6.3 Key Leak Protection

#### Implementation Plan:
- Monitor abnormal key usage
- Automatically disable suspicious keys
- Establish key leak emergency response process

## 7. Logging and Audit Mechanism

### 7.1 Log Content

#### Implementation Plan:
- User login/logout logs
- API call logs (already included in api_calls table)
- Permission change logs
- Security event logs
- System error logs

### 7.2 Log Security

#### Implementation Plan:
- Desensitize sensitive information
- Encrypt log files for storage
- Control log access permissions
- Regular backup and archiving

### 7.3 Audit Trail

#### Implementation Plan:
- Record user operation trails
- Associate user ID, operation time, operation type, and affected data
- Provide audit log query interface
- Generate security audit reports regularly

## 8. Technical Implementation Details

### 8.1 JWT Implementation Code Example

```python
import jwt
import datetime
from cryptography.hazmat.primitives import serialization

# JWT Configuration
JWT_ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Generate Access Token
def create_access_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    private_key = open("jwt-private.pem", "rb").read()
    private_key = serialization.load_pem_private_key(private_key, password=None)
    encoded_jwt = jwt.encode(data, private_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# Generate Refresh Token
def create_refresh_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    private_key = open("jwt-private.pem", "rb").read()
    private_key = serialization.load_pem_private_key(private_key, password=None)
    encoded_jwt = jwt.encode(data, private_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

### 8.2 Permission Verification Middleware Example

```python
from functools import wraps
from flask import request, jsonify

def require_auth(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"code": 401, "message": "Authentication token not provided"}), 401
            
            try:
                # Verify Token
                payload = verify_jwt_token(token)
                user_roles = payload.get('roles', [])
                
                # Check role permissions
                if roles and not any(role in user_roles for role in roles):
                    return jsonify({"code": 403, "message": "Insufficient permissions"}), 403
                
                # Add user information to request context
                request.current_user = payload
                
            except jwt.ExpiredSignatureError:
                return jsonify({"code": 401, "message": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"code": 401, "message": "Invalid token"}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 8.3 Password Processing Example

```python
import bcrypt

# Password encryption
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### 8.4 Rate Limiting Implementation Example

```python
import redis
from functools import wraps
from flask import request

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def rate_limit(max_requests=100, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user identifier
            user_id = request.current_user.get('user_id') if hasattr(request, 'current_user') else 'anonymous'
            key = f"rate_limit:{user_id}:{request.endpoint}"
            
            # Use Redis counter
            current = redis_client.get(key)
            if current is None:
                redis_client.setex(key, window, 1)
            elif int(current) >= max_requests:
                return jsonify({"code": 429, "message": "Rate limit exceeded"}), 429
            else:
                redis_client.incr(key)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## 9. Security Considerations and Best Practices

### 9.1 Security Header Settings

- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

### 9.2 Input Validation and Filtering

- Validate all user input
- Prevent SQL injection attacks
- Prevent XSS attacks
- Prevent CSRF attacks

### 9.3 Security Monitoring and Alerting

- Monitor abnormal login behavior in real-time
- Monitor API call anomaly patterns
- Set up security incident alerting mechanisms
- Regularly perform security scanning and penetration testing

### 9.4 Incident Response Plan

- Establish security incident response process
- Key leak emergency handling
- User data leak emergency handling
- System vulnerability remediation process

## 10. Future Improvement Suggestions

1. Integrate Multi-Factor Authentication (MFA)
2. Implement Single Sign-On (SSO)
3. Add user session management
4. Implement more granular permission control
5. Add security log analysis functionality
6. Implement automated security testing

This security authentication and authorization scheme provides a complete security protection mechanism that can effectively protect system and user data security.