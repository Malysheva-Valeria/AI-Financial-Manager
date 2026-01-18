"""
Transaction Domain Entity.
Pure business logic, framework-independent.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.budget_category import BudgetCategory
from app.domain.value_objects.transaction_type import TransactionType
from app.domain.value_objects.transaction_source import TransactionSource


@dataclass
class Transaction:
    """
    Transaction domain entity representing financial transaction.
    
    This is separate from TransactionModel (ORM) following Clean Architecture.
    Contains only business rules, no database or framework dependencies.
    """
    id: Optional[int]
    user_id: int
    amount: Decimal
    currency: str
    description: str
    category: BudgetCategory
    transaction_type: TransactionType
    source: TransactionSource
    is_ai_categorized: bool = False
    mono_transaction_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
    
    def is_income(self) -> bool:
        """
        Business rule: Check if transaction is income.
        
        Returns:
            True if transaction type is INCOME
        """
        return self.transaction_type == TransactionType.INCOME
    
    def is_expense(self) -> bool:
        """
        Business rule: Check if transaction is expense.
        
        Returns:
            True if transaction type is EXPENSE
        """
        return self.transaction_type == TransactionType.EXPENSE
    
    def is_from_bank(self) -> bool:
        """
        Business rule: Check if transaction came from bank sync.
        
        Returns:
            True if source is MONOBANK
        """
        return self.source == TransactionSource.MONOBANK
    
    def is_manual(self) -> bool:
        """
        Business rule: Check if transaction was manually added.
        
        Returns:
            True if source is MANUAL
        """
        return self.source == TransactionSource.MANUAL
    
    def soft_delete(self) -> None:
        """
        Business logic: Soft delete transaction.
        
        Financial transactions should never be physically deleted
        to preserve audit trail and history.
        """
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """
        Business logic: Restore soft-deleted transaction.
        """
        self.deleted_at = None
    
    def is_deleted(self) -> bool:
        """
        Check if transaction has been soft-deleted.
        
        Returns:
            True if deleted_at is set
        """
        return self.deleted_at is not None
    
    def get_absolute_amount(self) -> Decimal:
        """
        Get absolute value of amount (always positive).
        
        Returns:
            Positive decimal representing transaction magnitude
        """
        return abs(self.amount)
    
    def categorize_with_ai(self, predicted_category: BudgetCategory) -> None:
        """
        Business logic: Apply AI-predicted category.
        
        Args:
            predicted_category: Category predicted by AI
        """
        self.category = predicted_category
        self.is_ai_categorized = True
    
    def manually_recategorize(self, new_category: BudgetCategory) -> None:
        """
        Business logic: User manually changes category.
        
        Args:
            new_category: User-selected category
        """
        self.category = new_category
        self.is_ai_categorized = False
    
    def __str__(self) -> str:
        """String representation."""
        sign = "+" if self.is_income() else "-"
        return f"Transaction({sign}{self.get_absolute_amount()} {self.currency}: {self.description})"
