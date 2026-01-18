"""
Budget Domain Entity.
Pure business logic for monthly budgets with 50/30/20 rule.
"""
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.budget_category import BudgetCategory


@dataclass
class Budget:
    """
    Budget domain entity representing monthly financial plan.
    
    Implements 50/30/20 budgeting rule:
    - 50% NEEDS (essentials)
    - 30% WANTS (non-essentials)  
    - 20% SAVINGS (future)
    
    This is separate from BudgetModel (ORM) following Clean Architecture.
    Contains only business rules, no database dependencies.
    """
    id: Optional[int]
    user_id: int
    monthly_income: Decimal
    period_start_date: date
    period_end_date: date
    needs_allocated: Decimal
    wants_allocated: Decimal
    savings_allocated: Decimal
    created_at: datetime
    
    def calculate_50_30_20(self) -> tuple[Decimal, Decimal, Decimal]:
        """
        Business rule: Calculate 50/30/20 allocation from monthly income.
        
        Returns:
            Tuple of (needs, wants, savings) amounts
            
        Example:
            >>> budget = Budget(monthly_income=Decimal('30000'), ...)
            >>> budget.calculate_50_30_20()
            (Decimal('15000.00'), Decimal('9000.00'), Decimal('6000.00'))
        """
        needs = (self.monthly_income * Decimal('0.50')).quantize(Decimal('0.01'))
        wants = (self.monthly_income * Decimal('0.30')).quantize(Decimal('0.01'))
        savings = (self.monthly_income * Decimal('0.20')).quantize(Decimal('0.01'))
        return (needs, wants, savings)
    
    def get_allocated_for_category(self, category: BudgetCategory) -> Decimal:
        """
        Get allocated amount for specific category.
        
        Args:
            category: Budget category
            
        Returns:
            Allocated amount for category
        """
        allocation_map = {
            BudgetCategory.NEEDS: self.needs_allocated,
            BudgetCategory.WANTS: self.wants_allocated,
            BudgetCategory.SAVINGS: self.savings_allocated
        }
        return allocation_map[category]
    
    def get_remaining_budget(
        self, 
        category: BudgetCategory,
        total_spent: Decimal
    ) -> Decimal:
        """
        Calculate remaining budget for category.
        
        Args:
            category: Budget category
            total_spent: Amount already spent in this category
            
        Returns:
            Remaining budget (can be negative if overspent)
            
        Example:
            Budget NEEDS: 15,000
            Spent: 3,000
            Remaining: 12,000
        """
        allocated = self.get_allocated_for_category(category)
        remaining = allocated - total_spent
        return remaining.quantize(Decimal('0.01'))
    
    def get_safe_to_spend(
        self,
        category: BudgetCategory,
        total_spent: Decimal,
        current_date: Optional[date] = None
    ) -> Decimal:
        """
        Business logic: Calculate safe daily spending amount.
        
        This is the "Safe-to-Spend" feature - shows how much user
        can safely spend per day for the rest of the period.
        
        Formula: Remaining Budget / Days Left in Period
        
        Args:
            category: Budget category
            total_spent: Amount spent so far in category
            current_date: Reference date (defaults to today)
            
        Returns:
            Safe daily spending amount (0 if negative or period ended)
            
        Example:
            Allocated: 15,000
            Spent: 3,000
            Remaining: 12,000
            Days left: 15
            Safe: 12,000 / 15 = 800 UAH/day
        """
        if current_date is None:
            current_date = date.today()
        
        # If period ended, no more spending allowed
        if current_date > self.period_end_date:
            return Decimal('0.00')
        
        # Calculate remaining budget
        remaining = self.get_remaining_budget(category, total_spent)
        
        # If overspent or no budget left, return 0
        if remaining <= 0:
            return Decimal('0.00')
        
        # Calculate days left (including today)
        from app.domain.services.budget_helpers import get_days_left_in_period
        days_left = get_days_left_in_period(self.period_end_date, current_date)
        
        # Avoid division by zero
        if days_left <= 0:
            return Decimal('0.00')
        
        # Safe daily amount
        safe_daily = (remaining / days_left).quantize(Decimal('0.01'))
        return safe_daily
    
    def is_overspent(self, category: BudgetCategory, total_spent: Decimal) -> bool:
        """
        Business rule: Check if category is overspent.
        
        Args:
            category: Budget category
            total_spent: Amount spent in category
            
        Returns:
            True if spent more than allocated
        """
        return self.get_remaining_budget(category, total_spent) < 0
    
    def is_active(self, current_date: Optional[date] = None) -> bool:
        """
        Check if budget period is currently active.
        
        Args:
            current_date: Reference date (defaults to today)
            
        Returns:
            True if current date is within budget period
        """
        if current_date is None:
            current_date = date.today()
        return self.period_start_date <= current_date <= self.period_end_date
    
    def get_progress_percentage(
        self,
        category: BudgetCategory,
        total_spent: Decimal
    ) -> Decimal:
        """
        Calculate spending progress as percentage.
        
        Args:
            category: Budget category
            total_spent: Amount spent in category
            
        Returns:
            Percentage spent (0-100+, can exceed 100 if overspent)
            
        Example:
            Allocated: 15,000
            Spent: 3,000
            Progress: 20%
        """
        allocated = self.get_allocated_for_category(category)
        
        if allocated == 0:
            return Decimal('0.00')
        
        percentage = (total_spent / allocated * 100).quantize(Decimal('0.01'))
        return percentage
    
    def get_days_in_period(self) -> int:
        """
        Get total number of days in budget period.
        
        Returns:
            Number of days in period
        """
        return (self.period_end_date - self.period_start_date).days + 1
    
    def __str__(self) -> str:
        """String representation."""
        period = f"{self.period_start_date.strftime('%Y-%m')}"
        return f"Budget({period}, income={self.monthly_income} UAH)"
