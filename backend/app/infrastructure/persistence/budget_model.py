"""
SQLModel Budget - ORM model for database.
Separate from domain entity (Dependency Inversion Principle).
"""
from decimal import Decimal
from datetime import datetime, timezone, date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import Numeric, Date, DateTime, ForeignKey, UniqueConstraint
from pydantic import field_validator, model_validator

if TYPE_CHECKING:
    from app.infrastructure.persistence.user_model import UserModel


class BudgetModel(SQLModel, table=True):
    """
    Budget database model with Pydantic validation.
    
    Represents monthly budgets with 50/30/20 rule.
    One budget per month per user (enforced by unique constraint).
    """
    __tablename__ = "budgets"
    
    # Unique constraint: one budget per month per user
    __table_args__ = (
        UniqueConstraint('user_id', 'period_start_date', name='uq_user_period'),
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
        description="User who owns this budget"
    )

    # Income (base for calculations)
    monthly_income: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=2), nullable=False),
        description="Monthly income amount (base for 50/30/20 calculation)"
    )

    # Allocated amounts (50/30/20 rule)
    needs_allocated: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=2), nullable=False),
        description="50% allocated to NEEDS (essentials)"
    )
    wants_allocated: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=2), nullable=False),
        description="30% allocated to WANTS (non-essentials)"
    )
    savings_allocated: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=2), nullable=False),
        description="20% allocated to SAVINGS (future)"
    )

    # Period tracking (monthly budgets)
    period_start_date: date = Field(
        sa_column=Column(Date, nullable=False, index=True),
        description="Budget period start (first day of month)"
    )
    period_end_date: date = Field(
        sa_column=Column(Date, nullable=False),
        description="Budget period end (last day of month)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Budget creation timestamp"
    )

    # Relationship
    user: Optional["UserModel"] = Relationship(back_populates="budgets")

    # Pydantic Validators
    @field_validator('monthly_income')
    @classmethod
    def validate_income(cls, v: Decimal) -> Decimal:
        """Validate income is positive."""
        if v <= 0:
            raise ValueError("Monthly income must be positive")
        return v

    @field_validator('needs_allocated', 'wants_allocated', 'savings_allocated')
    @classmethod
    def validate_allocated_amounts(cls, v: Decimal) -> Decimal:
        """Validate allocated amounts are non-negative."""
        if v < 0:
            raise ValueError("Allocated amount cannot be negative")
        return v

    @model_validator(mode='after')
    def validate_period_order(self):
        """Validate period_end_date is after period_start_date."""
        if self.period_end_date <= self.period_start_date:
            raise ValueError("Period end must be after period start")
        return self

    @model_validator(mode='after')
    def validate_50_30_20_sum(self):
        """
        Validate that allocated amounts sum to monthly income.
        
        Allows small rounding differences (up to 1 UAH).
        """
        total_allocated = (
            self.needs_allocated + 
            self.wants_allocated + 
            self.savings_allocated
        )
        
        # Allow 1 UAH difference for rounding
        difference = abs(total_allocated - self.monthly_income)
        if difference > Decimal('1.00'):
            raise ValueError(
                f"Allocated amounts must sum to monthly income. "
                f"Expected: {self.monthly_income}, Got: {total_allocated}"
            )
        
        return self

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "monthly_income": "30000.00",
                "needs_allocated": "15000.00",
                "wants_allocated": "9000.00",
                "savings_allocated": "6000.00",
                "period_start_date": "2026-01-01",
                "period_end_date": "2026-01-31"
            }
        }

    def __repr__(self) -> str:
        """String representation."""
        period = f"{self.period_start_date.strftime('%Y-%m')}"
        return f"BudgetModel(id={self.id}, income={self.monthly_income}, period={period})"
