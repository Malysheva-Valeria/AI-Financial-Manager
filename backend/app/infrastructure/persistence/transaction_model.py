"""
SQLModel Transaction - ORM model for database.
Separate from domain entity (Dependency Inversion Principle).
"""
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import Numeric, String, Enum as SQLEnum, DateTime, ForeignKey, CheckConstraint
from pydantic import field_validator
import enum

if TYPE_CHECKING:
    from app.infrastructure.persistence.user_model import UserModel


class TransactionTypeEnum(str, enum.Enum):
    """Transaction type: Income or Expense."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionSourceEnum(str, enum.Enum):
    """Transaction source: Manual or Monobank."""
    MANUAL = "MANUAL"
    MONOBANK = "MONOBANK"


class BudgetCategoryEnum(str, enum.Enum):
    """Budget category: 50/30/20 rule."""
    NEEDS = "NEEDS"
    WANTS = "WANTS"
    SAVINGS = "SAVINGS"


class TransactionModel(SQLModel, table=True):
    """
    Transaction database model with Pydantic validation.
    
    Represents financial transactions (income/expense) for users.
    Supports manual entry and Monobank API sync.
    """
    __tablename__ = "transactions"
    
    # Add constraint at table level
    __table_args__ = (
        CheckConstraint('amount != 0', name='check_amount_not_zero'),
    )

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key to User
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="User who owns this transaction"
    )

    # Transaction Details
    amount: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=2), nullable=False),
        description="Amount (positive for income, negative for expense)"
    )
    
    currency: str = Field(
        default="UAH",
        sa_column=Column(String(3), nullable=False),
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)"
    )
    
    description: str = Field(
        sa_column=Column(String(255), nullable=False),
        min_length=1,
        max_length=255,
        description="Transaction description"
    )

    # Categorization
    category: BudgetCategoryEnum = Field(
        sa_column=Column(SQLEnum(BudgetCategoryEnum), nullable=False),
        description="Budget category (NEEDS/WANTS/SAVINGS)"
    )
    
    transaction_type: TransactionTypeEnum = Field(
        sa_column=Column(SQLEnum(TransactionTypeEnum), nullable=False),
        description="Income or Expense"
    )
    
    source: TransactionSourceEnum = Field(
        default=TransactionSourceEnum.MANUAL,
        sa_column=Column(
            SQLEnum(TransactionSourceEnum),
            nullable=False,
            server_default=TransactionSourceEnum.MANUAL.value
        ),
        description="Manual or Monobank"
    )
    
    is_ai_categorized: bool = Field(
        default=False,
        description="Whether category was predicted by AI"
    )

    # Monobank Integration
    mono_transaction_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), unique=True, nullable=True),
        max_length=100,
        description="Monobank transaction ID for deduplication"
    )

    # Timestamps (timezone-aware)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
        description="Transaction date"
    )

    # Soft Delete
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Soft delete timestamp"
    )

    # Relationship
    user: Optional["UserModel"] = Relationship(back_populates="transactions")

    # Pydantic Validators
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount is not zero."""
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Description cannot be empty")
        return v.strip()

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Normalize currency to uppercase."""
        if not v:
            raise ValueError("Currency cannot be empty")
        return v.upper().strip()

    @field_validator('created_at', mode='before')
    @classmethod
    def validate_not_future(cls, v: datetime) -> datetime:
        """Validate transaction date is not in the future."""
        if isinstance(v, datetime) and v > datetime.now(timezone.utc):
            raise ValueError("Transaction date cannot be in the future")
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "amount": "-150.50",
                "currency": "UAH",
                "description": "Groceries at ATB",
                "category": "NEEDS",
                "transaction_type": "EXPENSE",
                "source": "MANUAL",
                "is_ai_categorized": False
            }
        }

    def __repr__(self) -> str:
        """String representation."""
        sign = "+" if self.amount > 0 else ""
        return f"TransactionModel(id={self.id}, amount={sign}{self.amount} {self.currency}, {self.description[:30]})"
