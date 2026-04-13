# API Security & Best Practices

## RESTful API Security

### Input Validation
Always validate incoming data.

```python
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'Password is required'}
    )
    age = fields.Int(validate=validate.Range(min=0, max=150))

# Usage
schema = UserSchema()
try:
    result = schema.load({'email': 'user@example.com', 'password': 'secure123', 'age': 25})
except ValidationError as err:
    return {'errors': err.messages}, 400
```

### Rate Limiting
Prevent abuse by limiting requests per user.

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/data')
@limiter.limit("5 per minute")
def get_data():
    return {'data': 'sensitive'}
```

### API Versioning
Support multiple API versions gracefully.

```python
# URL versioning
@app.route('/api/v1/users/<int:user_id>')
def get_user_v1(user_id):
    return {'id': user_id, 'name': 'John'}

@app.route('/api/v2/users/<int:user_id>')
def get_user_v2(user_id):
    return {
        'id': user_id,
        'name': 'John',
        'profile_url': '/api/v2/users/1/profile'
    }

# Header versioning
@app.route('/api/users/<int:user_id>')
def get_user():
    version = request.headers.get('API-Version', 'v1')
    if version == 'v2':
        return get_user_v2()
    return get_user_v1()
```

## CORS (Cross-Origin Resource Sharing)
Control which domains can access your API.

```python
from flask_cors import CORS

# Allow all origins (not recommended for production)
CORS(app)

# Allow specific origins
CORS(app, origins=[
    "https://example.com",
    "https://app.example.com"
])

# Fine-grained control
@app.route('/api/data')
@cross_origin(origins=["https://example.com"], max_age=3600)
def get_data():
    return {'data': 'Accessible from example.com only'}
```

## API Documentation
Use OpenAPI/Swagger to document APIs.

```python
from flask import Flask
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User found
        schema:
          properties:
            id:
              type: integer
            name:
              type: string
      404:
        description: User not found
    """
    return {'id': user_id, 'name': 'John'}
```

## Webhooks
Send real-time notifications to external services.

```python
import hmac
import hashlib

# Server sending webhook
def send_webhook(event_data):
    payload = json.dumps(event_data)
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    requests.post(
        'https://client.example.com/webhook',
        json=event_data,
        headers={'X-Signature': signature}
    )

# Client receiving webhook
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Signature')
    payload = request.get_data()
    
    # Verify signature
    expected_sig = hmac.new(
        SECRET_KEY.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        return {'error': 'Unauthorized'}, 401
    
    handle_event(request.json)
    return {'status': 'received'}
```

## API Error Responses
Consistent error format.

```python
class APIError(Exception):
    def __init__(self, message, status_code=400, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        'error': error.message,
        'code': error.error_code or 'UNKNOWN_ERROR'
    }
    return response, error.status_code

@app.route('/api/data')
def get_data():
    if not authorized:
        raise APIError('Unauthorized', status_code=401, error_code='AUTH_REQUIRED')
    
    if not found:
        raise APIError('Resource not found', status_code=404, error_code='NOT_FOUND')
    
    return {'data': data}
```

## API Monitoring
Track API performance and issues.

```python
import prometheus_client
from prometheus_client import Counter, Histogram

request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration'
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_count.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    request_duration.observe(duration)
    return response
```

## GraphQL Security
Secure GraphQL APIs against common attacks.

```python
from graphene import ObjectType, String, Schema
from graphql import GraphQLError

# Query depth limiting
class DepthLimitValidator:
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
    
    def validate(self, document_ast, rules, type_info, context):
        # Check query depth and reject if too deep
        pass

# Rate limiting per query
@app.route('/graphql', methods=['POST'])
@limiter.limit("10 per minute")
def graphql_endpoint():
    return handle_graphql_query()

# Disable introspection in production
schema = Schema(query=Query, types=[...])

# In production, disable introspection
if not DEBUG:
    schema.introspect = False
```

## Pagination
Prevent memory issues with large result sets.

```python
@app.route('/api/users')
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100
    
    query = User.query
    paginated = query.paginate(page=page, per_page=per_page)
    
    return {
        'data': [u.to_dict() for u in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }
```

## API Deprecation
Remove old APIs without breaking applications.

```python
import warnings
from functools import wraps

def deprecated(replacement=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = f"{func.__name__} is deprecated"
            if replacement:
                message += f", use {replacement} instead"
            
            warnings.warn(message, DeprecationWarning)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/old-endpoint')
@deprecated(replacement='/api/new-endpoint')
def old_endpoint():
    return get_new_endpoint()
```
