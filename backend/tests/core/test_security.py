"""
Unit tests for password hashing and verification.
"""
import pytest
from app.core.security import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_hash_password_creates_valid_hash(self):
        """Should create a valid bcrypt hash."""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # Bcrypt hash starts with $2b$ and is 60 characters
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60
    
    def test_verify_correct_password_returns_true(self):
        """Should return True when password matches hash."""
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password_returns_false(self):
        """Should return False when password doesn't match."""
        password = "CorrectPassword"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword", hashed) is False
    
    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (different salts)."""
        password = "password123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_hash_is_irreversible(self):
        """Should not be able to retrieve original password from hash."""
        password = "SecretPassword"
        hashed = hash_password(password)
        
        # Hash should not contain original password
        assert password not in hashed
        assert password.lower() not in hashed.lower()


class TestPasswordVerification:
    """Test password verification edge cases."""
    
    def test_verify_empty_password(self):
        """Should handle empty password gracefully."""
        empty_password = ""
        hashed = hash_password(empty_password)
        
        assert verify_password(empty_password, hashed) is True
        assert verify_password("notempty", hashed) is False
    
    def test_verify_invalid_hash_returns_false(self):
        """Should return False for invalid hash format."""
        password = "password123"
        invalid_hash = "not_a_valid_bcrypt_hash"
        
        assert verify_password(password, invalid_hash) is False
    
    def test_verify_with_empty_hash_returns_false(self):
        """Should return False when hash is empty string."""
        password = "password123"
        assert verify_password(password, "") is False
    
    def test_case_sensitive_verification(self):
        """Password verification should be case-sensitive."""
        password = "MyPassword"
        hashed = hash_password(password)
        
        assert verify_password("MyPassword", hashed) is True
        assert verify_password("mypassword", hashed) is False
        assert verify_password("MYPASSWORD", hashed) is False


class TestPasswordSecurity:
    """Test security properties of password hashing."""
    
    def test_long_password(self):
        """Should handle long passwords correctly."""
        # Bcrypt has 72 byte limit but our function handles it
        long_password = "a" * 100
        hashed = hash_password(long_password)
        
        assert verify_password(long_password, hashed) is True
    
    def test_special_characters(self):
        """Should handle special characters in passwords."""
        special_password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/"
        hashed = hash_password(special_password)
        
        assert verify_password(special_password, hashed) is True
    
    def test_unicode_characters(self):
        """Should handle unicode characters in passwords."""
        unicode_password = "Пароль123🔐"
        hashed = hash_password(unicode_password)
        
        assert verify_password(unicode_password, hashed) is True
    
    def test_hashing_performance(self):
        """Hashing should complete in reasonable time."""
        import time
        
        password = "TestPassword123"
        start = time.time()
        hash_password(password)
        duration = time.time() - start
        
        # With rounds=12, should complete in under 0.5 seconds
        assert duration < 0.5


class TestBcryptRounds:
    """Test bcrypt rounds configuration."""
    
    def test_hash_uses_12_rounds(self):
        """Hash should use 12 rounds (12 cost factor)."""
        password = "password"
        hashed = hash_password(password)
        
        # Bcrypt format: $2b$12$...
        # The "12" is the cost factor (rounds = 2^12)
        cost_factor = hashed.split("$")[2]
        assert cost_factor == "12"
