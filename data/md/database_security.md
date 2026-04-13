# Database Security & Optimization

## Database Connection Security

### Secure Connection Strings
```python
import os
from urllib.parse import quote_plus

# BAD: Hardcoded password
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# GOOD: Environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# GOOD: With special characters escaped
password = os.getenv('DB_PASSWORD')
escaped_password = quote_plus(password)
DATABASE_URL = f"postgresql://user:{escaped_password}@localhost/dbname"
```

### Connection Pooling
```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Number of kept connections
    max_overflow=20,     # Maximum overflow connections
    pool_recycle=3600,   # Recycle connection after 1 hour
    pool_pre_ping=True   # Verify connection before using
)
```

## SQL Injection Prevention

### Parameterized Queries
```python
# With SQLAlchemy ORM
from sqlalchemy import text

# SAFE: Parameterized query
result = db.session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": user_email}
).fetchall()

# SAFE: ORM query
users = User.query.filter_by(email=user_email).all()

# SAFE: Using SQLAlchemy core
from sqlalchemy import select, column, table
users = db.session.execute(
    select(User).where(User.email == user_email)
).scalars()
```

## Data Encryption

### Encrypt Sensitive Fields
```python
from cryptography.fernet import Fernet
import os

# Generate key (store securely)
key = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(key)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    
    _ssn = db.Column(db.LargeBinary)  # Encrypted SSN
    
    @property
    def ssn(self):
        return cipher.decrypt(self._ssn).decode()
    
    @ssn.setter
    def ssn(self, value):
        self._ssn = cipher.encrypt(value.encode())
```

## Database Access Control

### Row-Level Security (PostgreSQL)
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own data
CREATE POLICY user_policy ON users
    FOR SELECT
    USING (id = current_user_id());

-- Create policy: Users can only update their own records
CREATE POLICY user_update_policy ON users
    FOR UPDATE
    USING (id = current_user_id())
    WITH CHECK (id = current_user_id());
```

### Database User Privileges
```sql
-- Create read-only user
CREATE USER read_only WITH PASSWORD 'password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;

-- Create user with specific table access
CREATE USER app_user WITH PASSWORD 'password';
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT SELECT ON products TO app_user;
```

## Data Backup & Recovery

### Automated Backups
```bash
#!/bin/bash
# Backup PostgreSQL database
BACKUP_DIR="/backups/databases"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -U postgres mydatabase > "$BACKUP_DIR/backup_$DATE.sql"

# Upload to cloud storage
aws s3 cp "$BACKUP_DIR/backup_$DATE.sql" s3://my-backups/
```

### Point-in-Time Recovery
```bash
# PostgreSQL WAL archiving for PITR
# In postgresql.conf:
# wal_level = replica
# max_wal_senders = 3
# max_wal_keep_size = 1GB

# Restore to specific time
pg_restore --recovery-target-time='2024-01-15 14:30:00' backup.sql
```

## Query Optimization

### Explain Plans
```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id;

-- Look for sequential scans on large tables (bad)
-- Should use index scans instead
```

### Common Performance Issues
```sql
-- PROBLEM: N+1 queries
-- SELECT * FROM users;  -- 1000 queries
-- For each user, SELECT * FROM orders WHERE user_id = ?;  -- 999 queries

-- SOLUTION: Use JOIN or eager loading
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- PROBLEM: Missing indexes
-- SOLUTION: Create indexes on frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

## Data Validation

### Constraints
```sql
-- NOT NULL constraint
ALTER TABLE users ADD CONSTRAINT email_not_null CHECK (email IS NOT NULL);

-- UNIQUE constraint
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);

-- FOREIGN KEY constraint
ALTER TABLE orders ADD CONSTRAINT fk_user_id
    FOREIGN KEY (user_id) REFERENCES users(id);

-- CHECK constraint
ALTER TABLE users ADD CONSTRAINT age_check CHECK (age >= 18);
```

## Audit Logging

### Track Changes
```python
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(255))
    record_id = db.Column(db.Integer)
    action = db.Column(db.String(50))  # INSERT, UPDATE, DELETE
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Audit trigger (PostgreSQL)
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id, timestamp)
    VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user_id(), NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_audit AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

## Database Monitoring

### Key Metrics
```python
# Monitor with prometheus
from prometheus_client import Counter, Gauge, Histogram

db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration')
db_connections = Gauge('db_connections', 'Number of database connections')
db_errors = Counter('db_errors_total', 'Total database errors')

# Use in queries
@db_query_duration.time()
def run_query(sql):
    return db.execute(sql)
```

### Slow Query Logging
```sql
-- PostgreSQL: Log queries over 1 second
SET log_min_duration_statement = 1000;

-- MySQL: Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

## Schema Versioning

### Migration Tools
```bash
# Using Alembic (Python)
alembic init alembic
alembic revision --autogenerate -m "Add user table"
alembic upgrade head

# Using Flyway (Java/SQL)
flyway info
flyway migrate
```

### Version Control
```python
# Track migration history
class Migration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
```
