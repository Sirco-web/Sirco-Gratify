# Cryptography Basics

## Encryption Types

### Symmetric Encryption
Same key for encryption and decryption. Fast but key must be shared securely.

```python
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
plaintext = b"Secret message"
ciphertext = cipher.encrypt(plaintext)
print(ciphertext)

# Decrypt
decrypted = cipher.decrypt(ciphertext)
print(decrypted)
```

### AES Encryption
Industry standard symmetric encryption.

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Generate key and IV
key = os.urandom(32)  # 256-bit key
iv = os.urandom(16)   # 128-bit IV

# Encrypt
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()
ciphertext = encryptor.update(b"Secret data") + encryptor.finalize()

# Decrypt
decryptor = cipher.decryptor()
plaintext = decryptor.update(ciphertext) + decryptor.finalize()
```

### Asymmetric Encryption
Public and private key pair. Slower but no key sharing needed.

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# Generate key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Encrypt with public key
plaintext = b"Secret message"
ciphertext = public_key.encrypt(
    plaintext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Decrypt with private key
decrypted = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
```

## Hashing

### Secure Password Hashing
```python
import bcrypt

# Hash password
password = b"my_secure_password"
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))

# Verify password
password_attempt = b"my_secure_password"
if bcrypt.checkpw(password_attempt, hashed):
    print("Password correct")
else:
    print("Password incorrect")
```

### Alternative: Argon2
```python
from argon2 import PasswordHasher

hasher = PasswordHasher()

# Hash
hashed = hasher.hash("password123")

# Verify
try:
    hasher.verify(hashed, "password123")
    print("Valid")
except:
    print("Invalid")
```

### SHA Hashing
```python
import hashlib

# SHA-256 (good for checksums, NOT for passwords)
data = b"Some data"
sha256_hash = hashlib.sha256(data).hexdigest()

# PBKDF2 (password hashing)
from hashlib import pbkdf2_hmac
hashed = pbkdf2_hmac('sha256', b'password', b'salt', 100000)
```

## Digital Signatures

### Sign and Verify
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Sign message
message = b"Important message"
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Verify signature
try:
    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signature valid")
except:
    print("Signature invalid")
```

## Key Management

### Secure Key Storage
```python
import os
from cryptography.fernet import Fernet
import json

# Never hardcode keys
# BAD:
SECRET_KEY = "my-secret-key-1234"

# GOOD: Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY')

# BETTER: Use key management service
import hvac
client = hvac.Client(url='http://localhost:8200')
secret = client.secrets.kv.read_secret_version(path='my-secret')
SECRET_KEY = secret['data']['data']['key']

# Key rotation
def rotate_key():
    old_key = os.getenv('SECRET_KEY')
    new_key = Fernet.generate_key()
    
    # Re-encrypt all data with new key
    re_encrypt_all_data(old_key, new_key)
    
    # Update key in key management system
    store_key_securely(new_key)
```

### Secrets Manager
```python
# AWS Secrets Manager
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='my-db-password')
password = secret['SecretString']

# Google Secret Manager
from google.cloud import secretmanager

def access_secret(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

## TLS/SSL Certificates

### Generate Self-Signed Certificate
```bash
# Generate private key
openssl genrsa -out private.key 2048

# Generate certificate
openssl req -new -x509 -key private.key -out certificate.crt -days 365
```

### Use in Flask
```python
from flask import Flask
from OpenSSL import SSL

app = Flask(__name__)

# Using self-signed certificate
context = SSL.Context(SSL.SSLv23)
context.use_privateKey_file('private.key')
context.use_certificate_file('certificate.crt')

app.run(ssl_context=context)

# Or simply
app.run(ssl_context='adhoc')  # Generates certificate on the fly
```

## Certificate Pinning
Prevent man-in-the-middle attacks.

```python
import requests
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

# Pin certificate
cert = """-----BEGIN CERTIFICATE-----
...certificate content...
-----END CERTIFICATE-----"""

session = requests.Session()
response = session.get(
    'https://api.example.com/data',
    verify=cert
)
```

## Random Number Generation

### Secure Random
```python
import secrets
import os

# Generate random token
token = secrets.token_hex(32)  # 64 hex characters

# Generate random bytes
random_bytes = os.urandom(32)

# Generate random integer
random_int = secrets.randbelow(1000)

# Choose random item
random_choice = secrets.choice(['option1', 'option2', 'option3'])
```

## Salting

### Password Salting
```python
import os
import hashlib

def hash_password(password):
    # Generate random salt
    salt = os.urandom(32)
    
    # Hash password with salt
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    # Store salt + hash
    return salt + hashed

def verify_password(password, stored_salt_hash):
    salt = stored_salt_hash[:32]
    stored_hash = stored_salt_hash[32:]
    
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    return hashed == stored_hash
```

## Cryptographic Best Practices

```python
# DO:
# ✅ Use established libraries (cryptography, bcrypt)
# ✅ Use appropriate algorithm for purpose
# ✅ Hash passwords (bcrypt, Argon2)
# ✅ Use salt for hashing
# ✅ Use random IVs and nonces
# ✅ Keep keys secure with management services
# ✅ Use TLS for data in transit
# ✅ Rotate keys regularly

# DON'T:
# ❌ Implement your own crypto algorithms
# ❌ Use weak algorithms (MD5, SHA1 for passwords)
# ❌ Hardcode secrets in code
# ❌ Use predictable random number generators
# ❌ Reuse IVs or nonces
# ❌ Log sensitive data
# ❌ Send passwords over unencrypted connections
```
