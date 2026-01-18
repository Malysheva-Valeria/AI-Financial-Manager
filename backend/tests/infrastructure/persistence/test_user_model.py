"""
Integration tests for UserModel ORM.
Tests database operations and Pydantic validation.
"""
import pytest
from sqlmodel import Session, select
from pydantic import ValidationError

from app.infrastructure.persistence.user_model import UserModel, TrackingModeEnum


class TestUserModel:
    """Test UserModel database operations and validation."""
    
    def test_create_user_in_database(self, session: Session):
        """Test creating a user and persisting to database."""
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$" + "x" * 50,  # Valid bcrypt hash format
            tracking_mode=TrackingModeEnum.MANUAL
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.tracking_mode == TrackingModeEnum.MANUAL
        assert user.is_premium is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_email_uniqueness_constraint(self, session: Session):
        """Test that email must be unique."""
        user1 = UserModel(
            email="unique@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user1)
        session.commit()
        
        # Attempt to create another user with same email
        user2 = UserModel(
            email="unique@example.com",
            password_hash="$2b$12$" + "y" * 50
        )
        session.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            session.commit()
    
    def test_email_lowercase_validator(self):
        """Test that email is normalized to lowercase."""
        user = UserModel(
            email="Test@EXAMPLE.COM",
            password_hash="$2b$12$" + "x" * 50
        )
        
        assert user.email == "test@example.com"
    
    def test_email_strip_whitespace(self):
        """Test that email whitespace is stripped."""
        user = UserModel(
            email="  test@example.com  ",
            password_hash="$2b$12$" + "x" * 50
        )
        
        assert user.email == "test@example.com"
    
    def test_invalid_email_raises_validation_error(self):
        """Test that invalid email format is rejected."""
        with pytest.raises(ValidationError):
            UserModel(
                email="not-an-email",
                password_hash="$2b$12$" + "x" * 50
            )
    
    def test_empty_email_raises_validation_error(self):
        """Test that empty email is rejected."""
        with pytest.raises(ValidationError):
            UserModel(
                email="",
                password_hash="$2b$12$" + "x" * 50
            )
    
    def test_short_password_hash_raises_validation_error(self):
        """Test that invalid password hash is rejected."""
        with pytest.raises(ValidationError, match="bcrypt hashes are 60 chars minimum"):
            UserModel(
                email="test@example.com",
                password_hash="too_short"
            )
    
    def test_empty_password_hash_raises_validation_error(self):
        """Test that empty password hash is rejected."""
        with pytest.raises(ValidationError):
            UserModel(
                email="test@example.com",
                password_hash=""
            )
    
    def test_tracking_mode_enum_validation(self):
        """Test that tracking_mode accepts valid enum values."""
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$" + "x" * 50,
            tracking_mode=TrackingModeEnum.AUTO_MONO
        )
        
        assert user.tracking_mode == TrackingModeEnum.AUTO_MONO
    
    def test_default_tracking_mode_is_manual(self):
        """Test that default tracking mode is MANUAL."""
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        
        assert user.tracking_mode == TrackingModeEnum.MANUAL
    
    def test_empty_mono_token_raises_validation_error(self):
        """Test that empty string mono_token is rejected."""
        with pytest.raises(ValidationError, match="cannot be empty string"):
            UserModel(
                email="test@example.com",
                password_hash="$2b$12$" + "x" * 50,
                mono_token=""
            )
    
    def test_none_mono_token_is_valid(self):
        """Test that None mono_token is valid."""
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$" + "x" * 50,
            mono_token=None
        )
        
        assert user.mono_token is None
    
    def test_webhook_hash_alphanumeric_validation(self):
        """Test that webhook_hash must be alphanumeric."""
        with pytest.raises(ValidationError, match="must be alphanumeric"):
            UserModel(
                email="test@example.com",
                password_hash="$2b$12$" + "x" * 50,
                webhook_hash="invalid-hash-with-dash"
            )
    
    def test_webhook_hash_minimum_length(self):
        """Test that webhook_hash must be at least 16 characters."""
        with pytest.raises(ValidationError, match="at least 16 characters"):
            UserModel(
                email="test@example.com",
                password_hash="$2b$12$" + "x" * 50,
                webhook_hash="short"
            )
    
    def test_valid_webhook_hash(self):
        """Test that valid webhook_hash is accepted."""
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$" + "x" * 50,
            webhook_hash="a1b2c3d4e5f6g7h8"
        )
        
        assert user.webhook_hash == "a1b2c3d4e5f6g7h8"
    
    def test_user_repr_excludes_sensitive_data(self):
        """Test that __repr__ doesn't expose password hash."""
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$secret_hash"
        )
        
        repr_str = repr(user)
        
        assert "test@example.com" in repr_str
        assert "secret_hash" not in repr_str
    
    def test_query_user_by_email(self, session: Session):
        """Test querying user by email."""
        user = UserModel(
            email="findme@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        
        # Query by email
        statement = select(UserModel).where(UserModel.email == "findme@example.com")
        found_user = session.exec(statement).first()
        
        assert found_user is not None
        assert found_user.email == "findme@example.com"
