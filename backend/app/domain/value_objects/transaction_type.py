"""
Transaction Type Value Object.
Defines whether transaction is income or expense.
"""
from enum import Enum


class TransactionType(str, Enum):
    """
    Transaction type: Income or Expense.
    
    Attributes:
        INCOME: Money received (salary, refund, etc.)
        EXPENSE: Money spent (groceries, bills, etc.)
    """
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    
    def is_income(self) -> bool:
        """Check if this is an income type."""
        return self == TransactionType.INCOME
    
    def is_expense(self) -> bool:
        """Check if this is an expense type."""
        return self == TransactionType.EXPENSE
