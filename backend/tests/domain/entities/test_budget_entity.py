"""
Unit tests for Budget domain entity.
Tests pure business logic without database dependencies.
"""
import pytest
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal

from app.domain.entities.budget import Budget
from app.domain.value_objects.budget_category import BudgetCategory


class TestBudgetEntity:
    """Test Budget domain entity business logic."""
    
    def test_budget_creation(self):
        """Test basic budget creation."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        assert budget.monthly_income == Decimal('30000.00')
        assert budget.needs_allocated == Decimal('15000.00')
    
    def test_calculate_50_30_20(self):
        """Test 50/30/20 calculation from income."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        needs, wants, savings = budget.calculate_50_30_20()
        
        assert needs == Decimal('15000.00')  # 50%
        assert wants == Decimal('9000.00')   # 30%
        assert savings == Decimal('6000.00') # 20%
    
    def test_get_allocated_for_category(self):
        """Test getting allocated amount for specific category."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        assert budget.get_allocated_for_category(BudgetCategory.NEEDS) == Decimal('15000.00')
        assert budget.get_allocated_for_category(BudgetCategory.WANTS) == Decimal('9000.00')
        assert budget.get_allocated_for_category(BudgetCategory.SAVINGS) == Decimal('6000.00')
    
    def test_get_remaining_budget(self):
        """Test calculating remaining budget."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        # Spent 3000 from NEEDS budget
        remaining = budget.get_remaining_budget(
            BudgetCategory.NEEDS,
            Decimal('3000.00')
        )
        
        assert remaining == Decimal('12000.00')  # 15000 - 3000
    
    def test_get_safe_to_spend(self):
        """Test Safe-to-Spend calculation."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        # January 16: 16 days left (including today)
        # Spent: 3000
        # Remaining: 12000
        # Safe: 12000 / 16 = 750
        safe = budget.get_safe_to_spend(
            BudgetCategory.NEEDS,
            total_spent=Decimal('3000.00'),
            current_date=date(2026, 1, 16)
        )
        
        assert safe == Decimal('750.00')
    
    def test_safe_to_spend_when_overspent(self):
        """Test Safe-to-Spend returns 0 when overspent."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        # Overspent
        safe = budget.get_safe_to_spend(
            BudgetCategory.NEEDS,
            total_spent=Decimal('20000.00'),
            current_date=date(2026, 1, 16)
        )
        
        assert safe == Decimal('0.00')
    
    def test_safe_to_spend_when_period_ended(self):
        """Test Safe-to-Spend returns 0 when period ended."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        # After period ended
        safe = budget.get_safe_to_spend(
            BudgetCategory.NEEDS,
            total_spent=Decimal('3000.00'),
            current_date=date(2026, 2, 1)  # Next month
        )
        
        assert safe == Decimal('0.00')
    
    def test_is_overspent(self):
        """Test overspent detection."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        assert not budget.is_overspent(BudgetCategory.NEEDS, Decimal('3000.00'))
        assert budget.is_overspent(BudgetCategory.NEEDS, Decimal('20000.00'))
    
    def test_is_active(self):
        """Test period active check."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        assert budget.is_active(date(2026, 1, 15))  # During period
        assert not budget.is_active(date(2026, 2, 1))  # After period
        assert not budget.is_active(date(2025, 12, 31))  # Before period
    
    def test_get_progress_percentage(self):
        """Test spending progress calculation."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        # Spent 3000 of 15000 = 20%
        progress = budget.get_progress_percentage(
            BudgetCategory.NEEDS,
            Decimal('3000.00')
        )
        
        assert progress == Decimal('20.00')
    
    def test_get_days_in_period(self):
        """Test getting total days in period."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        assert budget.get_days_in_period() == 31
    
    def test_string_representation(self):
        """Test __str__ method."""
        budget = Budget(
            id=1,
            user_id=1,
            monthly_income=Decimal('30000.00'),
            period_start_date=date(2026, 1, 1),
            period_end_date=date(2026, 1, 31),
            needs_allocated=Decimal('15000.00'),
            wants_allocated=Decimal('9000.00'),
            savings_allocated=Decimal('6000.00'),
            created_at=datetime.now(timezone.utc)
        )
        
        result = str(budget)
        assert "2026-01" in result
        assert "30000" in result
