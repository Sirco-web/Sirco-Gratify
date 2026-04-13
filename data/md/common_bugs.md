# Common Programming Bugs and Solutions

## Off-by-One Errors

One of the most common bugs in programming.

### Loop Range Problems

```python
# ❌ BUG - Missing last element
numbers = [1, 2, 3, 4, 5]
for i in range(len(numbers) - 1):  # Only goes to 3
    print(numbers[i])

# ✅ FIX - Include all elements
numbers = [1, 2, 3, 4, 5]
for i in range(len(numbers)):  # Goes to 4 (all indices)
    print(numbers[i])

# ✅ BETTER - Just iterate over list directly
for number in numbers:
    print(number)
```

### Array Indexing

```python
# ❌ BUG - IndexError on last iteration
items = ['a', 'b', 'c']
for i in range(len(items)):
    print(items[i + 1])  # Crashes on last iteration

# ✅ FIX - Access only valid indices
items = ['a', 'b', 'c']
for i in range(len(items) - 1):
    print(items[i + 1])
```

## Mutable Default Arguments

A classic Python gotcha.

```python
# ❌ BUG - Same list shared across calls
def add_item(item, my_list=[]):
    my_list.append(item)
    return my_list

result1 = add_item('a')  # ['a']
result2 = add_item('b')  # ['a', 'b'] - 'a' still there!

# ✅ FIX - Use None as default
def add_item(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list

result1 = add_item('a')  # ['a']
result2 = add_item('b')  # ['b'] - fresh list
```

## Variable Scope Issues

Confusing local and global variables.

```python
# ❌ BUG - Variable not updated
count = 0

def increment():
    count = count + 1  # UnboundLocalError
    return count

increment()

# ✅ FIX - Use global keyword
count = 0

def increment():
    global count  # Declare global
    count = count + 1
    return count

increment()  # Works

# ✅ BETTER - Pass as parameter
def increment(count):
    return count + 1

count = 0
count = increment(count)
```

## Infinite Loops

Code that never stops running.

```python
# ❌ BUG - Infinite loop
while True:
    print("Processing...")
    # Forgot to break or change condition

# ✅ FIX - Add proper exit condition
counter = 0
while counter < 5:
    print(f"Processing... {counter}")
    counter += 1  # Make progress toward exit
```

## None Handling

Not checking for None values.

```python
# ❌ BUG - AttributeError if None
user = None
print(user.name)  # Crash!

# ✅ FIX - Check before using
user = None
if user:
    print(user.name)
else:
    print("No user found")

# ✅ FIX - Use safe access
user = None
name = user.name if user else "Unknown"
```

## List Mutation While Iterating

Changing a list while looping through it.

```python
# ❌ BUG - Unexpected behavior
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # Dangerous!

# ✅ FIX - Iterate over copy
items = [1, 2, 3, 4, 5]
for item in items[:]:  # Iterate over copy
    if item % 2 == 0:
        items.remove(item)

# ✅ BETTER - Use list comprehension
items = [1, 2, 3, 4, 5]
items = [item for item in items if item % 2 != 0]
```

## String Comparison

Case sensitivity and whitespace issues.

```python
# ❌ BUG - Case matters
user_input = "YES"
if user_input == "yes":  # False!
    print("User agreed")

# ✅ FIX - Normalize input
user_input = "YES"
if user_input.lower() == "yes":
    print("User agreed")

# ❌ BUG - Whitespace ignored
password = " mypassword "
if password == "mypassword":  # False!
    print("Access granted")

# ✅ FIX - Strip whitespace
password = " mypassword ".strip()
if password == "mypassword":
    print("Access granted")
```

## Type Coercion Bugs

Unexpected type conversions.

```python
# ❌ BUG - String concatenation
items_count = 5
total = "You have " + items_count + " items"  # TypeError

# ✅ FIX - Convert to string
items_count = 5
total = "You have " + str(items_count) + " items"

# ✅ BETTER - Use f-strings
items_count = 5
total = f"You have {items_count} items"

# ❌ BUG - Boolean as integer
is_valid = True
total = 100 + is_valid  # Result is 101!

# ✅ FIX - Check type
is_valid = True
if is_valid:
    total = 101
```

## Dictionary Key Errors

Accessing non-existent keys.

```python
# ❌ BUG - KeyError
data = {'name': 'Alice', 'age': 30}
city = data['city']  # KeyError!

# ✅ FIX - Use get()
data = {'name': 'Alice', 'age': 30}
city = data.get('city', 'Unknown')  # Returns 'Unknown'

# ✅ FIX - Check if exists
data = {'name': 'Alice', 'age': 30}
if 'city' in data:
    city = data['city']
```

## Function Return Value Issues

Not returning values or returning None.

```python
# ❌ BUG - Function doesn't return
def calculate_total(prices):
    total = sum(prices)  # Forgot return!

result = calculate_total([10, 20, 30])
print(result)  # None

# ✅ FIX - Add return
def calculate_total(prices):
    total = sum(prices)
    return total

result = calculate_total([10, 20, 30])
print(result)  # 60
```

## Import Errors

Module not found or circular imports.

```python
# ❌ BUG - Module doesn't exist
from unknown_module import function

# ✅ FIX - Import from existing module
from os import path
from datetime import datetime

# ❌ BUG - Circular import
# file_a.py
from file_b import function_b

# file_b.py
from file_a import function_a

# ✅ FIX - Reorganize dependencies
# file_a.py
from file_b import function_b

# file_b.py
# Don't import from file_a
```

## Float Comparison Bugs

Comparing floating point numbers directly.

```python
# ❌ BUG - Float precision issues
x = 0.1 + 0.2
if x == 0.3:  # False! (x is 0.30000000000000004)
    print("Equal")

# ✅ FIX - Use tolerance
x = 0.1 + 0.2
tolerance = 1e-9
if abs(x - 0.3) < tolerance:
    print("Equal")

# ✅ FIX - Use math.isclose()
import math
x = 0.1 + 0.2
if math.isclose(x, 0.3):
    print("Equal")
```

## Performance Bugs

Code that runs slowly.

```python
# ❌ BUG - Inefficient string concatenation
result = ""
for i in range(1000):
    result = result + str(i)  # Creates new string each time!

# ✅ FIX - Use list and join
parts = []
for i in range(1000):
    parts.append(str(i))
result = "".join(parts)  # Much faster

# ❌ BUG - Repeated function calls
total = 0
for i in range(len(very_large_list)):  # len() called every iteration!
    total += very_large_list[i]

# ✅ FIX - Store in variable
total = 0
list_length = len(very_large_list)
for i in range(list_length):
    total += very_large_list[i]
```

## Debugging Workflow

### Step 1: Understand the Problem
What should happen vs what actually happens?

### Step 2: Isolate the Issue
Add print statements or use debugger to find exact location.

### Step 3: Check Assumptions
Verify your understanding of variables and state.

### Step 4: Test Hypothesis
Change one thing and verify it fixes the issue.

### Step 5: Clean Up
Remove debug code and verify fix is complete.

## Testing for Bugs

```python
def has_bug(data):
    if len(data) >= 1:
        return data[0]
    return None

# Test case 1: Normal input
assert has_bug([1, 2, 3]) == 1
print("✅ Test 1 passed")

# Test case 2: Single item
assert has_bug([1]) == 1
print("✅ Test 2 passed")

# Test case 3: Empty list - THIS CATCHES THE BUG
assert has_bug([]) is None
print("✅ Test 3 passed")

# Test case 4: None input
assert has_bug(None) is None  # This would crash, bug found!
```

## Quick Bug Checklist

- [ ] Program crashes? Look for None values or missing imports
- [ ] Wrong calculation? Check data types and order of operations
- [ ] Loop doesn't work? Verify range and loop variable
- [ ] String mismatch? Check case and whitespace
- [ ] Dictionary error? Use get() with default
- [ ] Performance issue? Look for O(n²) algorithms
- [ ] Unexpected behavior? Add type hints to catch errors
- [ ] Can't find bug? Add comprehensive test cases

Remember: Every programmer writes bugs. The key is learning effective debugging techniques to find and fix them quickly!
