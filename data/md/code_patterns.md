# Python Code Patterns and Best Practices

## Writing Clean Code

Clean code is code that is easy to read, understand, and maintain.

### Naming Conventions

Use clear, descriptive names.

```python
# ❌ BAD - Unclear names
def calc(x, y):
    return x * y + 5

result = calc(10, 20)

# ✅ GOOD - Clear names
def calculate_total_cost(quantity, unit_price):
    tax = 5
    return quantity * unit_price + tax

total = calculate_total_cost(10, 20)
```

### Keep Functions Small

Functions should do one thing well.

```python
# ❌ BAD - Does too many things
def process_user_data(user_json):
    data = json.loads(user_json)
    data['age'] = int(data['age'])
    data['salary'] = float(data['salary'])
    db.insert('users', data)
    send_email(data['email'])
    log_action('user_created', data['id'])
    return data

# ✅ GOOD - Each function does one thing
def parse_user_data(user_json):
    return json.loads(user_json)

def normalize_user_data(data):
    data['age'] = int(data['age'])
    data['salary'] = float(data['salary'])
    return data

def save_user(data):
    db.insert('users', data)

def notify_user_created(data):
    send_email(data['email'])
    log_action('user_created', data['id'])
```

### DRY - Don't Repeat Yourself

Write code once, reuse it.

```python
# ❌ BAD - Repeated code
def get_user_by_id(user_id):
    if not db.connected:
        raise Exception("Database not connected")
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

def get_user_by_name(name):
    if not db.connected:
        raise Exception("Database not connected")
    return db.query("SELECT * FROM users WHERE name = ?", name)

# ✅ GOOD - Code reuse
def _ensure_db_connected():
    if not db.connected:
        raise Exception("Database not connected")

def get_user_by_id(user_id):
    _ensure_db_connected()
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

def get_user_by_name(name):
    _ensure_db_connected()
    return db.query("SELECT * FROM users WHERE name = ?", name)
```

## Common Code Patterns

### Guard Clauses

Return early to avoid deep nesting.

```python
# ❌ BAD - Deeply nested
def process_order(order):
    if order is not None:
        if order['status'] == 'pending':
            if len(order['items']) > 0:
                return calculate_total(order)
    return None

# ✅ GOOD - Early returns
def process_order(order):
    if order is None:
        return None
    if order['status'] != 'pending':
        return None
    if len(order['items']) == 0:
        return None
    return calculate_total(order)
```

### Context Managers

Properly manage resources.

```python
# ❌ BAD - Might not close file
file = open("data.txt")
data = file.read()
file.close()

# ✅ GOOD - Auto closes file
with open("data.txt") as file:
    data = file.read()

# Works even if error occurs
with open("data.txt") as file:
    data = file.read()
    # If error here, file still closes
```

### List Comprehensions

Concise and efficient.

```python
# ❌ VERBOSE
numbers = [1, 2, 3, 4, 5]
squared = []
for n in numbers:
    squared.append(n ** 2)

# ✅ CONCISE
numbers = [1, 2, 3, 4, 5]
squared = [n ** 2 for n in numbers]

# ✅ WITH FILTERING
even_squared = [n ** 2 for n in numbers if n % 2 == 0]
```

### Dictionary Operations

Efficient data retrieval.

```python
# ❌ BAD - KeyError if not exists
config = {'host': 'localhost'}
port = config['port']  # Crash!

# ✅ GOOD - Use get() with default
config = {'host': 'localhost'}
port = config.get('port', 8080)

# ✅ WITH setdefault
settings = {}
timeout = settings.setdefault('timeout', 30)  # Returns 30, sets it
```

## Error Handling Patterns

### Specific Exception Catching

```python
# ❌ BAD - Catches everything
try:
    value = int(user_input)
    result = 10 / value
except:
    print("Error occurred")

# ✅ GOOD - Specific exceptions
try:
    value = int(user_input)
    result = 10 / value
except ValueError:
    print("Invalid number format")
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Finally Block

Always execute cleanup code.

```python
file = None
try:
    file = open("data.txt")
    data = file.read()
except IOError:
    print("Could not open file")
finally:
    if file:
        file.close()  # Always runs
```

## Type Hints

Make code more readable and catch errors.

```python
# ❌ NO TYPE HINTS
def calculate_total(items):
    return sum(item['price'] for item in items)

# ✅ WITH TYPE HINTS
from typing import List, Dict

def calculate_total(items: List[Dict[str, float]]) -> float:
    return sum(item['price'] for item in items)

# If someone passes wrong type, IDE warns immediately
```

## Performance Patterns

### Avoid Unnecessary Loops

```python
# ❌ SLOW - O(n²)
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(i+1, len(numbers)):
            if numbers[i] == numbers[j]:
                duplicates.append(numbers[i])
    return duplicates

# ✅ FAST - O(n)
def find_duplicates(numbers):
    seen = set()
    duplicates = set()
    for num in numbers:
        if num in seen:
            duplicates.add(num)
        seen.add(num)
    return list(duplicates)
```

### Use Built-in Functions

```python
# ❌ SLOWER
def find_max(numbers):
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

# ✅ FASTER
def find_max(numbers):
    return max(numbers)  # Built-in is optimized
```

## Testing Patterns

### Basic Unit Tests

```python
def test_calculate_total():
    items = [
        {'name': 'apple', 'price': 1.5},
        {'name': 'banana', 'price': 0.5}
    ]
    total = calculate_total(items)
    assert total == 2.0, f"Expected 2.0, got {total}"

def test_calculate_total_empty():
    items = []
    total = calculate_total(items)
    assert total == 0, f"Expected 0 for empty list, got {total}"
```

### Edge Cases

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Test normal case
assert divide(10, 2) == 5

# Test edge cases
try:
    divide(10, 0)
    assert False, "Should have raised error"
except ValueError:
    pass  # Expected
```

## Debugging Your Code

### Use Assertions

```python
def process_data(data):
    assert data is not None, "Data cannot be None"
    assert isinstance(data, list), "Data must be a list"
    assert len(data) > 0, "Data cannot be empty"
    # Process the data
    return [item * 2 for item in data]
```

### Add Logging

```python
import logging
logger = logging.getLogger(__name__)

def sensitive_operation(value):
    logger.debug(f"Starting operation with value: {value}")
    try:
        result = 100 / value
        logger.info(f"Operation succeeded: {result}")
        return result
    except ZeroDivisionError:
        logger.error("Division by zero attempted")
        raise
```

## Code Review Checklist

- [ ] Function names are clear and descriptive
- [ ] No repeated code (DRY principle)
- [ ] Error handling is specific (not bare except)
- [ ] Functions have one responsibility
- [ ] Code is tested with multiple cases
- [ ] Type hints are used
- [ ] Comments explain the "why", not the "what"
- [ ] No hardcoded values (use constants)
- [ ] Performance is reasonable for use case
- [ ] Code follows PEP 8 style guide

Remember: Good code is maintainable code. Write for the next person who has to read it!
