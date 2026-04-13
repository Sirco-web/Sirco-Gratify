# Testing Strategies

## Unit Testing
Test individual components in isolation.

```python
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)
    
    def test_add_negative_numbers(self):
        result = self.calc.add(-2, -3)
        self.assertEqual(result, -5)
    
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            self.calc.divide(5, 0)

if __name__ == '__main__':
    unittest.main()
```

## Mocking and Patching
Isolate code by replacing dependencies.

```python
from unittest.mock import Mock, patch, MagicMock

class UserService:
    def get_user(self, user_id):
        response = requests.get(f"http://api/users/{user_id}")
        return response.json()

# Mock external API
@patch('requests.get')
def test_get_user(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {'id': 1, 'name': 'John'}
    mock_get.return_value = mock_response
    
    service = UserService()
    user = service.get_user(1)
    
    assert user['name'] == 'John'
    mock_get.assert_called_once_with('http://api/users/1')
```

## Integration Testing
Test multiple components working together.

```python
class TestUserWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config='testing')
        self.client = self.app.test_client()
        setup_test_db()
    
    def test_user_registration_and_login(self):
        # Register user
        response = self.client.post('/register', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        
        # Login
        response = self.client.post('/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
```

## Test Coverage
Measure how much code is tested.

```bash
# Run tests with coverage
coverage run -m pytest
coverage report
coverage html  # Generate HTML report

# Typical targets:
# 80%+ for critical code
# 70%+ for business logic
# 50%+ for utilities
```

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

```python
# RED: Write failing test
def test_user_can_deposit_money():
    user = User(name="John", balance=0)
    user.deposit(100)
    assert user.balance == 100

# GREEN: Write minimum code to pass
class User:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount

# REFACTOR: Improve code
class User:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
    
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
```

## Parametrized Testing
Test multiple inputs without duplication.

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

## Fixtures
Reusable test setup.

```python
@pytest.fixture
def user_fixture():
    user = User(name="John", email="john@example.com")
    user.save()
    yield user
    user.delete()

def test_user_can_login(user_fixture):
    assert user_fixture.authenticate("password")
```

## BDD (Behavior-Driven Development)
Write tests in human-readable format.

```python
# Using pytest-bdd
from pytest_bdd import given, when, then, scenario

@scenario('features/login.feature', 'User can login')
def test_login():
    pass

@given('user has valid credentials')
def user_with_credentials():
    return User(email="test@example.com", password="pass123")

@when('user clicks login')
def user_clicks_login(user_with_credentials, client):
    return client.post('/login', data={
        'email': user_with_credentials.email,
        'password': user_with_credentials.password
    })

@then('user is logged in')
def user_is_logged_in(response):
    assert response.status_code == 200
```

## Performance Testing
Measure code performance under load.

```python
import timeit

# Simple timing
time_taken = timeit.timeit('sum(range(100))', number=100000)
print(f"Time: {time_taken:.2f}s")

# Load testing with locust
from locust import HttpUser, task

class UserBehavior(HttpUser):
    @task
    def index(self):
        self.client.get("/")
    
    @task
    def get_user(self):
        self.client.get("/api/users/1")
```

## Mutation Testing
Verify tests actually catch bugs.

```bash
# Using mutmut to inject bugs into code
mutmut run
mutmut results

# Tests should catch introduced bugs
```

## Test Organization

### Naming Convention
```
test_[module]_[function]_[scenario]

test_user_service_create_user_with_valid_email
test_user_service_create_user_with_invalid_email
test_user_service_create_user_with_existing_email
```

### Directory Structure
```
project/
├── src/
│   └── app.py
├── tests/
│   ├── unit/
│   │   └── test_user_service.py
│   ├── integration/
│   │   └── test_api_endpoints.py
│   └── fixtures/
│       └── conftest.py
```

## Continuous Integration
Automatically run tests on each commit.

```yaml
# GitHub Actions example
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Upload coverage
        run: pytest --cov --cov-report=xml
```
