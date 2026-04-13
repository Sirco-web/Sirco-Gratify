# Error Handling & Exceptions

## Exception Handling Best Practices

### Specific Exception Handling
```python
# BAD: Catches everything
try:
    risky_operation()
except Exception:
    print("Error occurred")

# GOOD: Catch specific exceptions
try:
    risky_operation()
except FileNotFoundError:
    print("File not found")
except ValueError:
    print("Invalid value")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise if unknown
```

### Context Managers
Ensure resources are cleaned up properly.

```python
# BAD: Resource might not close if exception occurs
f = open('file.txt')
data = f.read()
f.close()

# GOOD: Automatically closes
with open('file.txt') as f:
    data = f.read()

# Custom context manager
class DatabaseConnection:
    def __enter__(self):
        self.connection = connect_to_db()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        if exc_type:
            logger.error(f"Error: {exc_val}")
        return False  # Don't suppress exception

# Usage
with DatabaseConnection() as db:
    db.query("SELECT * FROM users")
```

### Custom Exceptions
```python
class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class DatabaseError(Exception):
    """Raised when database operation fails"""
    pass

def validate_email(email):
    if '@' not in email:
        raise ValidationError("Invalid email format")
    return True
```

### Exception Chaining
Preserve original exception context.

```python
# BAD: Loses original context
try:
    db.query()
except DatabaseError:
    raise ValueError("Invalid query")

# GOOD: Chains exceptions
try:
    db.query()
except DatabaseError as e:
    raise ValueError("Invalid query") from e
```

## Logging Best Practices

### Structured Logging
```python
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed diagnostic info")
logger.info("General informational message")
logger.warning("Warning: something unexpected")
logger.error("Error occurred but continuing")
logger.critical("Critical error, may fail")

# Use structured logging
logger.info(json.dumps({
    'event': 'user_login',
    'user_id': 123,
    'timestamp': time.time()
}))
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: Confirmation that things work
- **WARNING**: Potential problems
- **ERROR**: Error occurred but continuing
- **CRITICAL**: Error causing failure

### Log Rotation
Prevent log files from growing too large.

```python
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

logger.addHandler(handler)
```

## Circuit Breaker Pattern
Fail fast when service is down.

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

## Retry Logic
Automatically retry failed operations.

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1)
def unreliable_api_call():
    response = requests.get('http://api.example.com/data')
    response.raise_for_status()
    return response.json()
```

## Graceful Degradation
Provide partial functionality when systems fail.

```python
class RecommendationService:
    def get_recommendations(self, user_id):
        try:
            # Try ML model
            return self.ml_model.predict(user_id)
        except Exception:
            logger.warning("ML model failed, using fallback")
            # Fallback to rule-based recommendations
            return self.rules_based_recommendations(user_id)
        except Exception:
            logger.error("All recommendation systems failed")
            # Return empty list instead of crashing
            return []
```

## Error Recovery Strategies

### Idempotency
Operations produce same result when repeated.

```python
# Bad: Non-idempotent
def withdraw_money(account, amount):
    account.balance -= amount
    # If called twice, withdraws twice!

# Good: Idempotent
def withdraw_money(account, transaction_id, amount):
    if transaction_id in account.processed_transactions:
        return account.balance  # Already processed
    
    account.balance -= amount
    account.processed_transactions.add(transaction_id)
    return account.balance
```

### Transaction Rollback
```python
try:
    db.begin_transaction()
    db.insert_user(user)
    db.insert_order(order)
    db.commit()
except Exception as e:
    db.rollback()
    raise
```
