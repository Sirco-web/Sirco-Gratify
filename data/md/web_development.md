# Web Development Best Practices

## Frontend Architecture

### Component-Based Architecture
```javascript
// React example
function UserCard({ user, onDelete }) {
  return (
    <div className="card">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={() => onDelete(user.id)}>Delete</button>
    </div>
  );
}

// Reusable across application
export default UserCard;
```

### State Management
```javascript
// Avoid prop drilling with Context API
import React, { createContext, useContext, useState } from 'react';

const UserContext = createContext();

function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

// Use anywhere in tree
function UserProfile() {
  const { user } = useContext(UserContext);
  return <div>{user.name}</div>;
}
```

## Backend Architecture

### RESTful Principles
```python
# Good REST API design
GET    /api/users           # List all users
POST   /api/users           # Create new user
GET    /api/users/123       # Get specific user
PUT    /api/users/123       # Update user
DELETE /api/users/123       # Delete user

# Resource hierarchy
GET    /api/users/123/posts       # Get user's posts
POST   /api/users/123/posts       # Create post for user
```

### Service Layer Pattern
```python
# Separation of concerns
class UserService:
    """Business logic layer"""
    def create_user(self, email, password):
        if not self._validate_email(email):
            raise ValueError("Invalid email")
        
        user = User(email=email)
        user.set_password(password)
        return user

class UserAPI:
    """API layer"""
    def __init__(self, service):
        self.service = service
    
    def post(self):
        data = request.json
        try:
            user = self.service.create_user(data['email'], data['password'])
            return {'id': user.id}, 201
        except ValueError as e:
            return {'error': str(e)}, 400

class UserRepository:
    """Data layer"""
    def save(self, user):
        db.session.add(user)
        db.session.commit()
```

## Security Headers

### Required Headers
```python
@app.after_request
def set_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # HTTPS enforcement
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response
```

## Form Security

### CSRF Protection
```python
# Flask-WTF handles CSRF automatically
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class LoginForm(FlaskForm):
    username = StringField('Username')
    submit = SubmitField('Login')
    # csrf_token automatically included

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Safe - CSRF token verified
        user = authenticate_user(form.username.data)
```

### Form Validation
```python
from wtforms import StringField, validators

class UserForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(),
        validators.Length(min=5, max=255)
    ])
    
    password = StringField('Password', [
        validators.DataRequired(),
        validators.Length(min=8),
        validators.Regexp(
            '(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])',
            message='Password must have lowercase, uppercase, and digit'
        )
    ])
```

## Performance Optimization

### Frontend Performance
```html
<!-- Lazy load images -->
<img src="small.jpg" data-src="large.jpg" loading="lazy" alt="Image">

<!-- Defer non-critical scripts -->
<script src="analytics.js" defer></script>

<!-- Preload critical assets -->
<link rel="preload" href="critical.css" as="style">

<!-- Compress assets -->
<img src="image.webp" alt="Optimized">

<!-- Use CDN -->
<link rel="stylesheet" href="https://cdn.example.com/style.css">
```

### Backend Performance
```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_permissions(user_id):
    # Expensive query
    return db.query(Permission).filter_by(user_id=user_id).all()

# Use database query optimization
from django.db.models import Prefetch
users = User.objects.prefetch_related('posts', 'comments')

# Pagination to limit data
users = User.query.paginate(page=1, per_page=20)
```

## Error Handling Frontend

```javascript
// Global error handler
window.addEventListener('error', (event) => {
  console.error('Uncaught error:', event.error);
  reportErrorToBackend(event.error);
});

// Promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  reportErrorToBackend(event.reason);
});

// Try-catch with proper handling
async function fetchUserData(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    logger.error('Failed to fetch user:', error);
    showErrorToUser('Unable to load user data');
    throw error;
  }
}
```

## Responsive Design

```html
<!-- Mobile-first approach -->
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<style>
    /* Mobile first */
    .container {
        width: 100%;
        padding: 10px;
    }
    
    /* Tablet */
    @media (min-width: 768px) {
        .container {
            width: 750px;
            padding: 20px;
        }
    }
    
    /* Desktop */
    @media (min-width: 1024px) {
        .container {
            width: 1000px;
            padding: 40px;
        }
    }
</style>
```

## Accessibility (A11y)

```html
<!-- Semantic HTML -->
<header>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
    </nav>
</header>

<main>
    <article>
        <h1>Article Title</h1>
        <p>Content</p>
    </article>
</main>

<!-- Proper ARIA labels -->
<button aria-label="Close menu" onclick="closeMenu()">✕</button>

<!-- Form accessibility -->
<label for="email">Email:</label>
<input id="email" type="email" required>

<!-- Image alt text -->
<img src="chart.png" alt="Sales growth chart showing 25% increase">
```

## SEO Best Practices

```html
<!-- Meta tags -->
<head>
    <title>Unique, descriptive title under 60 chars</title>
    <meta name="description" content="Page description under 160 chars">
    <meta name="canonical" href="https://example.com/page">
    
    <!-- Open Graph -->
    <meta property="og:title" content="Title">
    <meta property="og:description" content="Description">
    <meta property="og:image" content="image.jpg">
    
    <!-- Schema markup -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Title",
        "author": "Author",
        "datePublished": "2024-01-15"
    }
    </script>
</head>

<!-- Semantic HTML -->
<h1>Main heading (one per page)</h1>
<h2>Subheading</h2>

<!-- Links -->
<a href="/products">Products</a> <!-- Good anchor text -->
<a href="/products">click here</a> <!-- Bad anchor text -->
```

## Web Standards Compliance

- Validate HTML: https://validator.w3.org/
- Validate CSS: https://jigsaw.w3.org/css-validator/
- Test accessibility: https://www.accessibilitytest.org/
- Check performance: https://pagespeed.web.dev/
- Mobile friendliness: https://search.google.com/mobile-friendly
- SSL/TLS: https://www.ssllabs.com/ssltest/
