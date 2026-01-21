"""
Security utilities for password hashing, verification, and JWT token management.

Uses bcrypt via passlib for secure, irreversible password hashing.
Uses python-jose for JWT token generation and validation.
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status

from app.core.config import settings

# Configure password hashing context
# Using bcrypt with 12 rounds (balance between security and performance)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        plain_password: The plaintext password to hash
    
    Returns:
        str: The bcrypt hash (includes algorithm, cost, salt, and hash)
    
    Note:
        - Each call produces a different hash (unique random salt)
        - Hash format: $2b$12$[22-char-salt][31-char-hash]
        - Cannot be reversed to get original password
    
    Example:
        >>> hashed = hash_password("MySecurePassword123")
        >>> print(hashed)
        '$2b$12$abc...xyz'
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The bcrypt hash to verify against
    
    Returns:
        bool: True if password matches, False otherwise
    
    Note:
        - Timing-safe comparison (resistant to timing attacks)
        - Does NOT decrypt the hash, compares cryptographically
    
    Example:
        >>> hashed = hash_password("MyPassword")
        >>> verify_password("MyPassword", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Invalid hash format or other error
        return False


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a JWT access token for a user.
    
    Args:
        email: User's email address (used as token subject)
        expires_delta: Optional custom expiration time. 
                      Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from settings.
    
    Returns:
        str: Encoded JWT token string
    
    Token Payload:
        {
            "sub": "user@example.com",  # subject - user email
            "exp": 1234567890,           # expiration timestamp
            "iat": 1234567800            # issued at timestamp
        }
    
    Example:
        >>> token = create_access_token("user@example.com")
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    payload = {
        "sub": email,  # subject - user email
        "exp": expire,  # expiration time
        "iat": now      # issued at time
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> str:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        str: The user email (subject) from the token
    
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or expired
    
    Validation:
        - Verifies signature using SECRET_KEY
        - Checks expiration time
        - Ensures token structure is valid
    
    Example:
        >>> token = create_access_token("user@example.com")
        >>> email = decode_access_token(token)
        >>> print(email)
        'user@example.com'
        
        >>> # Expired or invalid token
        >>> decode_access_token("invalid.token.here")
        HTTPException: 401 Unauthorized
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
        return email
        
    except JWTError:
        raise credentials_exception
