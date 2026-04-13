# APIs and Web Development

## What is an API?

An API (Application Programming Interface) is a way for programs to talk to each other.

### REST APIs

REST APIs use HTTP methods to perform operations.

```
GET    /users          - Get all users
GET    /users/123      - Get user with id 123
POST   /users          - Create new user
PUT    /users/123      - Update user 123
DELETE /users/123      - Delete user 123
```

### HTTP Status Codes

Understanding response codes is crucial for debugging.

```
200 OK              - Request successful
201 Created         - New resource created
400 Bad Request     - Invalid data sent
401 Unauthorized    - Authentication required
403 Forbidden       - No permission
404 Not Found       - Resource doesn't exist
500 Server Error    - Server problem
503 Service Error   - Service unavailable
```

## Building a Simple API

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage (fake database)
users = [
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'}
]

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({'error': 'Name required'}), 400
    
    new_user = {
        'id': max(u['id'] for u in users) + 1,
        'name': data['name']
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    user['name'] = data.get('name', user['name'])
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    initial_count = len(users)
    users = [u for u in users if u['id'] != user_id]
    
    if len(users) == initial_count:
        return jsonify({'error': 'User not found'}), 404
    
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
```

## Common API Patterns

### Authentication

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'secret-key-123':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/protected')
@require_api_key
def protected_resource():
    return jsonify({'data': 'secret'})
```

### Pagination

```python
@app.route('/items')
def list_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    items = get_all_items()  # Imagine this gets data
    total = len(items)
    
    return jsonify({
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    })
```

### Error Handling

```python
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/data')
def get_data():
    try:
        data = fetch_data_from_db()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Calling External APIs

```python
import requests
import json

def get_weather(city):
    url = "https://api.weather.com/current"
    params = {'city': city, 'units': 'metric'}
    headers = {'Authorization': 'Bearer YOUR_API_KEY'}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()  # Raise exception for bad status
        return response.json()
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout'}
    except requests.exceptions.HTTPError as e:
        return {'error': f'HTTP error: {e.response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

# Usage
weather = get_weather('London')
print(json.dumps(weather, indent=2))
```

## API Response Best Practices

```python
# ✅ GOOD - Consistent response format
@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = database.find_user(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found',
            'data': None
        }), 404
    
    return jsonify({
        'success': True,
        'error': None,
        'data': user
    }), 200

# ✅ GOOD - Meaningful error messages
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({
            'error': 'validation_error',
            'message': 'Email is required'
        }), 400
    
    if 'password' not in data:
        return jsonify({
            'error': 'validation_error',
            'message': 'Password is required'
        }), 400
    
    # Validate password...
    if not is_valid_password(data['email'], data['password']):
        return jsonify({
            'error': 'auth_failed',
            'message': 'Invalid email or password'
        }), 401
    
    token = generate_token(data['email'])
    return jsonify({'token': token}), 200
```

## Testing APIs

```python
import unittest
from your_app import app

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_users(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
    
    def test_create_user(self):
        response = self.app.post('/users', 
            json={'name': 'Charlie'}
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'Charlie')
    
    def test_create_user_missing_name(self):
        response = self.app.post('/users', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_get_nonexistent_user(self):
        response = self.app.get('/users/99999')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_user(self):
        # Create user
        create_resp = self.app.post('/users', json={'name': 'Test'})
        user_id = create_resp.get_json()['id']
        
        # Delete user
        delete_resp = self.app.delete(f'/users/{user_id}')
        self.assertEqual(delete_resp.status_code, 204)
        
        # Verify deleted
        get_resp = self.app.get(f'/users/{user_id}')
        self.assertEqual(get_resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
```

## Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/data')
@limiter.limit("5 per minute")
def get_data():
    return jsonify({'data': 'value'})
```

## CORS (Cross-Origin Resource Sharing)

```python
from flask_cors import CORS

CORS(app)  # Allow all origins

# Or specific configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "https://example.com",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/data')
def get_data():
    return jsonify({'data': 'value'})
```

## API Documentation

```python
@app.route('/api/docs')
def get_docs():
    """
    API Documentation
    
    GET /users
        Returns list of all users
        Response: 200 [{"id": 1, "name": "Alice"}, ...]
    
    POST /users
        Create new user
        Request: {"name": "Bob"}
        Response: 201 {"id": 2, "name": "Bob"}
    
    GET /users/<id>
        Get specific user
        Response: 200 {"id": 1, "name": "Alice"}
        Error: 404 {"error": "User not found"}
    
    PUT /users/<id>
        Update user
        Request: {"name": "New Name"}
        Response: 200 {"id": 1, "name": "New Name"}
    
    DELETE /users/<id>
        Delete user
        Response: 204 (No Content)
        Error: 404 {"error": "User not found"}
    """
    return get_docs.__doc__
```

Remember: A good API is well-documented, consistent, and includes clear error messages!
