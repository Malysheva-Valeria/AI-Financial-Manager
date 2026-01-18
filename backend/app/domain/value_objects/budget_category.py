"""
Budget Category Value Object.
Based on 50/30/20 budgeting rule.
"""
from enum import Enum


class BudgetCategory(str, Enum):
    """
    Budget category following 50/30/20 rule.
    
    Attributes:
        NEEDS: Essential expenses (50% of income)
               Examples: rent, groceries, utilities, transportation
        
        WANTS: Non-essential expenses (30% of income)
               Examples: entertainment, dining out, hobbies, subscriptions
        
        SAVINGS: Savings and investments (20% of income)
                 Examples: emergency fund, retirement, investments
    """
    NEEDS = "NEEDS"
    WANTS = "WANTS"
    SAVINGS = "SAVINGS"
    
    def is_essential(self) -> bool:
        """Check if category is essential (NEEDS)."""
        return self == BudgetCategory.NEEDS
    
    def get_budget_percentage(self) -> int:
        """Get recommended budget percentage for this category."""
        percentages = {
            BudgetCategory.NEEDS: 50,
            BudgetCategory.WANTS: 30,
            BudgetCategory.SAVINGS: 20
        }
        return percentages[self]
