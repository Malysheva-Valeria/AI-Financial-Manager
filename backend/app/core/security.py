"""
Security utilities for password hashing and verification.

Uses bcrypt via passlib for secure, irreversible password hashing.
"""
from passlib.context import CryptContext

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
