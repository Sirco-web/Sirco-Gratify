# Code Review & Best Practices

## Code Review Checklist

### Functionality & Logic
- [ ] Does code do what it's supposed to do?
- [ ] Are all edge cases handled?
- [ ] Error handling present and appropriate?
- [ ] Any potential null pointer exceptions?
- [ ] Logic is understandable?

### Performance
- [ ] Any obvious performance bottlenecks?
- [ ] Unnecessary loops or nested loops?
- [ ] Appropriate data structures used?
- [ ] N+1 query problems?
- [ ] Reasonable caching strategy?

### Security
- [ ] Any SQL injection vulnerabilities?
- [ ] Input validation present?
- [ ] Authentication/authorization checks?
- [ ] Sensitive data not logged?
- [ ] Secure password handling?
- [ ] No hardcoded secrets?

### Code Quality
- [ ] Consistent with project style?
- [ ] Proper naming conventions?
- [ ] Appropriate code comments?
- [ ] DRY principle followed?
- [ ] Functions not too long?
- [ ] Test coverage adequate?

### Testing
- [ ] Tests for new functionality?
- [ ] Tests for edge cases?
- [ ] No commented-out test code?
- [ ] Tests are deterministic?

## Code Review Comment Examples

### Good Comment
```
"This query will cause N+1 problem when iterating over results.
 Consider using eager loading with .prefetch_related('related_items')
 as shown in Django docs section 3.2.1"
```

### Constructive Feedback
```
"I see the intent, but this could be clearer. Consider:
 
 # Current
 if a and not b or c and not d:
     ...
 
 # More readable
 should_process = (a and not b) or (c and not d)
 if should_process:
     ...
```

### Praise Good Code
```
"Nice approach! The use of Factory pattern here makes it
 easy to extend with new types. This is maintainable."
```

## Common Code Smells

### Long Methods
```python
# BAD: 50-line method
def process_order(order):
    # ... 50 lines of code ...

# GOOD: Break into smaller methods
def process_order(order):
    validate_order(order)
    charge_payment(order)
    send_confirmation(order)
```

### Duplicate Code
```python
# BAD: Same code in multiple places
if user.is_admin:
    send_admin_alert(message)

# And somewhere else:
if user.is_admin:
    send_admin_alert(message)

# GOOD: Extract to method
def send_alert_if_admin(user, message):
    if user.is_admin:
        send_admin_alert(message)
```

### Magic Numbers
```python
# BAD: What's 86400?
if age > 86400:  # Assuming seconds
    mark_old()

# GOOD: Use constants
SECONDS_IN_DAY = 86400
if age > SECONDS_IN_DAY:
    mark_old()
```

### Too Many Parameters
```python
# BAD: Too many parameters
def create_user(name, email, phone, address, age, country):
    pass

# GOOD: Use object
class UserData:
    def __init__(self, name, email, phone, address, age, country):
        self.name = name
        self.email = email
        # ...

def create_user(user_data):
    pass
```

## Refactoring Techniques

### Extract Method
```python
# Before
def get_price():
    base = quantity * unit_price
    if quantity > 100:
        base = base * 0.9
    if quantity > 500:
        base = base * 0.85
    return base

# After
def get_price():
    base_price = quantity * unit_price
    return apply_discounts(base_price, quantity)

def apply_discounts(price, quantity):
    if quantity > 500:
        return price * 0.85
    if quantity > 100:
        return price * 0.9
    return price
```

### Extract Variable
```python
# Before
if user.age > 18 and user.address and user.credit_score > 650:
    process_loan_application(user)

# After
is_eligible = user.age > 18 and user.address and user.credit_score > 650
if is_eligible:
    process_loan_application(user)
```

### Replace Conditional with Polymorphism
```python
# Before
class ReportGenerator:
    def generate(self, type):
        if type == 'json':
            return json.dumps(self.data)
        elif type == 'csv':
            return csv.dumps(self.data)
        elif type == 'xml':
            return xml.dumps(self.data)

# After
class ReportGenerator:
    def __init__(self, formatter):
        self.formatter = formatter
    
    def generate(self):
        return self.formatter.format(self.data)

class JSONFormatter:
    def format(self, data):
        return json.dumps(data)
```

### Simplify Conditions
```python
# Before
def is_valid():
    if status == "active":
        if not is_expired():
            return True
    return False

# After
def is_valid():
    return status == "active" and not is_expired()
```

## Pair Programming

### Benefits
- Better code quality
- Knowledge sharing
- Fewer bugs (20-30% fewer)
- Team cohesion
- Better design decisions

### Roles
- **Driver**: Writes code
- **Navigator**: Reviews, suggests improvements, catches issues

### Best Practices
- Switch roles every 15-30 minutes
- Use communication tools (Zoom, VS Code Live Share)
- Take breaks to avoid fatigue
- Clear goals for each session
- Follow up with code review

## Metrics & Measurements

```python
# Code metrics to track
# Lines of Code (LOC) - balance between simplicity and completeness
# Cyclomatic Complexity - number of decision paths
# Test Coverage - percentage of code tested
# Technical Debt - cost of maintaining program
# Code Duplication - percentage of duplicate code

# Tools
# pylint - Python code analysis
# flake8 - Style guide enforcement
# SonarQube - Code quality platform
# CodeCov - Coverage tracking
```

## API Review for Teams

### Checklist
- [ ] Consistent with existing APIs?
- [ ] Backward compatible?
- [ ] Clear error messages?
- [ ] Proper authentication?
- [ ] Rate limiting implemented?
- [ ] Documented?
- [ ] Versioning strategy?

## Documentation

### Docstring Example
```python
def calculate_total_price(items, tax_rate=0.08, discount=0):
    """
    Calculate total price of items with tax and discount.
    
    Args:
        items (List[Item]): List of items to purchase
        tax_rate (float): Tax rate as decimal (default 0.08 = 8%)
        discount (float): Discount percentage as decimal (default 0)
    
    Returns:
        float: Total price after tax and discount
    
    Raises:
        ValueError: If tax_rate or discount are negative
        TypeError: If items is not a list
    
    Examples:
        >>> items = [Item(10), Item(20)]
        >>> calculate_total_price(items)
        32.4
        >>> calculate_total_price(items, tax_rate=0.1, discount=0.05)
        28.5
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    
    if tax_rate < 0 or discount < 0:
        raise ValueError("tax_rate and discount must be non-negative")
    
    subtotal = sum(item.price for item in items)
    total = subtotal * (1 + tax_rate) * (1 - discount)
    return total
```
