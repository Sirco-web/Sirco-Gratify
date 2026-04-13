# DevOps & Cloud Deployment

## Docker Containerization

### Basic Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run application
CMD ["python", "app.py"]
```

### Multi-Stage Build
```dockerfile
# Build stage
FROM python:3.11 as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .

ENV PATH=/root/.local/bin:$PATH

CMD ["python", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
    depends_on:
      - db
    volumes:
      - ./:/app
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
```

## Kubernetes

### Basic Pod Deployment
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
  labels:
    app: myapp

spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 5000
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-url
    resources:
      requests:
        memory: "256Mi"
        cpu: "500m"
      limits:
        memory: "512Mi"
        cpu: "1000m"
```

### Deployment with Auto-Scaling
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment

spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:1.0
        ports:
        - containerPort: 5000
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## CI/CD Pipeline

### GitHub Actions
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8 mypy
    
    - name: Lint with flake8
      run: |
        flake8 --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 --count --exit-zero --max-complexity=10
    
    - name: Test with pytest
      run: |
        pytest --cov=src --cov-report=xml
      env:
        DATABASE_URL: "postgresql://postgres:postgres@localhost/test"
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/myapp:latest
```

## Infrastructure as Code

### Terraform
```hcl
# Configure AWS provider
provider "aws" {
  region = "us-east-1"
}

# Create RDS database
resource "aws_db_instance" "main" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine              = "postgres"
  engine_version      = "15.1"
  instance_class      = "db.t3.micro"
  identifier          = "app-database"
  username            = var.db_username
  password            = var.db_password
  skip_final_snapshot = true
}

# Create S3 bucket
resource "aws_s3_bucket" "app_bucket" {
  bucket = "my-app-bucket-${var.environment}"
}

# Create EC2 instance
resource "aws_instance" "app" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "app-server"
  }
}

# Output values
output "database_endpoint" {
  value = aws_db_instance.main.endpoint
}
```

## Monitoring & Logging

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_connections = Gauge('active_connections', 'Number of active connections')

# Use in application
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_count.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    request_duration.observe(duration)
    return response
```

### Structured Logging
```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Setup JSON logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Log with context
logger.info('User login', extra={
    'user_id': 123,
    'ip': '192.168.1.1',
    'timestamp': datetime.utcnow().isoformat()
})
```

## Health Checks

### Liveness & Readiness
```python
@app.route('/health', methods=['GET'])
def health():
    """Liveness probe - is application running?"""
    return {'status': 'healthy'}, 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe - is application ready for traffic?"""
    try:
        db.session.execute('SELECT 1')
        redis_client.ping()
        return {'status': 'ready'}, 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {'status': 'not ready', 'reason': str(e)}, 503
```

## Blue-Green Deployment

```yaml
# In Kubernetes manifest
---
apiVersion: v1
kind: Service
metadata:
  name: app-service

spec:
  selector:
    app: myapp
    version: green  # Points to green deployment
  ports:
  - port: 80
    targetPort: 5000

---
# Deploy new version as "blue"
# Once verified, update service selector to point to "blue"
# This allows instant rollback
```

## Disaster Recovery

### Backup Strategy
```bash
#!/bin/bash
# Daily database backup to S3

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.sql"

# Backup database
pg_dump -U postgres mydb | gzip > $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://my-backups/

# Cleanup old backups (keep 7 days)
aws s3 rm s3://my-backups --recursive --exclude "*" --include "backup_*" \
  --older-than 7 days
```

## Security Best Practices

- Use environment variables for secrets, not config files
- Implement network policies to restrict traffic
- Use TLS for all communications
- Regularly update dependencies
- Scan images for vulnerabilities
- Implement RBAC (Role-Based Access Control)
- Audit all changes
- Use secrets management (Vault, AWS Secrets Manager)
