# Concurrency & Async Programming

## Threading in Python

### Basic Threading
```python
import threading

def worker(name):
    print(f"Worker {name} starting")
    time.sleep(2)
    print(f"Worker {name} done")

# Create threads
thread1 = threading.Thread(target=worker, args=("A",))
thread2 = threading.Thread(target=worker, args=("B",))

# Start threads
thread1.start()
thread2.start()

# Wait for completion
thread1.join()
thread2.join()
print("All threads complete")
```

### Thread Synchronization
```python
import threading

class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance
        self.lock = threading.Lock()
    
    def withdraw(self, amount):
        # Without lock: race condition
        # With lock: thread-safe
        with self.lock:
            if self.balance >= amount:
                temp = self.balance
                temp -= amount
                self.balance = temp
                return True
            return False
    
    def deposit(self, amount):
        with self.lock:
            self.balance += amount

# Thread-safe counter
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
    
    def value(self):
        with self._lock:
            return self._value
```

### Condition Variables
```python
import threading

class Buffer:
    def __init__(self):
        self.items = []
        self.condition = threading.Condition()
    
    def put(self, item):
        with self.condition:
            self.items.append(item)
            print(f"Produced {item}")
            self.condition.notify()  # Notify waiting threads
    
    def get(self):
        with self.condition:
            # Wait until buffer has items
            self.condition.wait_for(lambda: len(self.items) > 0)
            item = self.items.pop(0)
            print(f"Consumed {item}")
            return item
```

## Async/Await (Python)

### Basic Async
```python
import asyncio

async def fetch_data(url):
    print(f"Fetching {url}")
    await asyncio.sleep(1)  # Simulate network delay
    print(f"Got data from {url}")
    return f"Data from {url}"

async def main():
    # Run concurrently
    results = await asyncio.gather(
        fetch_data("http://api1.com"),
        fetch_data("http://api2.com"),
        fetch_data("http://api3.com")
    )
    print(results)

# Run
asyncio.run(main())
```

### Async with Streams
```python
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch_url(session, url))
        
        results = await asyncio.gather(*tasks)
        return results

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()

urls = ["http://api.example.com/1", "http://api.example.com/2"]
result = asyncio.run(fetch_all(urls))
```

### Async Context Managers
```python
class AsyncDatabaseConnection:
    async def __aenter__(self):
        self.connection = await connect_to_db()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

# Usage
async def query_database():
    async with AsyncDatabaseConnection() as db:
        data = await db.query("SELECT * FROM users")
        return data
```

## Multiprocessing

### Process Pool
```python
from multiprocessing import Pool
import os

def cpu_intensive_task(n):
    print(f"Process {os.getpid()} processing {n}")
    result = sum(i*i for i in range(n))
    return result

if __name__ == '__main__':
    # Use process pool for CPU-bound tasks
    with Pool(processes=4) as pool:
        results = pool.map(cpu_intensive_task, [100000, 200000, 300000, 400000])
    
    print(results)
```

### Process Communication
```python
from multiprocessing import Process, Queue

def worker(queue):
    for i in range(5):
        queue.put(f"Item {i}")
    queue.put(None)  # Signal end

if __name__ == '__main__':
    queue = Queue()
    
    p = Process(target=worker, args=(queue,))
    p.start()
    
    while True:
        item = queue.get()
        if item is None:
            break
        print(f"Main got: {item}")
    
    p.join()
```

## GIL (Global Interpreter Lock)
Python's threading limitation for CPU-bound tasks.

```python
import threading
import time

def cpu_bound():
    total = 0
    for i in range(100000000):
        total += i
    return total

# Single threaded
start = time.time()
cpu_bound()
cpu_bound()
print(f"Sequential: {time.time() - start:.2f}s")

# Multithreaded (slower due to GIL)
start = time.time()
t1 = threading.Thread(target=cpu_bound)
t2 = threading.Thread(target=cpu_bound)
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Threaded: {time.time() - start:.2f}s")

# For CPU-bound: use multiprocessing instead
```

## Producer-Consumer Pattern

```python
import threading
import queue
import time

def producer(q):
    for i in range(10):
        print(f"Producing item {i}")
        q.put(i)
        time.sleep(0.5)

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consuming item {item}")
        q.task_done()

if __name__ == '__main__':
    q = queue.Queue()
    
    # Create producer and consumer threads
    producer_thread = threading.Thread(target=producer, args=(q,))
    consumer_thread = threading.Thread(target=consumer, args=(q,))
    
    producer_thread.start()
    consumer_thread.start()
    
    producer_thread.join()
    q.put(None)  # Signal consumer to stop
    consumer_thread.join()
```

## Deadlock Avoidance

```python
import threading
import time

# DEADLOCK EXAMPLE - DO NOT USE
lock1 = threading.Lock()
lock2 = threading.Lock()

def thread1_func():
    with lock1:
        time.sleep(0.1)
        with lock2:  # Waits for lock2
            pass

def thread2_func():
    with lock2:
        time.sleep(0.1)
        with lock1:  # Waits for lock1 - DEADLOCK!
            pass

# SOLUTION: Always acquire locks in same order
def thread1_func_safe():
    with lock1:
        time.sleep(0.1)
        with lock2:
            pass

def thread2_func_safe():
    with lock1:  # Same order as thread1
        time.sleep(0.1)
        with lock2:
            pass
```

## Thread Pool Executor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download_file(url):
    print(f"Downloading {url}")
    time.sleep(2)
    return f"Downloaded {url}"

urls = ["url1", "url2", "url3", "url4"]

# Use thread pool
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all tasks
    futures = [executor.submit(download_file, url) for url in urls]
    
    # Process results as they complete
    for future in as_completed(futures):
        print(future.result())

# Or use map (maintains order)
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(download_file, urls)
    for result in results:
        print(result)
```

## Lock-Free Programming

```python
from queue import Queue
import threading

# Queue is thread-safe without explicit locks
queue = Queue(maxsize=10)

def producer():
    for i in range(100):
        queue.put(i)

def consumer():
    while True:
        item = queue.get()
        if item is None:
            break
        print(f"Processing {item}")

# Use thread-safe data structures instead of locks
```

## Barriers for Synchronization

```python
import threading

def worker(barrier, name):
    print(f"{name} waiting at barrier")
    barrier.wait()  # Wait for all threads
    print(f"{name} proceeding")

if __name__ == '__main__':
    barrier = threading.Barrier(3)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(barrier, f"Thread-{i}"))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
```
