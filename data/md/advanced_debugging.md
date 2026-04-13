# Advanced Debugging Techniques

## Memory Debugging
Memory leaks occur when allocated memory is not freed. Use tools like Valgrind (Linux), Address Sanitizer, or Memory Profiler (Python).

```python
# Python memory leak example
import tracemalloc
tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

## Race Conditions
Race conditions occur when multiple threads access shared data simultaneously without synchronization.

**Symptoms:** Non-deterministic crashes, intermittent test failures, data corruption.

**Solutions:**
- Use locks (Mutex, Lock, RLock)
- Atomic operations
- Immutable data structures
- Thread-safe queues
- Avoid global state

```python
import threading
lock = threading.Lock()

with lock:
    # Critical section - only one thread at a time
    shared_variable += 1
```

## Deadlock Detection
Deadlock occurs when threads wait for each other indefinitely.

**Prevention:**
- Always acquire locks in the same order
- Use timeout on lock acquisition
- Use lock-free data structures
- Avoid nested locks when possible

## Profiling and Bottleneck Analysis
Identify slow code sections:

```python
import cProfile
import pstats

cProfile.run('my_function()', 'output.prof')
p = pstats.Stats('output.prof')
p.sort_stats('cumulative').print_stats(10)
```

## GDB Debugging for C/C++
```bash
gdb ./program
(gdb) break main
(gdb) run
(gdb) step
(gdb) print variable_name
(gdb) backtrace
```

## Heisenbug Investigation
Heisenbugs disappear when you try to debug them (timing-sensitive bugs).

**Strategies:**
- Add minimal logging (avoid changing timing)
- Use gdb with conditional breakpoints
- Reproduce in production-like environment
- Check for race conditions or timing issues
- Use Thread Sanitizer: `clang -fsanitize=thread`

## Debugging Distributed Systems
- Use correlation IDs across all logs
- Implement distributed tracing (Jaeger, Zipkin)
- Check clock synchronization (NTP)
- Monitor network latency
- Use circuit breakers and timeouts

## Code Coverage Analysis
Ensure all code paths are tested:

```python
# Using coverage.py
coverage run -m pytest test_suite.py
coverage report
coverage html  # Generate HTML report
```

## Reverse Debugging
Replay execution backwards to find bug origin:

```bash
# GDB with reverse debugging
(gdb) record
(gdb) continue  # Run forward
(gdb) reverse-step  # Step backwards
(gdb) reverse-continue  # Continue backwards
```

## Common Bug Patterns
1. **Off-by-one errors**: Loop boundaries incorrect
2. **Null pointer dereference**: Accessing null without checking
3. **Buffer overflow**: Writing beyond buffer limits
4. **Use-after-free**: Using memory after deallocation
5. **Uninitialized variables**: Using undefined values
6. **Type confusion**: Treating one type as another
7. **Integer overflow**: Exceeding type limits

## Interactive Debugging Tools
- **pdb** (Python): Step through code interactively
- **ipdb** (Python): IPython kernel debugger
- **pry** (Ruby): Feature-rich debugger
- **Chrome DevTools**: Frontend debugging
- **VS Code Debugger**: VSCode built-in debugger
