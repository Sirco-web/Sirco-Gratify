# Data Structures and Algorithms

## Why Data Structures Matter

Choosing the right data structure can make your code 1000x faster.

### Time and Space Complexity

Big O notation shows how an algorithm scales.

```
O(1)     - Constant time - Always same speed         - Perfect
O(log n) - Logarithmic   - Doubles = +1 step        - Great
O(n)     - Linear        - 10x data = 10x slower   - Good
O(n²)    - Quadratic     - 10x data = 100x slower - Bad
O(2ⁿ)    - Exponential   - 10x data = impossibly slow - Terrible
```

## Common Data Structures

### List / Array

Best for: Ordered data, iteration, indexing

```python
# Time Complexity
my_list = [1, 2, 3, 4, 5]

my_list[0]           # O(1) - Fast
my_list.append(6)    # O(1) - Fast
my_list.insert(0, 0) # O(n) - Slow (shifts everything)
my_list.remove(3)    # O(n) - Slow (searches + shifts)

# Space: O(n)
```

### Dictionary / Hash Map

Best for: Fast lookups by key

```python
# Time Complexity
user_id_to_name = {
    1: 'Alice',
    2: 'Bob',
    3: 'Charlie'
}

user_id_to_name[1]           # O(1) - Very fast
user_id_to_name[999]         # O(1) - Still fast
user_id_to_name[1] = 'Alicia' # O(1) - Fast
del user_id_to_name[2]       # O(1) - Fast

# Space: O(n)
```

### Set

Best for: Unique values, membership testing

```python
# Time Complexity
unique_ids = {1, 2, 3, 4, 5}

1 in unique_ids        # O(1) - Very fast
unique_ids.add(6)      # O(1) - Fast
unique_ids.remove(1)   # O(1) - Fast

# Space: O(n)
```

### LinkedList

Best for: Frequent insertions/deletions at beginning

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def insert_at_start(self, data):  # O(1)
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def insert_at_index(self, index, data):  # O(n)
        # Must traverse to position
        current = self.head
        for _ in range(index):
            current = current.next
        # Insert...

# Space: O(n)
```

### Stack

Best for: Undo/redo, recursion, bracket matching

```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):  # O(1)
        self.items.append(item)
    
    def pop(self):  # O(1)
        return self.items.pop()
    
    def peek(self):  # O(1)
        return self.items[-1]
    
    def is_empty(self):  # O(1)
        return len(self.items) == 0

# Check if brackets match
def is_balanced(text):
    stack = Stack()
    pairs = {'(': ')', '[': ']', '{': '}'}
    
    for char in text:
        if char in pairs:
            stack.push(char)
        elif char in pairs.values():
            if stack.is_empty():
                return False
            if pairs[stack.pop()] != char:
                return False
    
    return stack.is_empty()

# Space: O(n)
```

### Queue

Best for: Task scheduling, breadth-first search

```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):  # O(1)
        self.items.append(item)
    
    def dequeue(self):  # O(1)
        return self.items.popleft()
    
    def is_empty(self):  # O(1)
        return len(self.items) == 0

# Process tasks in order
task_queue = Queue()
task_queue.enqueue('task1')
task_queue.enqueue('task2')
task_queue.enqueue('task3')

while not task_queue.is_empty():
    task = task_queue.dequeue()
    print(f"Processing {task}")

# Space: O(n)
```

## Common Algorithms

### Sorting

```python
# Bubble Sort - O(n²) - SLOW
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Quick Sort - O(n log n) - FAST
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

# Use built-in - O(n log n)
sorted_arr = sorted(arr)
```

### Searching

```python
# Linear Search - O(n) - OK for small lists
def linear_search(arr, target):
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

# Binary Search - O(log n) - Fast for sorted lists
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found

# Array must be sorted for binary search
sorted_arr = [1, 2, 3, 4, 5, 6, 7, 8, 9]
result = binary_search(sorted_arr, 5)  # Returns 4
```

## Problem Solving Patterns

### Two Pointers

```python
# Find pair that sums to target
def two_sum(arr, target):
    left, right = 0, len(arr) - 1
    
    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return [arr[left], arr[right]]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    
    return None

# Requires sorted array
result = two_sum([1, 2, 3, 4, 5, 6], 9)  # [3, 6]
```

### Sliding Window

```python
# Find longest substring without repeating characters
def longest_unique_substring(s):
    char_index = {}
    max_length = 0
    start = 0
    
    for end, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        
        char_index[char] = end
        max_length = max(max_length, end - start + 1)
    
    return max_length

result = longest_unique_substring("abcabcbb")  # 3 (abc)
```

### Binary Tree Traversal

```python
class TreeNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None

# Depth-First Search (DFS)
def dfs(node):
    if not node:
        return
    print(node.val)       # Process node
    dfs(node.left)        # Process left subtree
    dfs(node.right)       # Process right subtree

# Breadth-First Search (BFS)
from collections import deque

def bfs(root):
    if not root:
        return
    
    queue = deque([root])
    while queue:
        node = queue.popleft()
        print(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
```

### Dynamic Programming

```python
# Fibonacci - DP vs Recursion

# ❌ Slow recursion - O(2ⁿ)
def fib_slow(n):
    if n <= 1:
        return n
    return fib_slow(n-1) + fib_slow(n-2)  # Recalculates same values!

# ✅ Fast DP - O(n)
def fib_fast(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

# Fibonacci of 35
# fib_slow(35) - Takes seconds!
# fib_fast(35) - Instant
```

## Choosing the Right Structure

| Task | Best | Why |
|------|------|-----|
| Ordered data, iteration | List | O(1) indexing |
| Key-value lookup | Dict | O(1) lookup |
| Unique items | Set | O(1) membership |
| Undo/Redo | Stack | LIFO access |
| Task queue | Queue | FIFO access |
| Sorted search | Binary tree | O(log n) search |
| Ordered items | Sorted List | O(1) access |

## Performance Comparison

```python
import time

# Benchmark: N lookups in different structures

n = 1000000

# List - O(n) for search
my_list = list(range(n))
start = time.time()
for _ in range(1000):
    500000 in my_list
print(f"List: {time.time() - start:.3f}s")

# Dictionary - O(1) for search
my_dict = {i: i for i in range(n)}
start = time.time()
for _ in range(1000):
    500000 in my_dict
print(f"Dict: {time.time() - start:.3f}s")  # Much faster!

# Result:
# List: 5.234s
# Dict: 0.001s  - 5000x faster!
```

## Optimization Tips

1. **Choose right structure** - Dict for lookups, Set for unique, List for order
2. **Avoid nested loops** - O(n²) is too slow
3. **Use built-in functions** - They're optimized in C
4. **Cache expensive operations** - Don't recalculate
5. **Sort once, search many** - Use binary search after sorting
6. **Profile before optimizing** - Find the real bottleneck

Remember: The best algorithm is the one that solves your problem within time/space constraints!
