# Design Patterns & Architecture

## Creational Patterns

### Singleton Pattern
Ensures only one instance of a class exists.

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Thread-safe singleton
class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### Factory Pattern
Creates objects without specifying exact classes.

```python
class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        raise ValueError(f"Unknown animal: {animal_type}")

# Usage
dog = AnimalFactory.create_animal("dog")
```

### Builder Pattern
Constructs complex objects step by step.

```python
class DatabaseBuilder:
    def __init__(self):
        self.config = {}
    
    def set_host(self, host):
        self.config['host'] = host
        return self
    
    def set_port(self, port):
        self.config['port'] = port
        return self
    
    def build(self):
        return Database(self.config)

# Usage
db = DatabaseBuilder().set_host('localhost').set_port(5432).build()
```

## Structural Patterns

### Adapter Pattern
Makes incompatible interfaces compatible.

```python
class LegacyDatabase:
    def get_data(self):
        return {"raw": "data"}

class ModernInterface:
    def get_json(self):
        pass

class DatabaseAdapter(ModernInterface):
    def __init__(self, legacy_db):
        self.legacy = legacy_db
    
    def get_json(self):
        return json.dumps(self.legacy.get_data())
```

### Decorator Pattern
Adds behavior to objects dynamically.

```python
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Took {time.time() - start:.2f}s")
        return result
    return wrapper

@timing_decorator
def slow_function():
    time.sleep(1)
```

### Facade Pattern
Provides unified interface to subsystem.

```python
class ShoppingFacade:
    def __init__(self):
        self.inventory = Inventory()
        self.payment = PaymentGateway()
        self.shipping = ShippingService()
    
    def buy(self, item_id, user_id):
        if not self.inventory.has_item(item_id):
            return False
        if not self.payment.charge(user_id, price):
            return False
        return self.shipping.ship(user_id, item_id)
```

## Behavioral Patterns

### Observer Pattern
Objects notify multiple observers of state changes.

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer:
    def update(self, message):
        print(f"Received: {message}")
```

### Strategy Pattern
Encapsulates interchangeable algorithms.

```python
class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} with credit card"

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} via PayPal"

class Checkout:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def process(self, amount):
        return self.strategy.pay(amount)
```

### Command Pattern
Encapsulates requests as objects.

```python
class Command:
    def execute(self):
        pass

class TurnOnLight(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        self.light.on()
    
    def undo(self):
        self.light.off()

class RemoteControl:
    def __init__(self):
        self.commands = []
    
    def execute_command(self, command):
        command.execute()
        self.commands.append(command)
    
    def undo_last(self):
        if self.commands:
            self.commands.pop().undo()
```

## Architectural Patterns

### MVC (Model-View-Controller)
Separates concerns into three interconnected components.

```
Model: Data and business logic
View: Presentation layer
Controller: Input handling and coordination
```

### MVVM (Model-View-ViewModel)
Used in modern UI frameworks (React, Angular).

```
Model: Data source
View: UI components
ViewModel: State management and logic
```

### Microservices Architecture
Breaks application into loosely coupled services.

**Advantages:**
- Independent deployment
- Technology diversity
- Scalability

**Challenges:**
- Distributed system complexity
- Service coordination
- Data consistency

### Event-Driven Architecture
Components communicate via events.

```python
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        for handler in self.subscribers[type(event)]:
            handler(event)
```

### Layered Architecture
```
Presentation Layer → Business Logic → Persistence Layer → Database
```

## SOLID Principles

### Single Responsibility
Each class should have one reason to change.

```python
# Good
class UserValidator:
    def validate(self, user):
        pass

class UserRepository:
    def save(self, user):
        pass

# Bad
class User:
    def validate(self):
        pass
    
    def save_to_database(self):
        pass
```

### Open/Closed
Open for extension, closed for modification.

```python
# Use inheritance/interfaces instead of modifying existing code
class ReportFormat:
    def format(self, data):
        pass

class JSONReport(ReportFormat):
    def format(self, data):
        return json.dumps(data)

class CSVReport(ReportFormat):
    def format(self, data):
        return csv.dumps(data)
```

### Liskov Substitution
Subclasses must be substitutable for parent classes.

### Interface Segregation
Many specific interfaces beat one general interface.

### Dependency Inversion
Depend on abstractions, not concrete implementations.

```python
# Good: Depend on abstraction
class UserService:
    def __init__(self, database: DatabaseInterface):
        self.db = database

# Bad: Depend on concrete class
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()
```
