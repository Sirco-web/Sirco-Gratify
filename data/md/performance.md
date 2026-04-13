# Performance Optimization

## Algorithm Optimization

### Time Complexity Analysis
Measure how runtime grows with input size.

```python
# O(1) - Constant time
def get_first_element(lst):
    return lst[0]

# O(n) - Linear time
def find_maximum(lst):
    max_val = lst[0]
    for item in lst:
        if item > max_val:
            max_val = item
    return max_val

# O(n²) - Quadratic time
def bubble_sort(lst):
    for i in range(len(lst)):
        for j in range(len(lst) - 1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
    return lst

# O(log n) - Logarithmic time
def binary_search(lst, target):
    left, right = 0, len(lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Space Complexity
Memory used by algorithm.

```python
# O(1) - Constant space
def increment(x):
    return x + 1

# O(n) - Linear space
def create_list(n):
    return [i for i in range(n)]

# O(n²) - Quadratic space
def create_matrix(n):
    return [[i + j for j in range(n)] for i in range(n)]
```

## Caching Strategies

### Memoization
Store function results to avoid recalculation.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# With limits
@lru_cache(maxsize=32)
def expensive_operation(x):
    return complex_calculation(x)
```

### Cache Invalidation
Invalid cache when data changes.

```python
class Cache:
    def __init__(self):
        self.data = {}
        self.timestamps = {}
    
    def get(self, key, ttl_seconds=3600):
        if key not in self.data:
            return None
        
        age = time.time() - self.timestamps[key]
        if age > ttl_seconds:
            del self.data[key]
            del self.timestamps[key]
            return None
        
        return self.data[key]
    
    def set(self, key, value):
        self.data[key] = value
        self.timestamps[key] = time.time()
```

### LRU Cache
Evict least recently used items when full.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

## Database Optimization

### Indexing
Speed up queries dramatically.

```sql
-- Create index on frequently queried column
CREATE INDEX idx_user_email ON users(email);

-- Composite index
CREATE INDEX idx_user_status_date ON users(status, created_date);

-- For faster sorting
CREATE INDEX idx_order_date_desc ON orders(created_date DESC);
```

### Query Optimization
```sql
-- BAD: Full table scan
SELECT * FROM orders WHERE YEAR(created_date) = 2024;

-- GOOD: Uses index
SELECT * FROM orders WHERE created_date >= '2024-01-01' AND created_date < '2025-01-01';

-- BAD: Subquery for every row
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- GOOD: Use JOIN
SELECT DISTINCT u.* FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

### Connection Pooling
Reuse database connections.

```python
from sqlalchemy import create_engine

# Connection pool
engine = create_engine(
    'postgresql://user:pass@localhost/db',
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

## Code Optimization

### Avoid Unnecessary Work
```python
# BAD: Creates list then checks size
if len([x for x in range(10000) if x % 2 == 0]) > 0:
    process()

# GOOD: Use any() which stops at first match
if any(x % 2 == 0 for x in range(10000)):
    process()
```

### Batch Operations
```python
# BAD: Individual inserts
for item in items:
    db.insert_one(item)

# GOOD: Batch insert
db.insert_many(items)
```

### String Concatenation
```python
# BAD: Creates new string on each +
result = ""
for word in words:
    result += word

# GOOD: Join creates once
result = "".join(words)
```

## Profiling Tools

### Python Profiling
```python
import cProfile
import pstats

# Profile function
cProfile.run('main()', 'stats.prof')

# View results
stats = pstats.Stats('stats.prof')
stats.sort_stats('cumulative').print_stats(10)
```

### Line Profiler
```python
from line_profiler import LineProfiler

profiler = LineProfiler()

@profiler
def slow_function():
    pass

profiler.print_stats()
```

## Distributed Performance

### Horizontal Scaling
Add more servers instead of upgrading single server.

### Load Balancing
Distribute requests across servers.

```
User → Load Balancer → Server 1
                    → Server 2
                    → Server 3
```

### Caching Layers
```
User → Application Cache (Redis)
    → Database Query Cache
    → Full Database
```

### Async Operations
Handle long operations without blocking.

```python
import asyncio

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Run multiple concurrently
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)
```

## Monitoring Performance

### Key Metrics
- **Response Time**: How long requests take
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **CPU Usage**: Processor utilization
- **Memory Usage**: RAM consumption
- **Database Query Time**: SQL performance

### Tools
- **New Relic**: Application performance monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log aggregation and analysis
