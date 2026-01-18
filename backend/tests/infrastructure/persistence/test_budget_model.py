"""
Integration tests for BudgetModel ORM.
Tests database operations, validators, and relationships.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone, date
from sqlmodel import Session, select
from pydantic import ValidationError

from app.infrastructure.persistence.budget_model import BudgetModel
from app.infrastructure.persistence.user_model import UserModel


class TestBudgetModel:
    """Test BudgetModel database operations and validation."""
    
    def test_create_budget_in_database(self, session: Session):
        """Test creating a budget and persisting to database."""
        # First create a user
        user = UserModel(
            email="budget@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create budget
        budget = BudgetModel(
            user_id=user.id,
            monthly_income=Decimal('30000.00'),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31)
        )
        
        session.add(budget)
        session.commit()
        session.refresh(budget)
        
        assert budget.id is not None
        assert budget.user_id == user.id
        assert budget.monthly_income == Decimal('30000.00')
    
    def test_negative_income_raises_validation_error(self):
        """Test that income must be positive."""
        with pytest.raises(ValidationError, match="Monthly income must be positive"):
            BudgetModel(
                user_id=1,
                monthly_income=Decimal('-1000.00'),
                needs_allocated=Decimal('15000.00'),
                wants_allocated=Decimal('9000.00'),
                savings_allocated=Decimal('6000.00'),
                period_start_date=date(2026, 1, 1),
                period_end_date=date(2026, 1, 31)
            )
    
    def test_zero_income_raises_validation_error(self):
        """Test that income cannot be zero."""
        with pytest.raises(ValidationError, match="Monthly income must be positive"):
            BudgetModel(
                user_id=1,
                monthly_income=Decimal('0.00'),
                needs_allocated=Decimal('0.00'),
                wants_allocated=Decimal('0.00'),
                savings_allocated=Decimal('0.00'),
                period_start_date=date(2026, 1, 1),
                period_end_date=date(2026, 1, 31)
            )
    
    def test_period_end_before_start_raises_error(self):
        """Test that period_end_date must be after period_start_date."""
        with pytest.raises(ValidationError, match="Period end must be after period start"):
            BudgetModel(
                user_id=1,
                monthly_income=Decimal('30000.00'),
                needs_allocated=Decimal('15000.00'),
                wants_allocated=Decimal('9000.00'),
                savings_allocated=Decimal('6000.00'),
                period_start_date=date(2026, 1, 31),
                period_end_date=date(2026, 1, 1)  # Before start!
            )
    
    def test_allocated_sum_validation(self):
        """Test that allocated amounts must sum to income."""
        with pytest.raises(ValidationError, match="must sum to monthly income"):
            BudgetModel(
                user_id=1,
                monthly_income=Decimal('30000.00'),
                needs_allocated=Decimal('10000.00'),  # Sum = 25000
                wants_allocated=Decimal('10000.00'),
                savings_allocated=Decimal('5000.00'),  # Not 30000!
                period_start_date=date(2026, 1, 1),
                period_end_date=date(2026, 1, 31)
            )
    
    def test_unique_constraint_user_period(self, session: Session):
        """Test unique constraint on (user_id, period_start_date)."""
        user = UserModel(
            email="unique@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # First budget
        budget1 = BudgetModel(
            user_id=user.id,
            monthly_income=Decimal('30000.00'),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31)
        )
        session.add(budget1)
        session.commit()
        
        # Try to create another for same period
        budget2 = BudgetModel(
            user_id=user.id,
            monthly_income=Decimal('35000.00'),
            needs_allocated=Decimal('17500.00'),
            wants_allocated=Decimal('10500.00'),
            savings_allocated=Decimal('7000.00'),
            period_start_date=date(2026, 1, 1),  # Same period!
            period_end_date=date(2026, 1, 31)
        )
        session.add(budget2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
    
    def test_user_relationship(self, session: Session):
        """Test relationship between User and Budget."""
        user = UserModel(
            email="relation@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create budgets for different months
        b1 = BudgetModel(
            user_id=user.id,
            monthly_income=Decimal('30000.00'),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31)
        )
        b2 = BudgetModel(
            user_id=user.id,
            monthly_income=Decimal('32000.00'),
            needs_allocated=Decimal('16000.00'),
            wants_allocated=Decimal('9600.00'),
            savings_allocated=Decimal('6400.00'),
            period_start_date=date(2026, 2, 1),
            period_end_date=date(2026, 2, 28)
        )
        
        session.add_all([b1, b2])
        session.commit()
        
        # Refresh user to load budgets
        session.refresh(user)
        
        assert len(user.budgets) == 2
    
    def test_cascade_delete(self, session: Session):
        """Test that deleting user deletes budgets."""
        user = UserModel(
            email="cascade@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        budget = BudgetModel(
            user_id=user.id,
            monthly_income=Decimal('30000.00'),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31)
        )
        session.add(budget)
        session.commit()
        
        budget_id = budget.id
        
        # Delete user
        session.delete(user)
        session.commit()
        
        # Verify budget is also deleted
        statement = select(BudgetModel).where(BudgetModel.id == budget_id)
        result = session.exec(statement).first()
        
        assert result is None
    
    def test_50_30_20_calculation(self):
        """Test that 50/30/20 allocation is correct."""
        income = Decimal('30000.00')
        needs = (income * Decimal('0.50')).quantize(Decimal('0.01'))
        wants = (income * Decimal('0.30')).quantize(Decimal('0.01'))
        savings = (income * Decimal('0.20')).quantize(Decimal('0.01'))
        
        budget = BudgetModel(
            user_id=1,
            monthly_income=income,
            needs_allocated=needs,
            wants_allocated=wants,
            savings_allocated=savings,
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31)
        )
        
        assert budget.needs_allocated == Decimal('15000.00')
        assert budget.wants_allocated == Decimal('9000.00')
        assert budget.savings_allocated == Decimal('6000.00')
    
    def test_budget_repr(self):
        """Test __repr__ method."""
        budget = BudgetModel(
            user_id=1,
            monthly_income=Decimal('30000.00'),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31)
        )
        
        repr_str = repr(budget)
        
        assert "BudgetModel" in repr_str
        assert "30000" in repr_str
        assert "2026-01" in repr_str
