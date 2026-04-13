# Python Debugging Guide

## What is Debugging?

Debugging is the process of finding and fixing errors in your code. When your program doesn't work as expected, you need to investigate what went wrong and fix it.

## Common Python Errors

### SyntaxError
A syntax error occurs when Python can't understand your code.

```python
# ❌ WRONG - Missing colon
def hello()
    print("Hello")

# ✅ CORRECT
def hello():
    print("Hello")
```

### TypeError
Occurs when you try to do something with the wrong data type.

```python
# ❌ WRONG - Can't add string and integer
x = "hello" + 5

# ✅ CORRECT
x = "hello" + str(5)
```

### ValueError
Occurs when a function gets an argument of the right type but an inappropriate value.

```python
# ❌ WRONG - Can't convert non-numeric string to int
x = int("hello")

# ✅ CORRECT
x = int("123")
```

### IndexError
Trying to access an index that doesn't exist.

```python
# ❌ WRONG - List only has 3 items (index 0-2)
my_list = [1, 2, 3]
print(my_list[5])

# ✅ CORRECT
print(my_list[0])  # First item
```

### KeyError
Trying to access a dictionary key that doesn't exist.

```python
# ❌ WRONG - Key doesn't exist
my_dict = {"name": "John"}
print(my_dict["age"])

# ✅ CORRECT
print(my_dict.get("age", "Not found"))
```

### AttributeError
Trying to access an attribute that doesn't exist.

```python
# ❌ WRONG - String doesn't have method 'add'
text = "hello"
text.add("world")

# ✅ CORRECT
text = "hello" + "world"
```

## Debugging Tools

### Print Debugging

The simplest way to debug is using `print()` statements.

```python
def calculate_sum(a, b):
    print(f"Input a: {a}")
    print(f"Input b: {b}")
    result = a + b
    print(f"Result: {result}")
    return result

sum_result = calculate_sum(5, 3)
```

### Using assert

Assert statements check if something is True. If not, they raise an error.

```python
def divide(a, b):
    assert b != 0, "Cannot divide by zero!"
    return a / b

result = divide(10, 0)  # This will fail with clear message
```

### Try-Except Blocks

Catch errors gracefully instead of crashing.

```python
try:
    value = int(input("Enter a number: "))
    result = 10 / value
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An error occurred: {e}")
```

### Logging

Use logging instead of print for production code.

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing data: {data}")
    try:
        result = int(data) * 2
        logger.info(f"Result: {result}")
        return result
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return None
```

## Step-by-Step Debugging

1. **Reproduce the error** - Get it to happen consistently
2. **Isolate the problem** - Find the exact line causing it
3. **Understand the root cause** - Why is it happening?
4. **Fix it** - Make the necessary change
5. **Test the fix** - Make sure it works
6. **Check for similar issues** - Are there other occurrences?

## Debugging Example

Problem: Function returns wrong value

```python
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return average

result = calculate_average([1, 2, 3, 4, 5])
print(f"Average: {result}")  # Should be 3.0
```

If wrong output, add debugging:

```python
def calculate_average(numbers):
    print(f"Input: {numbers}")
    total = sum(numbers)
    print(f"Total: {total}")
    count = len(numbers)
    print(f"Count: {count}")
    average = total / count
    print(f"Average: {average}")
    return average

result = calculate_average([1, 2, 3, 4, 5])
```

Output shows exactly where the problem is.

## Debugging Best Practices

### Use Type Hints
Help catch errors early.

```python
def add(a: int, b: int) -> int:
    return a + b

add(5, 3)      # OK
add("5", "3")  # IDE warns about wrong type
```

### Write Tests
Find bugs before they reach production.

```python
def test_add():
    assert add(5, 3) == 8
    assert add(0, 0) == 0
    assert add(-5, 5) == 0
```

### Use a Debugger
Python has built-in debugger: pdb

```python
import pdb

def problematic_function():
    x = 5
    pdb.set_trace()  # Execution stops here, can inspect
    y = x + 10
    return y
```

### Read Error Messages
Python tells you exactly what's wrong.

```
Traceback (most recent call last):
  File "script.py", line 5, in <module>
    z = x / y
ZeroDivisionError: division by zero
```

## Common Debugging Mistakes

### ❌ Not Reading the Error
The error message tells you everything!

### ❌ Changing Multiple Things
Change one thing at a time so you know what fixed it.

### ❌ Not Testing After Fix
Always verify that your fix works.

### ❌ Ignoring Warnings
Warnings are hints about potential problems.

## Quick Debugging Checklist

- [ ] Read the error message carefully
- [ ] Identify the line causing the error
- [ ] Check variable values with print()
- [ ] Test individual components
- [ ] Use try-except for error handling
- [ ] Write tests to prevent regression
- [ ] Use type hints to catch errors early
- [ ] Clean up debug code before committing

Remember: Debugging is a skill. The more you practice, the faster you get at finding and fixing errors!
