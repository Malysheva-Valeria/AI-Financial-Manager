"""
SQLModel User - ORM model for database.
Separate from domain entity (Dependency Inversion Principle).
"""
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, Enum as SQLEnum, DateTime
from pydantic import EmailStr, field_validator
import enum

if TYPE_CHECKING:
    from app.infrastructure.persistence.transaction_model import TransactionModel


class TrackingModeEnum(str, enum.Enum):
    """Tracking mode: Auto (Monobank) or Manual."""
    AUTO_MONO = "AUTO_MONO"
    MANUAL = "MANUAL"


class UserModel(SQLModel, table=True):
    """
    User database model with Pydantic validation.
    
    Fields match specification from project documentation.
    Includes validators for data integrity and security.
    """
    __tablename__ = "users"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Authentication
    email: EmailStr = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False),
        description="User email (login) - validated and normalized to lowercase"
    )
    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False),
        min_length=60,  # bcrypt hash length
        max_length=255,
        description="Bcrypt hashed password (minimum 60 chars for bcrypt)"
    )

    # Tracking Settings
    tracking_mode: TrackingModeEnum = Field(
        default=TrackingModeEnum.MANUAL,
        sa_column=Column(
            SQLEnum(TrackingModeEnum),
            nullable=False,
            server_default=TrackingModeEnum.MANUAL.value
        ),
        description="AUTO_MONO or MANUAL tracking"
    )

    # Monobank Integration (nullable - only for AUTO mode)
    mono_token: Optional[str] = Field(
        default=None,
        sa_column=Column(String(500), nullable=True),
        max_length=500,
        description="Encrypted Monobank access token (Fernet)"
    )
    mono_account_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
        max_length=100,
        description="Monobank account ID (white jar)"
    )
    webhook_hash: Optional[str] = Field(
        default=None,
        sa_column=Column(String(64), unique=True, index=True, nullable=True),
        max_length=64,
        description="Unique webhook URL path for Monobank callbacks"
    )

    # User Preferences
    cash_reminder_enabled: bool = Field(
        default=False,
        description="Enable daily cash reminder at 21:00"
    )

    # Subscription
    is_premium: bool = Field(
        default=False,
        description="Premium subscription status"
    )

    # Timestamps (using timezone-aware datetime)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Account creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Last update timestamp (UTC)"
    )

    # Relationships
    transactions: List["TransactionModel"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Pydantic Validators
    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        """Normalize email to lowercase and strip whitespace."""
        if not v:
            raise ValueError("Email cannot be empty")
        return v.lower().strip()
    
    @field_validator('password_hash')
    @classmethod
    def validate_password_hash(cls, v: str) -> str:
        """Validate password hash format (bcrypt starts with $2b$)."""
        if not v:
            raise ValueError("Password hash cannot be empty")
        if len(v) < 60:
            raise ValueError("Invalid password hash - bcrypt hashes are 60 chars minimum")
        return v
    
    @field_validator('mono_token')
    @classmethod
    def validate_mono_token(cls, v: Optional[str]) -> Optional[str]:
        """Validate Monobank token is not empty string."""
        if v is not None and v.strip() == "":
            raise ValueError("Monobank token cannot be empty string")
        return v
    
    @field_validator('webhook_hash')
    @classmethod
    def validate_webhook_hash(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook hash format (alphanumeric)."""
        if v is not None:
            if not v.isalnum():
                raise ValueError("Webhook hash must be alphanumeric")
            if len(v) < 16:
                raise ValueError("Webhook hash must be at least 16 characters")
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password_hash": "$2b$12$KIXxLV2hFZ8y9z3F4Q5h1.XYZabcdefghijklmnopqrstuvwxyz1234",
                "tracking_mode": "MANUAL",
                "cash_reminder_enabled": True,
                "is_premium": False
            }
        }
    
    def __repr__(self) -> str:
        """String representation (without sensitive data)."""
        return f"UserModel(id={self.id}, email={self.email}, tracking_mode={self.tracking_mode})"